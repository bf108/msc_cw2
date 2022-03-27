import pandas as pd
from tqdm import tqdm
import os
from geopy.distance import geodesic
import numpy as np

os.getcwd()
os.chdir('/home/cdsw/Coursework_2_Twitter/msc_cw2')

from src.geo_etl.helper_functions import (calc_centroid_diag_bbox,
                                          check_country_in_eur_bbox,
                                          check_point_in_geom,
                                          edges_leading_diaganol)


def main():
    print('Read in preprocessed tweets')
    df = pd.read_csv('/home/cdsw/Coursework_2_Twitter/data/preprocessed_tweets.csv',
                     usecols=['longitude', 'latitude', 'tweet_id', 'place_longitude_1',
                              'place_longitude_2', 'place_latitude_1', 'place_latitude_2'])
    ########################################################################
    # Calculate diagonal length for location bounding boxes
    ########################################################################

    print('drop nans')
    tmp_df = df.dropna(subset=['place_longitude_1']).sample(10)

    #Get edges of box
    cols = ['place_longitude_1', 'place_longitude_2', 'place_latitude_1', 'place_latitude_2']
    print('get edges')
    edges_bbox = edges_leading_diaganol(*[df[c].values for c in cols])

    print('start loop for distances')
    diagonal = []
    for blhc, trhc in tqdm(zip(edges_bbox[0], edges_bbox[1])):
        try:
            ans = abs(geodesic(blhc, trhc).kilometers)
            # ans = abs(np.linalg.norm(trhc - blhc))
        except:
            ans = np.nan
        diagonal.append(ans)

    print('write out df')
    df_diagonal = pd.DataFrame(diagonal, columns=['diagonal'])
    df_diagonal.to_csv('/home/cdsw/Coursework_2_Twitter/msc_cw2/tweets_geodesic_diag_box.csv',
                       index=False)

    ########################################################################
    # Calculate centroid and diagonal length for location bounding boxes
    ########################################################################
    # print('Calculate centroid for all location bounding boxes')
    # df_tweets = calc_centroid_diag_bbox(df)
    # print('Write out df_tweets_diag_bbox.csv...')
    # df_tweets.to_csv('tweets_diag_bbox.csv', index=False)

    # print('read in tweets diag bbox')
    # df_tweets = pd.read_csv('/home/cdsw/Coursework_2_Twitter/msc_cw2/tweets_diag_bbox.csv')

    ########################################################################
    # Find Major Cities within Bounding Box
    ########################################################################

    # print('Read in countries')
    # # Read in zipfile with long-lat of cities in the world
    # zf = ZipFile('/home/cdsw/Coursework_2_Twitter/data/simplemaps_worldcities_basicv1.75.zip')
    # cities = pd.read_csv(zf.open('worldcities.csv'), usecols=['city', 'lat', 'lng', 'country', 'capital'])
    #
    # # Get geopandas data for world
    # gdf = geopd.read_file(geopd.datasets.get_path('naturalearth_lowres'))
    # gdf['centroid'] = gdf.centroid
    #
    # print('join cities to geometry')
    # # Join city data to gpd
    # df_eur = pd.merge(gdf[['name', 'centroid', 'geometry']], cities, left_on='name', right_on='country', how='inner')
    # df_eur.drop(columns=['name'], inplace=True)
    #
    # # Limit geopandas data to our EUR bounding box
    # df_eur['in_EUR_box'] = df_eur.apply(lambda x: check_country_in_eur_bbox(x), axis=1)
    # df_eur = df_eur[df_eur['in_EUR_box'] == True]
    #
    # print('Only keep capital cities')
    # # keep only capital cities and few other essentials
    # missed_city = ['Belfast', 'Cagliari', 'Edinburgh', 'Palma', 'Rijeka', 'Tangier', 'İzmir']
    # df_eur_major_city = df_eur[(df_eur['capital'] == 'primary') | (df_eur['city'].isin(missed_city))]
    #
    # # Reset index for lookups
    # df_eur_major_city.reset_index(drop=True, inplace=True)
    #
    # print(f"{df_eur_major_city.shape[0]} cities to cross check")
    #
    # ########################################################################
    # # Find Euclidian Distance to Capital Cities within Bounding Box
    # # Find closest 20 capital cities, and their corresponding country, to each tweet
    # ########################################################################
    #
    # # Get lng lat for all cities in numpy array
    # eur_lng_lat = df_eur_major_city[['lng', 'lat']].values
    #
    # # Array of tweet lng, lat
    # tweet_lng_lat = df_tweets[['fin_lng', 'fin_lat']].values
    #
    # # Calculate distance from each tweet to all capital cities
    # print('Calculate distance from each tweet to all capital cities')
    # distance_mat = []
    # for tup in tweet_lng_lat:
    #     distance_mat.append(distance.cdist(tup.reshape(1, 2), eur_lng_lat))
    #
    # # Closest k cities index
    # k = 20
    #
    # print(f'Closest {k} capital cities')
    # closest_k_cities_index = []
    # for mat in distance_mat:
    #     closest_k_cities_index.append(np.argpartition(mat[0], range(k))[:k])
    #
    # cities_dict = df_eur_major_city['city'].to_dict()
    #
    # closest_k_cities = []
    # for indices in closest_k_cities_index:
    #     closest_k_cities.append([cities_dict[idx] for idx in indices])
    #
    # countries_dict = df_eur_major_city['country'].to_dict()
    #
    # print('Closest countries')
    # closest_k_countries = []
    # for indices in closest_k_cities_index:
    #     closest_k_countries.append([countries_dict[idx] for idx in indices])
    #
    # #########################################################################
    # # Check whether the tweet is in countries associated with closest city
    # #########################################################################
    #
    # # Set up dictionary for country and geometry
    # country_geom_dict = {country: geom for country, geom in
    #                      df_eur_major_city.drop_duplicates(subset=['country'])[['country', 'geometry']].values}
    #
    # # List of coords for all tweets
    # tweet_points = [Point(tup) for tup in df_tweets[['fin_lng', 'fin_lat']].values]
    # df_tweets['point'] = tweet_points
    #
    # # Set up dictionary to store all results
    # idx_tweet_geo_dict = {idx: {'tweet_id': t[0], 'point': t[1]} for t, idx in
    #                       zip(df_tweets[['tweet_id', 'point']].values, df_tweets.index)}
    #
    # print('tweet country dict')
    #
    # count_unplaced_tweets = 0
    #
    # # Loop through all closest city: country list pairs
    # for i, v in enumerate(zip(closest_k_cities, closest_k_countries)):
    #     city_lst, country_lst = v[0], v[1]
    #     # set confirmed location flag to False
    #     idx_tweet_geo_dict[i]['confirmed'] = False
    #
    #     counter = 1
    #     for city, country in zip(city_lst, country_lst):
    #         twt_point = idx_tweet_geo_dict[i]['point']
    #         country_geom = country_geom_dict[country]
    #
    #         # If the tweet is in country geom, then assign values in dict and exit loop
    #         if check_point_in_geom(twt_point, country_geom):
    #             idx_tweet_geo_dict[i]['city'] = city
    #             idx_tweet_geo_dict[i]['country'] = country
    #             idx_tweet_geo_dict[i]['rank'] = counter
    #             idx_tweet_geo_dict[i]['confirmed'] = True
    #             break
    #         counter += 1
    #
    #     # If tweet not in any of listed country assign to country of closest city
    #     if idx_tweet_geo_dict[i].get('confirmed') == False:
    #         idx_tweet_geo_dict[i]['city'] = city_lst[0]
    #         idx_tweet_geo_dict[i]['country'] = country_lst[0]
    #         count_unplaced_tweets += 1
    #
    # print(f'There are a total of {count_unplaced_tweets} tweets which were not confirmed mapped to a country')
    #
    # df_tweet_geo = pd.DataFrame.from_dict(idx_tweet_geo_dict, orient='index')
    #
    # print('Write out df_tweet_geo')
    # df_tweet_geo.to_csv('/home/cdsw/Coursework_2_Twitter/data/tweet_geo_.csv', index=False)


if __name__ == '__main__':
    main()
