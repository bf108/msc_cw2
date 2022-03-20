import numpy as np
from datetime import datetime
import time


class ExtractTweetData:

    def __init__(self, tweet_json):
        self.tweet_json = tweet_json
        self.slm_tweet = dict()

    def extract_coordinates(self):
        try:
            self.slm_tweet['longitude'], self.slm_tweet['latitude'] = self.tweet_json.get('coordinates').get(
                'coordinates', np.nan)
        except:
            self.slm_tweet['longitude'], self.slm_tweet['latitude'] = np.nan, np.nan

        try:
            self.slm_tweet['cord_type'] = self.tweet_json.get('coordinates').get('type', np.nan)
        except:
            self.slm_tweet['cord_type'] = np.nan

    def extract_date(self):
        try:
            date_str = self.tweet_json.get('created_at')
            self.slm_tweet['dt_obj'] = datetime.fromtimestamp(
                time.mktime(time.strptime(date_str, '%a %b %d %H:%M:%S %z %Y')))
        except:
            self.slm_tweet['dt_obj'] = np.nan

    def extract_tweet_id(self):
        self.slm_tweet['tweet_id'] = self.tweet_json.get('id', np.nan)

    def extract_user_id(self):
        try:
            self.slm_tweet['user_id'] = self.tweet_json.get('user').get('id', np.nan)
        except:
            self.slm_tweet['user_id'] = np.nan

    def extract_user_name(self):
        try:
            self.slm_tweet['user_name'] = self.tweet_json.get('user').get('name', np.nan)
        except:
            self.slm_tweet['user_name'] = np.nan

    def extract_screen_name(self):
        try:
            self.slm_tweet['screen_name'] = self.tweet_json.get('user').get('screen_name', np.nan)
        except:
            self.slm_tweet['screen_name'] = np.nan

    def extract_user_friend_count(self):
        try:
            self.slm_tweet['user_friend_count'] = self.tweet_json.get('user').get('friends_count', np.nan)
        except:
            self.slm_tweet['user_friend_count'] = np.nan

    def extract_user_statuses_count(self):
        try:
            self.slm_tweet['user_statuses_count'] = self.tweet_json.get('user').get('statuses_count', np.nan)
        except:
            self.slm_tweet['user_statuses_count'] = np.nan

    def extract_place(self):
        if self.tweet_json.get('place'):
            for key in ['name', 'id', 'country']:
                self.slm_tweet[f'place_{key}'] = self.tweet_json['place'].get(key, np.nan)

            try:
                self.slm_tweet['place_longitude_1'] = \
                    self.tweet_json['place'].get('bounding_box').get('coordinates', np.nan)[0][0][0]
                self.slm_tweet['place_longitude_2'] = \
                    self.tweet_json['place'].get('bounding_box').get('coordinates', np.nan)[0][2][0]
                self.slm_tweet['place_latitude_1'] = \
                    self.tweet_json['place'].get('bounding_box').get('coordinates', np.nan)[0][0][1]
                self.slm_tweet['place_atitude_2'] = \
                    self.tweet_json['place'].get('bounding_box').get('coordinates', np.nan)[0][2][1]
            except:
                for key in ['longitude_1', 'longitude_2', 'latitude_1', 'latitude_2']:
                    self.slm_tweet[f'place_{key}'] = np.nan

        else:
            for key in ['name', 'id', 'country', 'longitude_1', 'longitude_2', 'latitude_1', 'latitude_2']:
                self.slm_tweet[f'place_{key}'] = np.nan

    def extract_text(self):
        self.slm_tweet['text'] = self.tweet_json.get('text', 'no_text')

    def extract_retweet_status(self):
        self.slm_tweet['retweeted'] = True if self.tweet_json.get('retweeted', np.nan) == 'True' else False


    def extract_user_mentions(self):
        self.slm_tweet['user_mentions'] = self.tweet_json.get('user_mentions', [])


    def extract_hashtags(self):
        self.slm_tweet['hashtags'] = self.tweet_json.get('hashtags', [])


    def produce_slim_tweet(self):
        # self.extract_coordinates()
        # self.extract_date()
        self.extract_tweet_id()
        # self.extract_user_id()
        # self.extract_place()
        # self.extract_text()
        # self.extract_retweet_status()
        # self.extract_user_name()
        # self.extract_screen_name()
        self.extract_user_mentions()
        self.extract_hashtags()

        # self.extract_user_friend_count()
        # self.extract_user_statuses_count()

    def get_slim_tweet(self):
        if len(self.slm_tweet) == 0:
            self.produce_slim_tweet()

        return self.slm_tweet
