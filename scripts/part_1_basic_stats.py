import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.ticker as ticker
from matplotlib.dates import DateFormatter, DayLocator
import calendar
from matplotlib import rc

########################################################
# Import Data
########################################################

df_t = pd.read_csv('/home/cdsw/Coursework_2_Twitter/data/preprocessed_tweets.csv',
                   usecols=['tweet_id', 'dt_obj'],
                   parse_dates=['dt_obj']
                  )


########################################################
# Q1.2 Time Series Tweets Per Day
########################################################

tweets_per_day = df_t.groupby(df_t['dt_obj'].dt.date).count()['tweet_id']

max_val = tweets_per_day.max()
max_day = np.argmax(tweets_per_day).day

min_val = tweets_per_day.min()
min_day = np.argmin(tweets_per_day).day


def thousands(val, pos):
    """
    val - float - value to be formatted
    pos - tick position
    """
    return f'{val * 1e-3:.0f}K'


formatter = ticker.FuncFormatter(thousands)

fig, ax = plt.subplots(2, figsize=(6, 4))

for axis in ax:
    axis.xaxis.set_major_formatter(DateFormatter("%d"))
    axis.xaxis.set_major_locator(DayLocator(interval=1))

    axis.yaxis.set_major_formatter(formatter)
    axis.set_ylabel('Tweets', fontdict={'weight': 'bold'})

tweets_per_day.plot(ax=ax[0])
ax[0].set_ylim(0, 5.5e5)
ax[0].set_xlabel('')

tweets_per_day.plot(ax=ax[1])
ax[1].set_ylim(4e5, 5.5e5)
ax[1].set_xlabel('Date in June 2021', fontdict={'weight': 'bold'})

fig.suptitle('Tweets per day in Europe')

fig.savefig('../static/time_series_tweet_whole_eur.png');


########################################################
# Q1.3 Compare Daily Tweets Between Weekend and Weekdays
########################################################

#Provide weekday int and extract day from datetime obj
df_t['weekday_int'] = df_t['dt_obj'].dt.weekday
df_t['day_int'] = df_t['dt_obj'].dt.day

group_tweets = df_t.groupby(['weekday_int','day_int']).count()[['tweet_id']].unstack('weekday_int')
group_tweets.columns = [calendar.day_name[c] for c in group_tweets.columns.droplevel()]

#Plot Daily Box Plots
fig, ax = plt.subplots(figsize=(6,4))
ax.set_ylabel('Tweets',fontdict={'weight':'bold'})
x_tick_labels = [l.get_text() for l in ax.get_xticklabels()]
ax.set_xticklabels(x_tick_labels, fontdict={'weight':'bold'})
ax.set_title('Tweets per Day of Week in June 2021')
group_tweets.reset_index(drop=True).plot(kind='box', ax=ax)
ax.set_ylim(400000,550000)
ax.grid(b=True, which='major',axis='both')
ax.yaxis.set_major_formatter(formatter)
fig.savefig('../static/box_plots_daily_q_1_3_1.png')

#Plot Daily Bar Chart
x_pos = np.arange(len(group_tweets.columns))
x_vals = group_tweets.describe().loc[['mean'],:].values[0]
errors = group_tweets.describe().loc[['std'],:].values[0]
x_labels = group_tweets.columns
width = 0.6

fig, ax = plt.subplots(2,figsize=(6,5))
ax[0].set_title('Mean Tweets per weekday in June 2021 Europe')

for axis in ax:
    axis.set_ylabel('Tweets', fontdict={'weight':'bold'})
    axis.bar(x_pos, x_vals, yerr=errors, align='center', alpha=0.5, ecolor='black', capsize=6, width=width)
    axis.grid(b=True, which='major',axis='both')
    axis.yaxis.set_major_formatter(formatter)

ax[0].set_xticklabels(['' for i in range(7)])
ax[1].set_xticks(x_pos)
ax[1].set_xticklabels(x_labels, fontdict={'weight':'bold'})
ax[1].set_ylim(4e5,5.5e5);
fig.savefig('../static/bar_plots_daily_q_1_3_2.png')


#Group weekdays and weekends
wkd = group_tweets.columns[:5]
wked = group_tweets.columns[5:]

group_tweets['weekday'] = group_tweets[wkd].mean(axis=1)
group_tweets['weekends'] = group_tweets[wked].mean(axis=1)

#Plot Weekend vs Weekday Box Plots
fig, ax = plt.subplots(figsize=(5,3))
ax.set_ylabel('Tweets', fontdict={'weight':'bold'})
ax.set_title('Num of Tweets on Weekdays vs Weekends June 2021')
group_tweets[['weekday','weekends']].reset_index(drop=True).plot(kind='box', ax=ax)
ax.set_ylim(400000,550000)
ax.grid(which='major',axis='x', b=True)
ax.yaxis.set_major_formatter(formatter)

