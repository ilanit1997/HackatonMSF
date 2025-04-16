import pandas as pd
from tqdm import tqdm
from annotate_utils import *
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import pickle
import wandb

wandb.init(project="michal-sela", name="annotate reddit posts metadata - missing from risks")
wandb.save('annotate_utils.py')

#### Load the data and model
model = load_gemini_model()
df_filtered = pd.read_csv("/data/home/ilanit.sobol/dv/data/outputs/reddit/labeled/iter2/results_posts_risks_joined_all.csv")

#### Define the model chain
prompt_template_str_labels = """
Analyze a reddit post and extract information about the relationship.

Story: {story}

{format_instructions}
"""
wandb.config.update({"prompt_template_str_labels": prompt_template_str_labels})

parser_labels = PydanticOutputParser(pydantic_object=Labels)
format_instructions_labels = parser_labels.get_format_instructions()
wandb.config.update({"format_instructions_labels": format_instructions_labels})

prompt_labels = PromptTemplate(
    template=prompt_template_str_labels,
    input_variables=["story"],
    partial_variables={"format_instructions": format_instructions_labels}
)
chain_labels = prompt_labels | model | parser_labels
#### Load existing results
output_folder = "/data/home/ilanit.sobol/dv/data/outputs/reddit/labeled/iter2"

output_file_labels = os.path.join(output_folder, "results_posts_labels.pkl")
if os.path.exists(output_file_labels):
    results_labels = pickle.load(open(output_file_labels, "rb"))
else:
    results_labels = []

existing_results_labels = [res["post_id"] for res in results_labels]
print(len(existing_results_labels))
df_filtered_current = df_filtered[~df_filtered["post_id"].isin(existing_results_labels)]
#### Run the model
for i, row in tqdm(df_filtered_current.iterrows(), total=df_filtered_current.shape[0]):
    wandb.log({"i": i})
    if row["post_id"] in existing_results_labels:
        continue
    results_labels = process_chain(row, existing_results_labels, chain_labels, results_labels)
    if len(results_labels) % 5 == 0:
        with open(output_file_labels, "wb") as f:
            pickle.dump(results_labels, f)

#### Join the results with the original data
df_filtered = df_filtered.set_index("post_id")
results_df_labels = pd.DataFrame(results_labels)
results_df_labels = results_df_labels[results_df_labels["output_json"] != None]
expanded_json_df_labels = pd.json_normalize(results_df_labels['output_json'])
expanded_json_df_labels["post_id"] = results_df_labels["post_id"]
expanded_json_df_labels = expanded_json_df_labels.set_index("post_id")
results_df_labels = results_df_labels.set_index("post_id")
results_df_joined_labels = results_df_labels.join(expanded_json_df_labels, how='inner')
results_df_joined_labels = results_df_joined_labels.drop(["story", "output_json"], axis=1)
final_df_joined_all = df_filtered.merge(results_df_joined_labels, left_on = "post_id", right_on="post_id", how='inner')
print(f"final_df_joined_all shape: {final_df_joined_all.shape}")

#### Save the results
final_df_joined_all.to_csv(os.path.join(output_folder, "reddit_posts_filtered_metadata.csv"), index=False)
wandb.finish()
