# 🧾 Abusive Relationship Stories: Annotated Reddit Dataset

This repository contains a dataset of ~8000 Reddit posts related to potentially abusive romantic relationships. 
The posts were automatically annotated using a state-of-the-art Large Language Model (LLM), with guidance and partial review provided by domain experts in domestic abuse from the Michal Sela Forum.

To request access to the dataset, please fill out the following form:

👉 [Request Access Form](https://forms.gle/sU1tT9C6yEoGNVZ96)

Access is granted for academic and research purposes only. Approved applicants will receive a private download link.
---

## 🧠 Dataset Description

Each post in the dataset contains:

- **Post Metadata**: Extracted directly from Reddit.
- **Relationship & Demographic Metadata**: Automatically extracted using Google’s Gemini-pro LLM.
- **Contextual Risk Factors**: Annotated by the LLM based on known signs of abuse.

> ⚠️ LLM-based annotations may include errors and should be used as **guidance**, not ground truth.

---

## 📚 Source Subreddits

The dataset was curated from:
```
abusiverelationships, emotionalabuse, NarcissisticSpouses, NarcAbuseAndDivorce,
domesticviolence, abusesurvivors, relationship_advice, survivinginfidelity,
LifeAfterNarcissism, ToxicRelationships, relationships, Infidelity
```

---

## 🚫 Filtering Criteria

Posts were excluded if:
- The author was under 18.
- The post was not a personal story.
- The post was unrelated to romantic relationships.
- The post was too short or too long.

> ⚠️ Filtering was automated and may contain false positives.

---

## 📑 Feature Descriptions

Below is a summary of key features included in the dataset, categorized by their source and purpose:

### 🔹 Post Metadata
- **post_id**: A unique identifier assigned to each Reddit post, allowing reference and indexing.
- **title**: The headline or subject line of the Reddit post, often summarizing the content.
- **post_author**: The username of the individual who submitted the post.
- **body**: The main textual content of the post, describing the relationship or incident.
- **post_body**: A concatenation of the post title and body for holistic textual analysis.
- **date_time**: The exact timestamp when the post was published on Reddit.
- **url**: The direct web address linking to the Reddit post.
- **score**: The net number of upvotes the post received (upvotes minus downvotes).
- **num_comments**: Total number of comments on the post.
- **flairs**: Community-assigned tags or labels providing context or categorization.
- **subreddit**: The specific subreddit where the post was published.

### 🔹 Comment Metadata
- **highest_comment_id**: The ID of the comment with the highest score, indicating community endorsement.
- **highest_comment_body**: The full text of the most upvoted comment.
- **highest_comment_author**: Username of the author who wrote the highest scoring comment.
- **highest_comment_date_time**: Timestamp indicating when the top comment was posted.
- **highest_comment_score**: The net score of the highest scoring comment.
- **longest_comment_id**: ID of the comment with the greatest character length.
- **longest_comment_body**: The content of the longest comment, potentially containing detailed advice or responses.
- **longest_comment_author**: Username of the author who wrote the longest comment.
- **longest_comment_date_time**: Time and date when the longest comment was posted.
- **longest_comment_score**: Community score of the longest comment.

### 🔹 Relationship Metadata (LLM)
- **children**: Indicates whether the romantic relationship described involves shared children.
- **relationship_type**: Describes the nature of the relationship (e.g., dating, married, roommates).
- **was_breakup**: Flags whether a breakup event is mentioned in the post.
- **relationship_status**: Current status of the relationship at the time of writing (e.g., together, separated).
- **when_breakup**: Timeframe of the breakup relative to the post date, if applicable.
- **living_with**: Indicates whether the individuals in the relationship were cohabiting.

### 🔹 Demographic Metadata (LLM)
- **author_role**: Defines the relationship of the post author to the people involved in the abuse narrative.
- **age_female**: Estimated or mentioned age of the female individual in the scenario.
- **age_male**: Estimated or mentioned age of the male individual in the scenario.
- **author_gender**: Gender of the author as inferred or declared in the post.
- **age_victim**: Age of the victim involved in the described events.
- **age_offender**: Age of the alleged offender in the post.
- **gender_victim**: Gender of the victim (e.g., male, female, other).
- **gender_offender**: Gender of the alleged offender.


### 🧷 Contextual Risk Factors (LLM)

Each contextual risk factor was automatically annotated using a Large Language Model (LLM). These factors represent behavioral, emotional, and situational indicators commonly associated with abusive relationships. The possible annotation values are:

- **Yes** — Clear evidence in the text supports the presence of the risk factor.
- **No** — Clear evidence in the text indicates the absence of the risk factor.
- **Plausibly** — Some indirect or vague evidence suggests the presence of the risk factor, but it is not definitive.
- **Cannot Be Inferred** — The available text does not provide enough information to determine the presence or absence of the factor.

> 🛑 **Note**: These factors were formulated in collaboration with the Michal Sela Forum (MSF) and experts in domestic abuse, based on known risk factors. Additional risks may exist that are not captured in this dataset.

#### Risk Factors:
- **abusive_relationship**: Whether the relationship is abusive.
- **emotional_violence**: Emotional or psychological harm inflicted by the offender on the victim.
- **physical_violence**: Physical pain or harm inflicted by the offender on the victim.
- **sexual_violence**: Non-consensual sexual acts performed by the offender on the victim.
- **economic_violence**: Control exerted by the offender over the victim's financial resources.
- **spiritual_violence**: Control over the victim's spiritual practices (e.g., religious coercion).
- **past_offenses**: History of criminal or abusive behavior by the offender.
- **social_isolation**: Limiting the victim’s social interactions.
- **suicidal_threats**: Suicide threats by the offender, often manipulative.
- **mental_condition**: Diagnosed mental health conditions affecting the offender.
- **daily_activity_control**: Control over the victim’s daily routines or decisions.
- **violent_behavior**: General tendency to display violent behavior.
- **unemployment**: The offender is not employed.
- **substance_use**: Use or dependency on harmful substances.
- **obsessiveness**: Excessive focus or control over the victim's actions.
- **jealousy**: Jealous behavior leading to control or conflict.
- **outbursts**: Explosive anger or temper episodes.
- **ptsd**: The offender suffers from post-traumatic stress disorder.
- **hard_childhood**: Traumatic childhood experiences of the offender.
- **emotional_dependency**: Offender’s psychological dependence on the victim.
- **fear_based_relationship**: The victim feels fear within the relationship.
- **humiliation**: Demeaning or humiliating acts by the offender.
- **physical_threats**: Verbal or implied threats of physical harm.
- **presence_of_others_in_assault**: Others were present during acts of violence.
- **signs_of_injury**: Physical evidence of harm to the victim.
- **property_damage**: Damaging objects as intimidation or punishment.
- **access_to_weapons**: Offender has access to firearms or other weapons.
- **gaslighting**: Psychological manipulation causing the victim to doubt themselves.
- **victim_support_network**: Presence of a support system for the victim.
- **offender_support_network**: Presence of a support system for the offender.
- **attempts_to_end_relationship**: Victim attempted to leave the relationship.
- **refusal_to_end_relationship**: Offender resists the end of the relationship.
- **public_private_discrepancy**: Mismatch between public and private behavior of the offender.
- **narcissistic_traits**: Traits such as grandiosity, entitlement, lack of empathy.
- **aggressive_behavior**: General pattern of aggression beyond the intimate relationship.
---

## 🧑‍⚕️ Expert Annotation

A small subset of <20 posts was reviewed by trained domestic abuse professionals for annotation calibration and validation of the LLM outputs.

---

## 📘 Appendix: Acronyms & Terms

| Acronym | Meaning |
|--------|---------|
| AP | Affair partner |
| BS/BP | Betrayed spouse/partner |
| DV | Domestic violence |
| DARVO | Deny, Attack, Reverse Victim and Offender |
| EA/PA | Emotional/Physical affair |
| NC | No contact |
| NEX | Narcissistic ex |
| PTSD | Post-traumatic stress disorder |
| RIC | Reconciliation Industrial Complex |
| Trickle-truth | Gradual, partial confession following evidence |
| Hoovering | Attempt by abuser to re-engage the victim |
| Monkey branching | Lining up a new relationship while still in the old one |

