import matplotlib.pyplot as plt
import numpy as np


def annot_max(x,y, ax=None):
    xmax = x[np.argmax(y)]-1
    ymax = y.max()
    text= f"{xmax}th June\n{ymax*1e-3:.0f}k tweets"
    if not ax:
        ax=plt.gca()
    bbox_props = dict(boxstyle="square,pad=0.2", fc="w", ec="k", lw=0.72)
    arrowprops=dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=60", ec='k')
    kw = dict(xycoords='data',textcoords="axes fraction",
              arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top")
    ax.annotate(text, xy=(xmax, ymax), xytext=(.4,0.85), fontsize=7, **kw)


def plot_tweets_country(country):
    df_country = df_comb[df_comb['country'] == country]
    df_country_tweet_per_day = df_country.groupby(df_country['dt_obj'].dt.day).count()[['tweet_id']].rename(
        columns={'tweet_id': 'tweet_count'})

    max_tweets = df_country_tweet_per_day.max().values[0]
    day = np.argmax(df_country_tweet_per_day.tweet_count)
    mean_tweets = df_country_tweet_per_day.mean().values[0]
    print(f'{max_tweets / mean_tweets:.2f} x greater than monthly average')

    fig, ax = plt.subplots(figsize=(6, 4))
    df_country_tweet_per_day.plot(ax=ax)
    annot_max(df_country_tweet_per_day.index.values, df_country_tweet_per_day.tweet_count, ax=ax)
    ax.yaxis.set_major_formatter(formatter)
    ax.set_ylabel('Tweet Count', fontdict={'weight': 'bold'})
    ax.set_xlabel('Date in June', fontdict={'weight': 'bold'})
    ax.legend(loc='upper left', bbox_to_anchor=(0, 1), fontsize=8)
    ax.set_title(f'Tweets per day in {country}')
    plt.show()

    return day


def create_corpus(text_string):
    # Tokenize, remove blank spaces, lowercase, remove punctuation, drop words with length<=2
    corpus = {}
    for word in text_string.split(' '):
        # normalize
        w = word.strip().lower().translate(str.maketrans('', '', string.punctuation))
        if len(w) >= 3 and "’" not in w:
            if corpus.get(w):
                corpus[w] += 1
            else:
                corpus[w] = 1

    return corpus


def frequency_words(date, country, stop_words=None):
    tweet_ids_on_date = df_comb[(df_comb['dt_obj'].dt.day == date) & (df_comb['country'] == country)]['tweet_id'].values
    all_tweets = ' '.join(df_txt[df_txt['tweet_id'].isin(tweet_ids_on_date)]['text'].values)
    corpus = create_corpus(all_tweets)
    frequency = sorted([(k, v) for k, v in corpus.items()], key=lambda x: x[1], reverse=True)
    if stop_words:
        frequency_after_stop = [tup for tup in frequency if tup[0] not in stop_words]
        frequency_after_stop_dict = {tup[0]: tup[1] for tup in frequency_after_stop}
    else:
        frequency_after_stop_dict = {tup[0]: tup[1] for tup in frequency}

    return frequency_after_stop_dict


def create_word_cloud(country, stop_words=None, det_lng=None):
    """
    country: str - 'name of country'
    stop_words: list (str) - stop words to include
    det_lng: str - iso 639-1 code for language e.g en=English, es=Spanish, de-li=german
    """
    day = plot_tweets_country(country)
    frequency_after_stop_dict = frequency_words(day, country, stop_words=stop_words)

    if det_lng:
        translator = Translator(from_lang=det_lng, to_lang='en')

        # Only translate top 50 words
        trans_frequency_after_stop_dict = {}
        counta = 1
        for k, v in sorted([(k, v) for k, v in frequency_after_stop_dict.items()], key=lambda x: x[1], reverse=True):
            if counta < 50:
                word_trans = translator.translate(k).split(' ')[0]
                trans_frequency_after_stop_dict[word_trans] = v
                counta += 1
            else:
                trans_frequency_after_stop_dict[k] = v
        frequency_after_stop_dict = trans_frequency_after_stop_dict

    if stop_words:
        wrdcloud = WordCloud(stopwords=stop_words).generate_from_frequencies(frequencies=frequency_after_stop_dict)
    else:
        wrdcloud = WordCloud().generate_from_frequencies(frequencies=frequency_after_stop_dict)

    plt.figure()
    plt.imshow(wrdcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title(f'World Cloud for Tweets in {country} on {day} June 2021')
    plt.show()