import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re

########################################################################
# Tweets per User Hist
########################################################################

dfs = []
for i in range(5):
    csv = f'tweet_screen_name_{i}.csv'
    path = f'/home/cdsw/Coursework_2_Twitter/data/{csv}'
    dfs.append(pd.read_csv(path))

df_user = pd.concat(dfs)
df_user.reset_index(drop=True, inplace=True)

df_t = pd.read_csv('/home/cdsw/Coursework_2_Twitter/data/preprocessed_tweets.csv', usecols=['tweet_id','user_id'])

df_tot_users = pd.DataFrame(df_t.groupby('user_id').count()['tweet_id']).rename(columns={'tweet_id':'tweet_count'})

bins = np.array([1,2,4,8,16,32,64,128,250,500,1000, 2000, 4000, 8000, 16000])
i = 1
halfway = []
for v in bins[1:]:
    halfway.append( i+(v-i)/2)
    i = v

i = 1
halfway_lab = []
for v in bins[1:]:
    if v>1e3:
        halfway_lab.append(f'{i/1e3:.0f}k-{v/1e3:.0f}k')
    else:
        halfway_lab.append(f'{i}-{v}')
    i = v

fig, ax = plt.subplots()
ax.hist(df_tot_users['tweet_count'], bins=bins, log=True, ec='k')
ax.set_xscale('log')

ax.set_xticks(halfway)
ax.set_xticklabels(halfway_lab, rotation=90)

ax.set_title('Histogram of Tweets Per User Plotted on Log:Log Scale')
ax.set_ylabel('Number of Users in Each Bin')
ax.set_xlabel('Tweets Per User')

fig.savefig('/home/cdsw/Coursework_2_Twitter/static/hist_tweets_per_user.png');


########################################################################
# Top 5 Users
########################################################################
top_user_ids = df_tot_users.sort_values(by=['tweet_count'], ascending=False).iloc[:5]['user_id'].values

df_top_5_users = df_tot_users.sort_values(by=['tweet_count'], ascending=False).iloc[:5].reset_index() \
    .merge(df_user[df_user['user_id'].isin(top_user_ids)].drop_duplicates(), how='inner',
           on='user_id')


# Combine tweet text to review some tweets
dfs = []
for i in range(5):
    csv = f'tweet_text_{i}.csv'
    path = f'/home/cdsw/Coursework_2_Twitter/data/{csv}'
    dfs.append(pd.read_csv(path, lineterminator='\n'))

df_txt = pd.concat(dfs)
df_txt.reset_index(drop=True, inplace=True)

df_tot = pd.read_csv('/home/cdsw/Coursework_2_Twitter/data/preprocessed_tweets.csv',
                     usecols=['tweet_id', 'user_id', 'dt_obj'],
                     parse_dates=['dt_obj'])

df_tot_top_5_users = df_tot[df_tot['user_id'].isin(df_top_5_users.user_id.values)]
df_tot_top_5_users = pd.merge(df_tot_top_5_users, df_top_5_users, how='inner', on='user_id')
df_tot_top_5_users = pd.merge(df_tot_top_5_users, df_txt[df_txt['tweet_id'].isin(df_tot_top_5_users.tweet_id.values)],
                              how='inner', on='tweet_id')

#Method used to print out results for each user

for row in df_top_5_users.itertuples():
    user_id = row.user_id
    tweet_count = row.tweet_count
    screen_name = row.screen_name
    avg_min_bet_tweets = (30 * 24 * 60) / tweet_count

    print(
        f"""The number {row.Index + 1} tweeter, measured by tweet count, is {screen_name} (user_id: {str(int(user_id))}).\n"""
        f"""They tweeted {tweet_count} times in June 2021\n"""
        f"""that equates to a tweet every {avg_min_bet_tweets:.2f} minutes\n\n""")


########################################################################
# Top 5 Users by Mention
########################################################################

def extract_at_hashtags(text):
    pat = '(?i)(#\S*)|(@ ?\S*)'
    return [''.join(tup).replace(' ','') for tup in re.findall(pat,str(text))]


tweet_texts = df_txt.dropna().values

hashtags_with_ws = {}
for tweet in tweet_texts:
    try:
        for tag in extract_at_hashtags(tweet):
            if hashtags_with_ws.get(tag):
                hashtags_with_ws[tag]['count'] += 1
                hashtags_with_ws[tag]['tweets'].append(tweet)
            else:
                hashtags_with_ws[tag] = {'count': 1, 'tweets':[tweet]}
    except Exception as e:
        print(tweet)
        print(e)
        break

top_mentions = sorted([(k,v['count']) for k,v in hashtags_with_ws.items()], key=lambda x: x[1], reverse=True)