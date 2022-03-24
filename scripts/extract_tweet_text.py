from src.etl.extract_tweet_data import ExtractTweetData
from zipfile import ZipFile
import os
import json
from tqdm import tqdm
import pandas as pd

os.chdir('/Users/u1079317/Desktop/Personal/MSc_Exeter/Intro_DS/CW2/data')
cwd = os.getcwd()

slim_down_tweet_list = []
for zfile in tqdm(sorted(os.listdir(cwd))):
    zip_path = os.path.join(cwd, zfile)
    with ZipFile(zip_path) as zf:
        with zf.open(zf.namelist()[0]) as tmp_json:
            for tweet in tmp_json.readlines():
                tweet_dict = json.loads(tweet)
                etd = ExtractTweetData(tweet_dict)
                slim_down_tweet_list.append(etd.get_slim_tweet(tweet_id=True,
                       user_id=True,
                       coords=True,
                       date=True,
                       place=True,
                       text=True,
                       retweet=True,
                       user_name=True,
                       screen_name=True,
                       user_mentions=True,
                       hashtags=True))


df = pd.DataFrame(slim_down_tweet_list)

print(df.shape)

#Chunk the csv into more managable size files.
for idx, chunk in enumerate(np.array_split(df,5)):
    csv_str = f'../CW2/data/slim_down_tweet_user_data_{idx}.csv'
    chunk.to_csv(csv_str, index=False)

# df.to_csv('../Intro_DS/CW2/slim_down_tweets_retweet.csv')
# df.to_csv('../Intro_DS/CW2/slim_down_tweets_user_data_screen_name.csv',index=False)
# df.to_csv('../Intro_DS/CW2/slim_down_tweets_entities.csv',index=False)