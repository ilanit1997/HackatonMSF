import re
import datetime
import pandas as pd
import os
import json
from langchain_google_vertexai import VertexAI
from vertexai import generative_models
from typing import Optional
import time
from pydantic import BaseModel, Field


def extract_between_brackets(text):
    pattern = r'\[(.*?)\]'
    matches = re.findall(pattern, text)
    return matches


def remove_text_between_brackets(text):
    pattern = r'\[.*?\]'
    result = re.sub(pattern, '', text)
    return result


def num_words(text):
    try:
        return len(text.split())
    except:
        return 0

def is_deleted_or_null(text):
    if text is None:
        return True
    if type(text) == float:
        return True
    if type(text) == str:
        return '[deleted]' in text
    return False
def convert_utc_to_datetime(utc_time):
    return datetime.datetime.utcfromtimestamp(utc_time).strftime('%d/%m/%y %H:%M:%S')


def remove_text_after_x(text, x):
    pattern = re.escape(x) + r'.*'
    result = re.sub(pattern, '', text, flags=re.IGNORECASE)
    return result


def extract_data_from_comment(comment, prefix=None):
    data = dict(comment_id=comment.id, comment_body=remove_text_after_x(comment.body, 'edit:'),
                comment_author=comment.author,
                comment_date_time=convert_utc_to_datetime(comment.created), comment_score=comment.score)
    if prefix is not None:
        data = {f"{prefix}_{k}": v for k, v in data.items()}
    return data


def extract_data_from_post(post):
    post_data = dict(post_id=post.id, title=remove_text_between_brackets(post.title),
                     post_author=post.author,
                     body=remove_text_after_x(post.selftext, 'edit:'), date_time=convert_utc_to_datetime(post.created),
                     url=post.url, score=post.score, num_comments=post.num_comments)
    post_data['flairs'] = str(extract_between_brackets(post.title))
    comments = [(comment, comment.score, num_words(comment.body)) for comment in post.comments]
    comments = [x for x in comments if x[2] > 30]
    highest_comment = sorted(comments, key=lambda c: c[1], reverse=True)[0][0]
    longest_comment = sorted(comments, key=lambda c: c[2], reverse=True)[0][0]
    post_data.update(extract_data_from_comment(highest_comment, 'highest'))
    post_data.update(extract_data_from_comment(longest_comment, 'longest'))
    return post_data

def load_data(root ="/data/home/ilanit.sobol/dv/data/outputs/reddit/subreddits"):
    all_files_csv = []
    for subdir, dirs, files in os.walk(root):
        for file in files:
            if file.endswith(".csv"):
                all_files_csv.append(os.path.join(subdir, file))
    dfs = []
    for file in all_files_csv:
        try:
            df = pd.read_csv(file)
            dfs.append(df)
        except Exception as e:
            pass
    df = pd.concat(dfs)
    print(f"loaded {len(df)} rows")
    return df


def filter_data(df):
    df = df.drop_duplicates('post_id')
    df = df[(df['longest_comment_body'] != '[deleted]') & (df['highest_comment_body'] != '[deleted]')]
    df = df[df["body"].isnull() == False]
    df['body'] = [remove_text_after_x(text, 'edit:') if type(text) == str else ""
                  for text in df['body'].values]
    df['longest_comment_body'] = [remove_text_after_x(text, 'edit:') if type(text) == str else "" for text in
                                  df['longest_comment_body'].values]
    df['highest_comment_body'] = [remove_text_after_x(text, 'edit:') if type(text) == str else "" for text in
                                  df['highest_comment_body'].values]
    df['post_body'] = df['title'] + '\n' + df['body']
    df["deleted"] = df["body"].apply(lambda x: is_deleted_or_null(x))
    df = df[df["deleted"] == False]
    df["post_num_words"] = df["post_body"].apply(lambda x: num_words(x))
    df_filtered = df[df["deleted"] == False]
    df_filtered = df_filtered[(df_filtered['post_num_words'] > 50) & (df_filtered['post_num_words'] < 1200)]
    print(f"filtered to {len(df_filtered)} rows")
    return df_filtered


def load_gemini_model(name="gemini-1.5-pro-preview-0409",
                      path_to_creds="/data/home/ilanit.sobol/code_files/configs/vertex-ai_creds.json",
                      max_output_tokens=3000,):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json.load(open(path_to_creds))["path"]
    # Safety config
    safety_config = {
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }
    model = VertexAI(model_name=name, max_output_tokens=max_output_tokens, safety_settings=safety_config,
                     temperature=0, region="us-central1")
    return model

