import pandas as pd
import numpy as np

def main():

    dfs = []
    for i in range(5):
        csv = f'../cdsw/Coursework_2_Twitter/data/tweets_{i}.csv'
        tmp_df = pd.read_csv(csv, index_col=0)
        dfs.append(tmp_df)

    df_tot = pd.concat(dfs)
    df_tot.rename(columns={'place_atitude_2': 'place_latitude_2'}, inplace=True)

    dfs = []
    for i in range(5):
        csv = f'../cdsw/Coursework_2_Twitter/data/tweet_user_dt_{i}.csv'
        tmp_df = pd.read_csv(csv, index_col=0, parse_dates=['dt_obj'])
        dfs.append(tmp_df)

    df_user_dt = pd.concat(dfs)
    df_user_dt = df_user_dt.reset_index()
    df_comb = pd.concat([df_tot, df_user_dt], axis=1)

    tc1 = df_comb.shape[0]
    # Drop duplicate columns
    df_comb = df_comb.loc[:, ~df_comb.columns.duplicated()]

    # Drop tweets with missing tweet_ids
    df_comb.dropna(subset=['tweet_id'], inplace=True)
    tc2 = df_comb.shape[0]

    # Drop duplicate tweets
    df_comb.drop_duplicates(subset=['tweet_id'], inplace=True)
    tc3 = df_comb.shape[0]

    #Convert dt_obj column to datetime
    # df_comb['dt_obj'] = pd.to_datetime(df_comb['dt_obj'])

    # Limit tweets to June
    df_comb = df_comb[df_comb['dt_obj_dt'].dt.month == 6]
    tc4 = df_comb.shape[0]

    print(f'Dropped {tc1-tc2} tweets without an id')
    print(f'Dropped {tc2 - tc3} duplicate tweets')
    print(f'Dropped {tc3-tc4} from May')
    print(f'Remaining tweets: {tc4}')

    df_comb.to_csv('../cdsw/Coursework_2_Twitter/data/preprocessed_tweets.csv', index=False)

if __name__ == "__main__":
    main()