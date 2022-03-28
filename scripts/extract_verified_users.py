from src.etl.extract_tweet_data import ExtractTweetData
from zipfile import ZipFile
import os
import json
from tqdm import tqdm
import pandas as pd

os.chdir('/Users/u1079317/Desktop/Personal/MSc_Exeter/Intro_DS/CW2/data')
cwd = os.getcwd()

verified_users = {'screen_name': [], 'user_id': []}
for zfile in tqdm(sorted(os.listdir(cwd))):
    if '.zip' in zfile:
        zip_path = os.path.join(cwd, zfile)
        with ZipFile(zip_path) as zf:
            with zf.open(zf.namelist()[0]) as tmp_json:
                for tweet in tmp_json.readlines():
                    tweet_dict = json.loads(tweet)
                    etd = ExtractTweetData(tweet_dict)

                    slm_twt = etd.get_slim_tweet(tweet_id=False,
                                                   user_id=True,
                                                   coords=False,
                                                   date=False,
                                                   place=False,
                                                   text=False,
                                                   retweet=False,
                                                   user_name=False,
                                                   screen_name=True,
                                                   user_mentions=False,
                                                   hashtags=False,
                                                    user_verified_status=True)

                    if slm_twt['user_verified_status']:
                        if not slm_twt['screen_name'] in verified_users['screen_name']:
                            verified_users['screen_name'].append(slm_twt['screen_name'])
                            verified_users['user_id'].append(slm_twt['user_id'])

df = pd.DataFrame(verified_users)
print(df.shape)
df.to_csv('/Users/u1079317/Desktop/Personal/MSc_Exeter/Intro_DS/CW2/data/verified_users.csv', index=False)