import pandas as pd
import numpy as np
from tqdm import tqdm
import requests
import math
from zipfile import ZipFile
import geopandas as geopd
from scipy.spatial import distance
from shapely.geometry import Point

import os

os.getcwd()
os.chdir('/home/cdsw/Coursework_2_Twitter/msc_cw2')

from src.geo_etl.helper_functions import (calc_centroid_diag_bbox,
                                          check_country_in_eur_bbox,
                                          check_point_in_geom)

def main():
    print('read in preprocessed tweets')
    df = pd.read_csv('/home/cdsw/Coursework_2_Twitter/data/preprocessed_tweets.csv',
                     usecols=['longitude', 'latitude', 'tweet_id', 'place_longitude_1',
                              'place_longitude_2', 'place_latitude_1', 'place_latitude_2'])

    # df_tweets = calc_centroid_diag_bbox(df)
    #
    # print('write out df_tweets')
    # df_tweets.to_csv('tweets_diag_bbox.csv',index=False)

    df_tweets = pd.read_csv('/home/cdsw/Coursework_2_Twitter/data/tweets_diag_bbox.csv')

    print('read in tweets diag bbox')
    df_tweets = pd.read_csv('/home/cdsw/Coursework_2_Twitter/msc_cw2/tweets_diag_bbox.csv')

    
    print('Read in countries')
    # Read in zipfile with long-lat of cities in the world
    zf = ZipFile('/home/cdsw/Coursework_2_Twitter/data/simplemaps_worldcities_basicv1.75.zip')
    cities = pd.read_csv(zf.open('worldcities.csv'), usecols=['city', 'lat', 'lng', 'country', 'population'])

    # Get geopandas data for world
    gdf = geopd.read_file(geopd.datasets.get_path('naturalearth_lowres'))
    gdf['centroid'] = gdf.centroid

    print('join cities to geometry')
    # Join city data to gpd
    df_eur = pd.merge(gdf[['name', 'centroid', 'geometry']], cities, left_on='name', right_on='country', how='inner')
    df_eur.drop(columns=['name'], inplace=True)

    # Limit geopandas data to our EUR bounding box
    df_eur['in_EUR_box'] = df_eur.apply(lambda x: check_country_in_eur_bbox(x), axis=1)
    df_eur = df_eur[df_eur['in_EUR_box'] == True]

    print('Only keep cities with 100K people or more')
    # keep only cities over 100K people
    df_eur_major_city = df_eur[df_eur['population'] >= 1e5]

    # Reset index for lookups
    df_eur_major_city.reset_index(drop=True, inplace=True)
    
    print(f"{df_eur_major_city.shape[0]} cities to cross check")

    # Get lng lat for all cities in numpy array
    eur_lng_lat = df_eur_major_city[['lng', 'lat']].values

    # Array of tweet lng, lat
    tweet_lng_lat = df_tweets[['fin_lng', 'fin_lat']].values

    tweet_lng_lat.shape

    # Calculate distance from each tweet to all cities
    print('Calculate distance from each tweet to all cities')
    distance_mat = []
    for tup in tqdm(tweet_lng_lat):
        distance_mat.append(distance.cdist(tup.reshape(1, 2), eur_lng_lat))

    # Closest k cities index
    k = 5

    print('Closest 5 cities')
    closest_k_cities_index = []
    for mat in tqdm(distance_mat):
        closest_k_cities_index.append(np.argpartition(mat[0], range(k))[:k])

    cities_dict = df_eur_major_city['city'].to_dict()

    closest_k_cities = []
    for indices in tqdm(closest_k_cities_index):
        closest_k_cities.append([cities_dict[idx] for idx in indices])

    countries_dict = df_eur_major_city['country'].to_dict()

    print('Closest countries')
    closest_k_countries = []
    for indices in tqdm(closest_k_cities_index):
        closest_k_countries.append([countries_dict[idx] for idx in indices])

    # Now we need to check whether the tweet is in these countries starting with country of closes city
    country_geom_dict = {country: geom for country, geom in
                         df_eur_major_city.drop_duplicates(subset=['country'])[['country', 'geometry']].values}

    tweet_points = [Point(tup) for tup in df_tweets[['fin_lng', 'fin_lat']].values]

    df_tweets['point'] = tweet_points

    idx_tweet_geo_dict = {idx: {'tweet_id': t[0], 'point': t[1]} for t, idx in
                          zip(df_tweets[['tweet_id', 'point']].values, df_tweets.index)}

    print('tweet country dict')
    for i, v in tqdm(enumerate(zip(closest_k_cities, closest_k_countries))):
        city_lst, country_lst = v[0], v[1]
        # set confirmed location flag to False
        idx_tweet_geo_dict[i]['confirmed'] = False

        counter = 1
        for city, country in zip(city_lst, country_lst):
            # if tweet geo point in country geom == True
            twt_point = idx_tweet_geo_dict[i]['point']
            country_geom = country_geom_dict[country]

            if check_point_in_geom(twt_point, country_geom):
                idx_tweet_geo_dict[i]['city'] = city
                idx_tweet_geo_dict[i]['country'] = country
                idx_tweet_geo_dict[i]['rank'] = counter
                idx_tweet_geo_dict[i]['confirmed'] = True
                break
            counter += 1

        # If tweet not in any of listed country input np.nan
        if idx_tweet_geo_dict[i].get('confirmed') == False:
            idx_tweet_geo_dict[i]['city'] = city_lst[0]
            idx_tweet_geo_dict[i]['country'] = country_lst[0]


    df_tweet_geo = pd.DataFrame.from_dict(idx_tweet_geo_dict, orient='index')

    print('Write out df_tweet_geo')
    df_tweet_geo.to_csv('/home/cdsw/Coursework_2_Twitter/data/tweet_geo.csv',index=False)

    
if __name__=='__main__':
  main()