def process_chain(row, existing_results, chain, results, max_retries=3):
    """
    Processes a data chain for a given row and appends the output to results if successful.

    Args:
        row (dict): Data row containing post details.
        existing_results (list): Set of indices that have already been processed.
        chain (callable): Chain function to be invoked with the story.
        results (list): List to append the results to.
        max_retries (int): Maximum number of retry attempts.

    Returns:
        list: Updated list of results.
    """

    story = row["post_body"]
    post_id = row["post_id"]
    attempts = 0

    while attempts < max_retries:
        try:
            output = chain.invoke({"story": story})
            output_json = json.loads(output.json())
            results.append({
                "story": story,
                "post_id": post_id,
                "output_json": output_json
            })
            return results
        except Exception as e:
            time.sleep(3)
            attempts += 1
            if attempts == max_retries:
                return results  # Return the results even if all retries fail
    return results

class Labels(BaseModel):
    is_romantic: str = Field(
        enum=["yes", "no", "cannot be inferred"],
        description="Indicates whether the relationship is romantic."
    )
    abusive_relationship: str = Field(
        description="Indicates whether the relationship is abusive.",
        enum=["yes", "no", "cannot be inferred", "irrelevant"]
    )
    relationship_status: str = Field(
        enum=["together", "separated", "process of separation", "cannot be inferred", "irrelevant"],
        description="Indicates the status of the romantic relationship."
    )
    children: str = Field(
        description="Indicates whether the romantic relationship involves children shared by the couple.",
        enum=["yes", "no", "cannot be inferred", "irrelevant"]
    )
    relationship_type: str = Field(
        description="Indicates the nature of the relationship between the individuals mentioned in the post.",
        enum=["dating", "relationship", "engaged", "married", "friends", "family", "roommates", "classmates", "co-workers", "other"]
    )
    was_breakup: str = Field(
        description="Indicates whether a breakup is mentioned.",
        enum=["yes", "no"]
    )
    when_breakup: str = Field(
        description="If breakup is mentioned then - when was the breakup (relative to post's date)?",
        enum=["irrelevant", "week", "month", "6 months", "a year", "3 years", "5 years", "more than 5 years", "cannot be inferred"]
    )
    story_type: str = Field(
        description="Indicates the nature and intent of the post, providing insight into the type of content and its primary purpose.",
         enum=[ "sharing a personal story",  "practical advice (without a personal story)", "advice request (without a personal story)",  "venting (without a personal story)", "other"  ]
    )
    author_role: str = Field(
        description="Indicates the relationship of the author to the individual involved in the narrative of abuse.",
        enum=["victim",  "relative of the victim", "acquaintance of the victim", "offender", "relative of the offender", "acquaintance of the offender", "other", "irrelevant"]
    )
    living_with: str = Field(
        description="Indicates whether the individuals involved in the relationship are currently living together. If no information about living situation, then answer with cannot be inferred",
        enum=["yes", "no", "cannot be inferred"]
    )
    age_female: Optional[int] = Field(
        default=None,
        description="Specifies the age of the female involved in the scenario described in the post. "
    )
    age_male: Optional[int] = Field(
        default=None,
        description="Specifies the age of the male involved in the scenario described in the post, if applicable"
    )
    author_gender: str = Field(
        description="Denotes the gender of the post's author.",
        enum=["female", "male", "other"]
    )



