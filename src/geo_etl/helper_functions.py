import pandas as pd
import numpy as np
from tqdm import tqdm
import requests
import math
from zipfile import ZipFile
import geopandas as geopd
from scipy.spatial import distance
from shapely.geometry import Point


def find_centroid(array_min_lng, array_max_lng, array_min_lat, array_max_lat):
    lng = array_min_lng + (array_max_lng - array_min_lng) / 2
    lat = array_min_lat + (array_max_lat - array_min_lat) / 2

    return np.array((lng, lat)).T


def edges_leading_diaganol(array_min_lng, array_max_lng, array_min_lat, array_max_lat):
    blhc = np.array((array_min_lng, array_min_lat)).T
    trhc = np.array((array_max_lng, array_max_lat)).T

    return blhc, trhc


def leading_diag_len(df):
    cols = ['place_longitude_1', 'place_longitude_2', 'place_latitude_1', 'place_latitude_2']

    #Check all necessary columns present
    for c in cols:
        if c not in df.columns:
            raise ValueError(f'{c} not in DataFrame columns')

    #Get edges of box
    edges_bbox = edges_leading_diaganol(*[df[c].values for c in cols])

    #Create array of diagonal
    diagonal = []
    for blhc, trhc in zip(edges_bbox[0], edges_bbox[1]):
        try:
            ans = abs(np.linalg.norm(trhc - blhc))
        except:
            ans = np.nan

        diagonal.append(ans)

    df_diagonal = pd.DataFrame(diagonal, columns=['diagonal'])

    return df_diagonal


def calc_centroid_diag_bbox(df):
    cols = ['place_longitude_1', 'place_longitude_2', 'place_latitude_1', 'place_latitude_2']
    centroid_loc_bbox = find_centroid(*[df[c].values for c in cols])
    df_loc_lat_centroid = pd.DataFrame(centroid_loc_bbox, columns=['loc_centroid_lng', 'loc_centroid_lat'])

    df_diagonal = leading_diag_len(df)

    df = pd.concat([df, df_loc_lat_centroid, df_diagonal], axis=1)

    final_lng = []
    for tup in tqdm(df[['longitude', 'loc_centroid_lng']].values):
        if math.isnan(tup[0]):
            final_lng.append(tup[1])
        else:
            final_lng.append(tup[0])

    final_lat = []
    for tup in tqdm(df[['latitude', 'loc_centroid_lat']].values):
        if math.isnan(tup[0]):
            final_lat.append(tup[1])
        else:
            final_lat.append(tup[0])

    # Add lng and lat columns to data taking GPRS tweet loc first, else centroid of location bbox
    df['fin_lng'] = final_lng
    df['fin_lat'] = final_lat

    df_tweets = df[['tweet_id', 'diagonal', 'fin_lng', 'fin_lat']].copy(deep=True)

    return df_tweets


# This data is for the entire world, lets limit it to our bounding box for EUROPE
def check_country_in_eur_bbox(row):
    long_min = -24.5
    long_max = 69.1
    lat_min = 34.8
    lat_max = 81.9

    if (((row['lng'] >= long_min) and (row['lng'] <= long_max))
            and
            ((row['lat'] >= lat_min) and (row['lat'] <= lat_max))):
        return True

    return False


def check_point_in_geom(point, geom):
    return geom.contains(point)