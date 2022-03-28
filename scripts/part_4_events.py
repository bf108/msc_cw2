from wordcloud import STOPWORDS
from src.viz.plotting_functions import create_word_cloud
import pandas as pd
import numpy as np

########################################################################
# Prepare / import Data
########################################################################

#Read in dfs
df_geo = pd.read_csv('/home/cdsw/Coursework_2_Twitter/data/tweet_geo.csv',usecols=['tweet_id','country'])
df_t = pd.read_csv('/home/cdsw/Coursework_2_Twitter/data/preprocessed_tweets.csv',
                   usecols=['tweet_id','dt_obj'],
                  parse_dates=['dt_obj'])
dfs = []
for i in range(5):
    csv = f'tweet_text_{i}.csv'
    path = f'/home/cdsw/Coursework_2_Twitter/data/{csv}'
    dfs.append(pd.read_csv(path , lineterminator='\n'))

df_txt = pd.concat(dfs)
df_txt.reset_index(drop=True, inplace=True)
df_comb = pd.concat([df_geo, df_t['dt_obj']], axis=1)

########################################################################
# Prepare / import Data
########################################################################

create_word_cloud('United Kingdom', stop_words=STOPWORDS)

create_word_cloud('France', stop_words=eng_fr_stop_words, det_lng='fr')

