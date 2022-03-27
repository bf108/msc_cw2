import pandas as pd
from zipfile import ZipFile
import geopandas as geopd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from src.geo_etl.helper_functions import check_country_in_eur_bbox

############################################################################################################
# Import Geo Data
# Geometry - geopandas
# Citydata - simplemaps
############################################################################################################

#Read in zipfile with long-lat of cities in the world
zf = ZipFile('/home/cdsw/Coursework_2_Twitter/data/simplemaps_worldcities_basicv1.75.zip')
cities = pd.read_csv(zf.open('worldcities.csv'), usecols=['city','lat','lng','country','capital'])

#Get geopandas data for world
gdf = geopd.read_file(geopd.datasets.get_path('naturalearth_lowres'))

#Join city data to gpd
gdf_wit_city_data = pd.merge(gdf[['name','geometry']], cities, left_on='name', right_on='country', how='inner')
gdf_wit_city_data = gdf_wit_city_data.drop(columns=['name']).rename(columns={'geometry':'country_geometry'})

#Limit geopandas data to our EUR bounding box
gdf_wit_city_data['in_EUR_box'] = gdf_wit_city_data.apply(lambda x: check_country_in_eur_bbox(x), axis=1)
df_eur = gdf_wit_city_data[gdf_wit_city_data['in_EUR_box'] == True]

#Find capital cities
df_eur_capital = df_eur[df_eur['capital'] == 'primary']
gdf_eur_capital = geopd.GeoDataFrame(
    df_eur_capital, geometry=geopd.points_from_xy(df_eur_capital.lng, df_eur_capital.lat))

missed_cities = ['Belfast', 'Cagliari', 'Edinburgh', 'Palma', 'Rijeka', 'Tangier', 'İzmir']

############################################################################################################
# Plot EUR with Capitals which will be used to map tweets to countries
############################################################################################################

fig, ax = plt.subplots(figsize=(20, 10))
gdf.boundary.plot(ax=ax, edgecolor='k', facecolor='green', alpha=0.2)  # color='white',
ax.set_xlim(-24.5, 69.1);
ax.set_ylim(34.8, 81.9)
ax.set_xlabel('Longitude', fontdict={'size': 20})
ax.set_ylabel('Latitude', fontdict={'size': 20})
ax.set_title('Bounding Box for Europe: lng (-24.5, 69.1) lat (34.8, 81.9)'
             '\nCapital Cities labelled'
             , fontdict={'size': 20})
ax.tick_params(axis='both', which='major', labelsize=15)

# Annotate capital city
for x, y, label in zip(gdf_eur_capital.lng, gdf_eur_capital.lat, gdf_eur_capital.city):
    if label in ['Amsterdam', 'Vienna', 'Rijeka', 'Ljubljana', 'Podgorica', 'Pristina']:
        pass
    else:
        ax.annotate(label, xy=(x, y), fontsize=11, weight='bold', color='k')

# Annotate missed cities
for x, y, label in zip(missed_cities.lng, missed_cities.lat, missed_cities.city):
    if label in ['Amsterdam', 'Vienna', 'Rijeka', 'Ljubljana', 'Podgorica', 'Pristina']:
        pass
    else:
        ax.annotate(label, xy=(x, y), fontsize=11, weight='bold', color='k')

#Sort out clashes with capitals
ax.annotate('Vienna', xy=(13, 48), fontsize=11, weight='bold', color='k')
ax.annotate('Sarajevo', xy=(17, 44), fontsize=11, weight='bold', color='k')
ax.annotate('Ljubljana', xy=(12, 46), fontsize=11, weight='bold', color='k')

plt.tight_layout();
fig.savefig('../static/bounding_box_eur_cities.png');


############################################################################################################
# Plot GPS Tweets in EUR
############################################################################################################

#Read in necessary data
df_geo = pd.read_csv('/home/cdsw/Coursework_2_Twitter/data/tweet_geo_.csv', usecols=['tweet_id', 'point', 'country'])
df_diag = pd.read_csv('/home/cdsw/Coursework_2_Twitter/msc_cw2/tweets_diag_bbox.csv')
df_t = pd.read_csv('/home/cdsw/Coursework_2_Twitter/data/preprocessed_tweets.csv',
                   usecols=['longitude', 'latitude', 'tweet_id'])
df_comb = pd.concat([df_t[['longitude', 'latitude']], df_geo], axis=1)
# Get Point Geometry for all tweets
pnts = geopd.GeoSeries.from_wkt(df_comb[~df_comb['longitude'].isna()]['point'])

