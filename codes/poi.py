"""
Author: Xander Peng
Date: 2024/7/26
Description: Run this script to analyze and output the POI stats of EVCS in these 3 study areas entirely,
which can be modified according to the specific required analysis.
"""
import os

import codes.utils.tools.poi_tool as poi_tool
import codes.preprocessing.poi_classification_tools as pct
import pandas as pd
import geopandas as gpd

buffer_dis_list = [300, 500, 800, 1000, 1500, 2000]
''' China '''
evcs_cn = pd.read_csv(r'../data/interim/cleaned_evcs/china_evcs4plot.csv.csv')
region_name = 'cn'
evcs_shp_dir = r'../data/input/evcs_shp//'
buffer_root_dir = r'../data/interim/evcs_buffers//'
china_prov_folder_list = os.listdir(pct.POI_ROOT_DIR + "china/POI_CityLevel//")
classified_poi_dir = pct.POI_OUPUT_DIR + 'china//'
result_root_dir = r'../data/output/texts/poi//'

for buff_dist in buffer_dis_list:
    ''' Create or read the buffer shp '''
    current_buffer: gpd.GeoDataFrame = poi_tool.create_buffer(input_shp=evcs_shp_dir + '\\' + region_name + '_cs.shp',
                                                              output_dir=buffer_root_dir + '\\' + region_name,
                                                              distance=buff_dist,
                                                              cs_points_df=evcs_cn.copy(),
                                                              lon_col='wgs84_lon',
                                                              lat_col='wgs84_lat',
                                                              points_usecols=['name', 'pname', 'cityname'],
                                                              buffer_usecols=['wgs84_lon', 'wgs84_lat', 'geometry']
                                                              )
    province_list: list = evcs_cn['pname'].drop_duplicates().to_list()  # All provinces
    poi2cs = pd.DataFrame()

    ''' Calculate the poi mix '''
    for p in china_prov_folder_list:
        poi_cs_slice = poi_tool.cal_poi(region=region_name,
                                        state_kw=p,
                                        country_kw=None,

                                        cs_buffer=current_buffer,
                                        cs_kw_field='pname',
                                        cs_buffer_name='name',

                                        poi_root_dir=classified_poi_dir + '\\' + region_name,
                                        poi_df_lon='wgs84_lon',
                                        poi_df_lat='wgs84_lat',

                                        join_gdf_idx='name_left',
                                        eu_country_dict=None
                                        )

        poi2cs = pd.concat([poi2cs, poi_cs_slice])

    ''' Output '''
    poi2cs.to_csv(result_root_dir + '\\' + region_name + '\\' + region_name + '_' + str(buff_dist) + 'dist.csv')

''' USA '''
evcs_us = pd.read_csv(r'../data/interim/cleaned_evcs/usa_evcs4plot.csv.csv')
region_name = 'us'
for buff_dist in buffer_dis_list:
    ''' Create or read the buffer shp '''
    current_buffer: gpd.GeoDataFrame = poi_tool.create_buffer(input_shp=evcs_shp_dir + '\\' + region_name + '_cs.shp',
                                                              output_dir=buffer_root_dir + '\\' + region_name,
                                                              distance=buff_dist,
                                                              cs_points_df=evcs_us.copy(),  # modify here
                                                              lon_col='lon',
                                                              lat_col='lat',
                                                              points_usecols=['name', 'NAME_1', 'NAME_2'],
                                                              buffer_usecols=['lon', 'lat', 'geometry']
                                                              )
    state_list: list = evcs_us['NAME_1'].drop_duplicates().to_list()  # All countries
    poi2cs = pd.DataFrame()

    ''' Calculate the poi mix '''
    for p in state_list:
        poi_cs_slice = poi_tool.cal_poi(region=region_name,
                                        state_kw=p,  # not important in eu scenario
                                        country_kw=None,

                                        cs_buffer=current_buffer,
                                        cs_kw_field='NAME_1',
                                        cs_buffer_name='name',

                                        poi_root_dir=classified_poi_dir + '\\' + region_name,
                                        poi_df_lon='lon',
                                        poi_df_lat='lat',

                                        join_gdf_idx='name',
                                        #    eu_country_dict=eu_country_dict
                                        )

        poi2cs = pd.concat([poi2cs, poi_cs_slice])

    ''' Output '''
    poi2cs.to_csv(result_root_dir + '\\' + region_name + '\\' + region_name + '_' + str(buff_dist) + 'dist.csv')

""" EU """
evcs_eu = pd.read_csv(r'../data/interim/cleaned_evcs/europe_evcs4plot.csv.csv',
                      usecols=['value', 'location_unique_id',
                               'location_country', 'location_lng', 'location_lat',
                               'COUNTRY', 'NAME_1', 'NAME_2']
                      )
eu_country_dict = poi_tool.country_full_name(eu_cs_df=evcs_eu)
eu_country_dict.update({'GB': 'great-britain',
                        'NL': 'Netherlands',
                        'CZ': 'czech-republic',
                        'MK': 'Macedonia',
                        'MD': 'Moldova'
                        })

region_name = 'eu'
# for buff_dist in [300, 500, 800, 1000, 1500, 2000]:
for buff_dist in buffer_dis_list:
    ''' Load the buffer shp '''
    current_buffer = poi_tool.create_buffer(input_shp=evcs_shp_dir + '\\' + region_name + '_cs.shp',
                                            output_dir=buffer_root_dir + '\\' + region_name,
                                            distance=buff_dist,
                                            cs_points_df=evcs_eu.copy(),
                                            lon_col='location_lng',
                                            lat_col='location_lat',
                                            points_usecols=['location_unique_id', 'location_country', 'NAME_1',
                                                            'NAME_2'],
                                            buffer_usecols=['location_lng', 'location_lat', 'geometry']
                                            )
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
                                        cs_buffer_name='ORIG_FID',

                                        poi_root_dir=classified_poi_dir + '\\' + region_name,
                                        poi_df_lon='lon',
                                        poi_df_lat='lat',

                                        join_gdf_idx='ORIG_FID',
                                        eu_country_dict=eu_country_dict
                                        )

        poi2cs = pd.concat([poi2cs, poi_cs_slice])

    ''' Output '''
    poi2cs.to_csv(result_root_dir + '\\' + region_name + '\\' + region_name + '_' + str(buff_dist) + 'dist.csv')
