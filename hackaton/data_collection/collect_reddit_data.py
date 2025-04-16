import time
from reddit_utils import *

CLIENT_ID = 'xx'
CLIENT_SECRET = 'yy'
USER_AGENT = 'my_user_agent'  # just give it a name
reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT)

##################### Load existing data #####################
exisiting_data = []
for i in range(1, 3):
    root = f"/data/home/ilanit.sobol/dv/data/outputs/reddit/subreddits/new/iter{i}"
    for file in os.listdir(root):
        if file.endswith(".csv"):
            exisiting_data.append(pd.read_csv(f"{root}/{file}"))
queries_root = "/data/home/ilanit.sobol/dv/data/outputs/reddit/subreddits/queries"

for subreddit in os.listdir(queries_root):
    for sort in os.listdir(f"{queries_root}/{subreddit}"):
        for file in os.listdir(f"{queries_root}/{subreddit}/{sort}"):
            if file.endswith(".csv"):
                try:
                    exisiting_data.append(pd.read_csv(f"{queries_root}/{subreddit}/{sort}/{file}"))
                except Exception as e:
                    pass

exisiting_data = pd.concat(exisiting_data)
exisiting_data = exisiting_data.drop_duplicates(subset=["post_id"])
post_ids = exisiting_data.post_id.values
################################################################
################## Collect data from reddit ####################

queries = ["marriage", "relationship", "love", "hate", "like", "partner", "ex", "divorce", "work", "done", "everything",
           "right", "wrong", "simple", "know", "boyfriend", "flowers", "date", "clothes", "story", "together",
           "breakup", "social", "mental", "health", "hard", "we", "me", "living"]
age_range = range(20, 55)
mrange, frange = [f"M{x}" for x in age_range], [f"F{x}" for x in age_range]
queries.extend(mrange)
queries.extend(frange)

sorts = ["hot", "new", "relevance"]
subrredit_str_lists = ['abusiverelationships', 'ToxicRelationships', 'domesticviolence', 'abusesurvivors',
                       'emotionalabuse', 'NarcAbuseAndDivorce', 'NarcissisticSpouses']

for sort in sorts:
    for query in queries:
        for subrredit_str in subrredit_str_lists:
            folder = f'{queries_root}/{query}/{sort}'
            os.makedirs(folder, exist_ok=True)
            if os.path.exists(f'{folder}/{subrredit_str}.csv'):
                continue
            current_data = []
            try:
                subreddit_obj = reddit.subreddit(subrredit_str)
                posts = list(subreddit_obj.search(query, time_filter="all", limit=500, sort=sort))
                for post in tqdm(posts, desc=f"{query}_{sort}_{subrredit_str}"):
                    if post.id in post_ids:
                        continue
                    try:
                        post_data = extract_data_from_post(post)
                        post_data.update(dict(subreddit=subrredit_str))
                        current_data.append(post_data)
                    except Exception as e:
                        pass
                df = pd.DataFrame(current_data)
                df.to_csv(f'{folder}/{subrredit_str}.csv', index=False)
            except Exception as e:
                CLIENT_ID = 'yy'
                CLIENT_SECRET = 'xx'
                USER_AGENT = 'my_user_agent'  # just give it a name
                reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT)
                time.sleep(20)