fig, ax = plt.subplots(figsize=(20, 10))
# ax.set_facecolor('blue')
gdf.boundary.plot(ax=ax, edgecolor='k', facecolor='green', alpha=0.15)  # color='white',
pnts.plot(ax=ax, color='r', markersize=0.1)
ax.set_xlim(-10, 50)
ax.set_ylim(32.5, 65)
ax.set_xlabel('Longitude', fontdict={'size': 20, 'weight': 'bold'})
ax.set_ylabel('Latitude', fontdict={'size': 20, 'weight': 'bold'})
ax.set_title('800K tweets with GPS in Europe June 2021', fontdict={'size': 20, 'weight': 'bold'})
ax.tick_params(axis='both', which='major', labelsize=15)

# Annotate capital city
for x, y, label in zip(gdf_eur_capital.lng, gdf_eur_capital.lat, gdf_eur_capital.city):
    if label in ['Amsterdam', 'Vienna', 'Rijeka', 'Ljubljana', 'Podgorica', 'Pristina']:
        pass
    else:
        ax.annotate(label, xy=(x, y), fontsize=11, weight='bold', color='k')

# Annotate missed cities
for x, y, label in zip(missed_cities.lng, missed_cities.lat, missed_cities.city):
    if label in ['Amsterdam', 'Vienna', 'Rijeka', 'Ljubljana', 'Podgorica', 'Pristina']:
        pass
    else:
        ax.annotate(label, xy=(x, y), fontsize=11, weight='bold', color='k')

ax.annotate('Vienna', xy=(13, 48), fontsize=11, weight='bold', color='k')
ax.annotate('Sarajevo', xy=(17, 44), fontsize=11, weight='bold', color='k')
ax.annotate('Ljubljana', xy=(12, 46), fontsize=11, weight='bold', color='k')

red_dot = mlines.Line2D([], [], color='red', marker='o', markersize=0.5, linestyle='None', label='Single Tweet')
ax.legend(handles=[red_dot], fontsize=16, facecolor='white', loc=1);

plt.tight_layout();
fig.savefig('../static/bounding_box_eur_cities_aoi_tweets.png');

############################################################################################################
# Plot Heat Map of Tweets in EUR
############################################################################################################

GPS_tweets_per_country = df_comb.groupby('country').count()[['longitude']] \
    .sort_values(by='longitude', ascending=False) \
    .reset_index() \
    .rename(columns={'country': 'name', 'longitude': 'gps_tweet_counts'})

gdf_ = pd.merge(gdf, GPS_tweets_per_country, how='outer', on='name')

#Get centroid of country to place Country Label
gdf_['centroid'] = gdf_[~gdf_['gps_tweet_counts'].isna()][['name', 'geometry']].drop_duplicates(subset='name')[
    'geometry'].centroid
country_centroid_lng_lat = [(sh.x, sh.y) for sh in gdf_[gdf_['centroid'] != None]['centroid'].values]
country_lab = [lab for lab in gdf_[gdf_['centroid'] != None]['name'].values]

fig, ax = plt.subplots(figsize=(20, 10))
gdf.boundary.plot(ax=ax, edgecolor='k', facecolor='green', alpha=0.15)  # color='white',
gdf_.plot('gps_tweet_counts', ax=ax, legend=True,
          legend_kwds={'label': 'Number of GPS Tweets June 2021'}, cmap='Wistia')
ax.set_xlim(-10, 50)
ax.set_ylim(32.5, 65)
ax.set_xlabel('Longitude', fontdict={'size': 20, 'weight': 'bold'})
ax.set_ylabel('Latitude', fontdict={'size': 20, 'weight': 'bold'})
ax.set_title('Tweets with GPS recorded in Europe Aggregated to Country\n', fontdict={'size': 20, 'weight': 'bold'})
ax.tick_params(axis='both', which='major', labelsize=15)

for xy, label in zip(country_centroid_lng_lat, country_lab):
    if label == 'France':
        pass
    else:
        ax.annotate(label, xy=(xy[0], xy[1]), fontsize=13, weight='bold', color='k')

#Some centroids are in locations outside of map. So manually place them
ax.annotate('France', xy=(2, 46), fontsize=13, weight='bold', color='k')
ax.annotate('Morocco', xy=(-8, 34), fontsize=13, weight='bold', color='k')
ax.annotate('Algeria', xy=(2, 34), fontsize=13, weight='bold', color='k')
ax.annotate('Russia', xy=(40, 55), fontsize=13, weight='bold', color='k')
ax.annotate('Norway', xy=(6, 60), fontsize=13, weight='bold', color='k')

cb_ax = fig.axes[1]
cb_ax.set_ylabel('\nGPS Tweet Count (000\'s)', fontdict={'size': 20, 'weight': 'bold'})
cb_ax.tick_params(axis='both', which='major', labelsize=15)
colour_bar_y_ticks_labels = [l.get_text() for l in cb_ax.get_yticklabels()]
cb_ax.set_yticklabels([int(y) // 1000 for y in colour_bar_y_ticks_labels]);

fig.savefig('../static/bounding_box_eur_heatmap.png');