fig.savefig('../static/box_plots_wd_vs_we_q_1_3_3.png');

#Plot Weekend vs Weekday Bar Charts
x_pos = np.arange(len(group_tweets[['weekday','weekends']].columns))
x_vals = group_tweets[['weekday','weekends']].describe().loc[['mean'],:].values[0]
errors = group_tweets[['weekday','weekends']].describe().loc[['std'],:].values[0]
x_labels = group_tweets[['weekday','weekends']].columns
width = 0.4

fig, ax = plt.subplots(2,figsize=(5,5))
ax[0].set_title('Mean Tweets per weekday/weekend in June 2021 Europe')
for axis in ax:
    axis.set_ylabel('Number of Tweets')
    axis.bar(x_pos, x_vals, yerr=errors, align='center', alpha=0.5, ecolor='black', capsize=6, width=width)
    axis.grid(b=True, which='major',axis='both')
    axis.yaxis.set_major_formatter(formatter)

ax[0].set_xticklabels(['' for i in range(7)])
ax[0].set_ylim(0,6e5);
ax[1].set_xticks(x_pos)
ax[1].set_xticklabels(x_labels)
ax[1].set_ylim(3e5,5.5e5)
fig.savefig('../static/bar_plots_wd_vs_we_q_1_3_4.png');


########################################################
# Q1.4 Compare Hourly Tweets Between Weekend and Weekdays
########################################################

df_t['hr'] = df_t['dt_obj'].dt.hour

tweets_per_day_hr = df_t.groupby(['weekday_int','day_int','hr']).count()['tweet_id'].unstack()\
.groupby(['weekday_int']).mean()\
.transpose().rename(columns={i:calendar.day_name[i] for i in range(7)})

tweets_per_day_hr.index.name = None
tweets_per_day_hr.columns.name = None


rc('font',weight='bold')

fig, ax = plt.subplots(figsize=(8,4))
ax.set_title('Avg tweets/hr', fontdict={'weight':'bold'})
ax.set_ylabel('Tweets', fontdict={'weight':'bold'})
ax.set_xlabel('Time (24hr format)', fontdict={'weight':'bold'})

tweets_per_day_hr.plot(kind='line', ax=ax);

x_pos = np.arange(24)
ax.set_xticks(x_pos)
ax.set_xticklabels(x_pos)
ax.grid(b=True,which='major',axis='both')
ax.grid(b=True, which='major',axis='both')
ax.yaxis.set_major_formatter(formatter)

ax.legend(loc='upper left',
          bbox_to_anchor=(-0.05, -0.2), fancybox=True, shadow=True, ncol=7, prop={'size': 8})

fig.savefig('../static/daily_tweets_per_hr.png');

tmp_df = df_t.groupby(['weekday_int','day_int','hr']).count()['tweet_id'].unstack()

df_tmp_wd = tmp_df[tmp_df.index.get_level_values('weekday_int') < 5]
df_tmp_we = tmp_df[tmp_df.index.get_level_values('weekday_int') >= 5]
df_tmp_wd_ = df_tmp_wd.reset_index(drop=True).describe().transpose()[['mean','std']].rename(columns={'mean':'weekday_mean','std':'weekday_std'})
df_tmp_we_ = df_tmp_we.reset_index(drop=True).describe().transpose()[['mean','std']].rename(columns={'mean':'weekend_mean','std':'weekend_std'})
df_ts_wk_we = pd.concat([df_tmp_wd_,df_tmp_we_],axis=1)

fig, ax = plt.subplots(figsize=(8,4))
ax.set_title('Avg tweets/hr - Weekdays vs Weekends', fontdict={'weight':'bold'})
ax.set_ylabel('Tweets', fontdict={'weight':'bold'})
ax.set_xlabel('Time (24hr format)',  fontdict={'weight':'bold'})

ax.plot(df_ts_wk_we['weekday_mean'], label='Weekdays')
ax.fill_between(np.arange(24),df_ts_wk_we['weekday_mean']-df_ts_wk_we['weekday_std'],df_ts_wk_we['weekday_mean']+df_ts_wk_we['weekday_std'], alpha=0.3)
ax.plot(df_ts_wk_we['weekend_mean'], label='Weekends')
ax.fill_between(np.arange(24),df_ts_wk_we['weekend_mean']-df_ts_wk_we['weekend_std'],df_ts_wk_we['weekend_mean']+df_ts_wk_we['weekend_std'], alpha=0.5)

x_pos = np.arange(24)
ax.set_xticks(x_pos)
ax.set_xticklabels(x_pos)
ax.grid(b=True,which='major',axis='both')
ax.yaxis.set_major_formatter(formatter)
# ax.legend(loc=2, ncol=2)

ax.legend(loc='upper left',
          bbox_to_anchor=(0.3, -0.2), fancybox=True, shadow=True, ncol=7, prop={'size': 8});

fig.savefig('../static/weekday_vs_weekend_tweets_per_hr.png');