enums_answers_text = [
    "yes",
    "no",
    "plausibly",
    "cannot be inferred"
]
class RiskFactors(BaseModel):
    age_victim: Optional[int] = Field(
        default=None
    )
    age_offender: Optional[int] = Field(
        default=None
    )
    gender_victim: str = Field(
        enum=["male", "female", "other", "cannot be inferred"],
    )
    gender_offender: str = Field(
        enum=["male", "female", "other", "cannot be inferred"],
    )
    emotional_violence: str = Field(
        enum=enums_answers_text,
        description="Emotional or psychological harm inflicted by the offender on the victim"
    )
    physical_violence: str = Field(
        enum=enums_answers_text,
        description="Physical pain or harm inflicted by the offender on the victim"
    )
    sexual_violence: str = Field(
        enum=enums_answers_text,
        description="Non-consensual sexual acts performed by the offender on the victim"
    )
    economic_violence: str = Field(
        enum=enums_answers_text,
        description="Control exerted by the offender over the victim's financial resources"
    )
    spiritual_violence: str = Field(
        enum=enums_answers_text,
        description="Control exerted by the offender over the victim's spiritual practices, such as preventing "
                    "religious ceremonies or enforcing religious practices against the victim's will."
    )
    past_offenses: str = Field(
        enum=enums_answers_text,
        description="Any historical criminal or abusive behavior by the offender"
    )
    social_isolation: str = Field(
        enum=enums_answers_text,
        description="Restriction of the victim’s social contacts and interactions by the offender"
    )
    suicidal_threats: str = Field(
        enum=enums_answers_text,
        description="Threats of suicide made by the offender, often as a manipulative tactic"
    )
    mental_condition: str = Field(
        enum=enums_answers_text,
        description="Presence of diagnosed mental health conditions affecting the offender, including personal crisis"
    )
    daily_activity_control: str = Field(
        enum=enums_answers_text,
        description="Control over the victim’s daily life and decisions by the offender"
    )
    violent_behavior: str = Field(
        enum=enums_answers_text,
        description="Does the offender exhibit violent behavior towards others?"
    )
    unemployment: str = Field(
        enum=enums_answers_text,
        description="The offender is unemployed"
    )
    substance_use: str = Field(
        enum=enums_answers_text,
        description="Dependency on drugs, alcohol, or other harmful substances by the offender."
    )
    obsessiveness: str = Field(
        enum=enums_answers_text,
        description="The offender’s excessive fixation on the victim, often controlling or overbearing, a need to "
                    "monitor the victim in everyday activities"
    )
    jealousy: str = Field(
        enum=enums_answers_text,
        description="Displays of jealousy by the offender, potentially leading to controlling behavior."
    )
    outbursts: str = Field(
        enum=enums_answers_text,
        description="Sudden and intense episodes of anger exhibited by the offender."
    )
    ptsd: str = Field(
        enum=enums_answers_text,
        description="The offender suffers from post-traumatic stress disorder"
    )
    hard_childhood: str = Field(
        enum=enums_answers_text,
        description="The offender suffers from a traumatic childhood experience"
    )
    emotional_dependency: str = Field(
        enum=enums_answers_text,
        description="The offender’s emotional or psychological dependence on the victim."
    )
    fear_based_relationship: str = Field(
        enum=enums_answers_text,
        description="The victim experiences fear within the relationship."
    )
    humiliation: str = Field(
        enum=enums_answers_text,
        description="Actions by the offender that humiliate or demean the victim"
    )
    physical_threats: str = Field(
        enum=enums_answers_text,
        description="Threats of physical violence made by the offender towards the victim"
    )
    presence_of_others_in_assault: str = Field(
        enum=enums_answers_text,
        description="Presence of others during acts of assault or violence initiated by the offender."
    )
    signs_of_injury: str = Field(
        enum=enums_answers_text,
        description="Physical signs of injury on the victim indicating abuse."
    )
    property_damage: str = Field(
        enum=enums_answers_text,
        description="Damage to property by the offender as a form of intimidation or aggression"
    )
    access_to_weapons: str = Field(
        enum=enums_answers_text,
        description="The offender’s access to weapons, posing a potential risk of violent behavior."
    )
    gaslighting: str = Field(
        enum=enums_answers_text,
        description="The offender, portraying themselves as a victim or a martyr, "
                    "manipulates the victim into doubting their own perception and feeling guilty, "
                    "a tactic known as gaslighting."
    )
    victim_support_network: str = Field(
        enum=enums_answers_text,
        description="Availability of a social support network (such as family or friends) for the victim"
    )
    offender_support_network: str = Field(
        enum=enums_answers_text,
        description="Availability of a social support network (such as family or friends) for the offender"
    )
    attempts_to_end_relationship: str = Field(
        enum=enums_answers_text,
        description="Attempts by the victim to end the relationship"
    )
    refusal_to_end_relationship: str = Field(
        enum=enums_answers_text,
        description="Refusal by the offender to accept the end of the relationship"
    )
    public_private_discrepancy: str = Field(
        enum=enums_answers_text,
        description="Discrepancy between the offender’s public persona and private behavior"
    )
    narcissistic_traits: str = Field(
        enum=enums_answers_text,
        description="Exhibitions of narcissism by the offender, including grandiosity and lack of empathy"
    )
    aggressive_behavior: str = Field(
        enum=enums_answers_text,
        description="The offender's tendency to behave violently or aggressively."
    )
