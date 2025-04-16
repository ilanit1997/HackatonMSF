from tqdm import tqdm
from annotate_utils import *
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import pickle
import wandb

wandb.init(project="michal-sela", name="annotate reddit posts risk")
wandb.save('annotate_utils.py')

#### Load the data and model
model = load_gemini_model()
df_filtered = pd.read_csv("/data/home/ilanit.sobol/dv/data/outputs/reddit/labeled/iter2/results_posts_metadata_filtered.csv")

#### Define the model chain
prompt_template_str_risk = """
Evaluate the potential for danger in a relationship as described in a Reddit post by assessing the presence of various risk factors. 
Provide responses of 'yes', 'no', 'plausibly', 'cannot be inferred' for each risk factor, based only on details written in the story. 

Use the following guidelines:

Yes - Clear evidence in the text supports the presence of the risk factor.
No - Clear evidence in the text indicates the absence of the risk factor.
Plausibly - There is some indirect or vague evidence suggesting the presence of the risk factor, but it is not definitive.
Cannot Be Inferred - There is insufficient information in the text to make a determination about the presence or absence of the risk factor.

Story: {story}

Format:
{format_instructions}
"""
wandb.config.update({"prompt_template_str_risk": prompt_template_str_risk})

parser_risk = PydanticOutputParser(pydantic_object=RiskFactors)
format_instructions_risk = parser_risk.get_format_instructions()
prompt_risk = PromptTemplate(
    template=prompt_template_str_risk,
    input_variables=["story"],
    partial_variables={"format_instructions": format_instructions_risk}
)
chain_risk = prompt_risk | model | parser_risk
#### Load existing results
output_folder = "/data/home/ilanit.sobol/dv/data/outputs/reddit/labeled/iter2"

output_file_labels = os.path.join(output_folder, "results_posts_risks.pkl")
if os.path.exists(output_file_labels):
    results_risks = pickle.load(open(output_file_labels, "rb"))
else:
    results_risks = []

existing_results_risks = [res["post_id"] for res in results_risks]
print(len(existing_results_risks))
df_filtered_current = df_filtered[~df_filtered["post_id"].isin(existing_results_risks)]
#### Run the model
for i, row in tqdm(df_filtered_current.iterrows(), total=df_filtered_current.shape[0]):
    wandb.log({"i": i})
    if row["post_id"] in existing_results_risks:
        continue
    results_risks = process_chain(row, existing_results_risks, chain_risk, results_risks)
    if len(results_risks) % 5 == 0:
        with open(output_file_labels, "wb") as f:
            pickle.dump(results_risks, f)


#### Join the results with the original data
df_filtered = df_filtered.set_index("post_id")
results_df_risks = pd.DataFrame(results_risks)
results_df_risks = results_df_risks[results_df_risks["output_json"] != None]
expanded_json_df_risks = pd.json_normalize(results_df_risks['output_json'])
expanded_json_df_risks["post_id"] = results_df_risks["post_id"]
expanded_json_df_risks = expanded_json_df_risks.set_index("post_id")
results_df_risks = results_df_risks.set_index("post_id")
results_df_joined_risks = results_df_risks.join(expanded_json_df_risks, how='inner')
results_df_joined_risks = results_df_joined_risks.drop(["story", "output_json"], axis=1)
final_df_joined_all = df_filtered.merge(results_df_joined_risks, left_on = "post_id", right_on="post_id", how='inner')
print(f"final_df_joined_all shape: {final_df_joined_all.shape}")

#### Save the results
final_df_joined_all.to_csv(os.path.join(output_folder, "results_posts_metadata_risks.csv"), index=False)
wandb.finish()
