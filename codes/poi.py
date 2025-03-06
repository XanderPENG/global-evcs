"""
Author: Xander Peng
Date: 2024/7/26
Description: Run this script to analyze and output the POI stats of EVCS in these 3 study areas entirely,
which can be modified according to the specific required analysis.
"""
import os

from codes.utils.tools.io_tool import load_preprocessed_evcs
import codes.utils.tools.poi_tool as poi_tool
import codes.preprocessing.poi_classification_tools as pct
import pandas as pd
import geopandas as gpd

buffer_dis_list = [300, 800, 1000]
buffer_root_dir = r'../data/interim/evcs_buffers//'
classified_poi_dir = pct.POI_OUPUT_DIR + '//'
result_root_dir = r'../data/output/texts/poi//'
''' China '''
# region_name = 'china'
# evcs_cn = load_preprocessed_evcs(region_name)
# evcs_shp_dir = r'../data/input/evcs_shp//china//'
# china_prov_folder_list = os.listdir(pct.POI_OUPUT_DIR + 'china//')
#
# for buff_dist in buffer_dis_list:
#     ''' read the buffer shp '''
#     current_buffer = gpd.read_file(buffer_root_dir + 'china//' + str(buff_dist) + 'buffer.shp')
#     province_list: list = evcs_cn['province'].drop_duplicates().to_list()  # All provinces
#     poi2cs = pd.DataFrame()
#
#     ''' Calculate the poi mix '''
#     for p in evcs_cn['province'].drop_duplicates().to_list():
#         poi_cs_slice = poi_tool.cal_poi(region=region_name,
#                                         state_kw=p,
#                                         country_kw=None,
#
#                                         cs_buffer=current_buffer,
#                                         cs_kw_field='province',
#                                         cs_buffer_name='name',
#
#                                         poi_root_dir=classified_poi_dir+'china//',
#                                         poi_df_lon='wgs84_lon',
#                                         poi_df_lat='wgs84_lat',
#
#                                         join_gdf_idx='name_left',
#                                         eu_country_dict=None
#                                         )
#
#         poi2cs = pd.concat([poi2cs, poi_cs_slice])
#
#     ''' Output '''
#     poi2cs.to_csv(result_root_dir + region_name + '//' + str(buff_dist) + 'dist.csv.gz')

''' USA '''
# evcs_us = load_preprocessed_evcs('usa',
#                                  usecols=['Station Name', 'City', 'State', 'Latitude', 'Longitude'],
#                                  index_col=0
#                                   )
# # Sjoin the evcs with the state-level boundary
# evcs_us = gpd.GeoDataFrame(evcs_us,
#                             geometry=gpd.points_from_xy(evcs_us['Longitude'], evcs_us['Latitude']),
#                             crs='EPSG:4326'
#                             )
# evcs_us = gpd.sjoin(evcs_us,
#                     gpd.read_file(r'../data/input/boundary/usa/gadm41_USA_1.shp')[['NAME_1', 'geometry']],
#                     how='left',
#                     predicate='within')
#
# region_name = 'usa'
# for buff_dist in buffer_dis_list:
#     ''' Create or read the buffer shp '''
#     current_buffer = gpd.read_file(buffer_root_dir + 'usa//' + str(buff_dist) + 'buffer.shp')
#
#     # Sjoin the current buffer with the city-level boundary
#     current_buffer = gpd.sjoin(current_buffer,
#                                gpd.read_file(r'../data/input/boundary/usa/gadm41_USA_2.shp')[['NAME_1', 'NAME_2', 'geometry']],
#                                how='left',
#                                predicate='within')
#
#     state_list: list = evcs_us['NAME_1'].dropna().drop_duplicates().to_list()  # All countries
#     poi2cs = pd.DataFrame()
#
#     ''' Calculate the poi mix '''
#     for p in state_list:
#         print('Start: ', p)
#         poi_cs_slice = poi_tool.cal_poi(region=region_name,
#                                         state_kw=p,  # not important in eu scenario
#                                         country_kw=None,
#
#                                         cs_buffer=current_buffer,
#                                         cs_kw_field='NAME_1',
#                                         cs_buffer_name='Station Na',
#
#                                         poi_root_dir=classified_poi_dir + region_name,
#                                         poi_df_lon='lon',
#                                         poi_df_lat='lat',
#
#                                         join_gdf_idx='Station Na',
#                                         #    eu_country_dict=eu_country_dict
#                                         )
#
#         poi2cs = pd.concat([poi2cs, poi_cs_slice])
#
#     ''' Output '''
#     poi2cs.to_csv(result_root_dir + region_name + '//' + str(buff_dist) + 'dist.csv.gz')

""" EU """
evcs_eu = load_preprocessed_evcs('europe',
                                 usecols=['location_unique_id', 'location_country', 'Latitude', 'Longitude',
                                          'COUNTRY'])
# evcs_eu = pd.read_csv(r'../data/interim/cleaned_evcs/europe_evcs4plot.csv.csv',
#                       usecols=['value', 'location_unique_id',
#                                'location_country', 'location_lng', 'location_lat',
#                                'COUNTRY', 'NAME_1', 'NAME_2']
#                       )
eu_country_dict = poi_tool.country_full_name(eu_cs_df=evcs_eu)
eu_country_dict.update({'GB': 'great-britain',
                        'NL': 'Netherlands',
                        'CZ': 'czech-republic',
                        'MK': 'Macedonia',
                        'MD': 'Moldova',
                        'EL': 'Greece'
                        })

region_name = 'europe'

for buff_dist in buffer_dis_list:
    ''' Load the buffer shp '''
    current_buffer = gpd.read_file(buffer_root_dir + 'europe//' + str(buff_dist) + 'buffer.shp')
    country_list: list = evcs_eu['location_country'].drop_duplicates().to_list()  # All countries abr
    poi2cs = pd.DataFrame()

    ''' Calculate the poi mix '''
    for p in country_list:  # p is country abr
        print('Start: ', p)
        poi_cs_slice = poi_tool.cal_poi(region=region_name,
                                        state_kw=None,  # not important in eu scenario
                                        country_kw=p,

                                        cs_buffer=current_buffer,
                                        cs_kw_field='location_c',
                                        cs_buffer_name='location_u',

                                        poi_root_dir=classified_poi_dir + region_name,
                                        poi_df_lon='lon',
                                        poi_df_lat='lat',

                                        join_gdf_idx='location_u',
                                        eu_country_dict=eu_country_dict
                                        )

        poi2cs = pd.concat([poi2cs, poi_cs_slice])

    ''' Output '''
    poi2cs.to_csv(result_root_dir + region_name + '//' + str(buff_dist) + 'dist.csv.gz')
