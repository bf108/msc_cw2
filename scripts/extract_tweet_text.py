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
                slim_down_tweet_list.append(etd.get_slim_tweet())


df = pd.DataFrame(slim_down_tweet_list)

print(df.shape)

df.to_csv('/Users/u1079317/Desktop/Personal/MSc_Exeter/Intro_DS/CW2/slim_down_tweets_retweet.csv')