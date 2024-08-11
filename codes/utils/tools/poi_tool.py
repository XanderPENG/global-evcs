"""
Author: Xander Peng
Date: 2024/8/8
Description: 
"""
import difflib
import os
import numpy as np
import pandas as pd
import geopandas as gpd
import arcpy
import requests
from bs4 import BeautifulSoup as bs


def create_buffer(
        input_shp: str,  # the dir of input shp
        output_dir: str,  # The dir of output buffer
        distance: int or float,  # unit: meters
        cs_points_df=None,
        lon_col=None,
        lat_col=None,
        points_usecols=None,
        buffer_usecols=None,
):
    """
    Create buffer for the cs points using arcpy; which can be modified to use geopandas.
    :param input_shp:
    :param output_dir:
    :param distance:
    :param cs_points_df:
    :param lon_col:
    :param lat_col:
    :param points_usecols:
    :param buffer_usecols:
    :return:
    """
    ''' Check if there is the cs points shp'''
    if os.path.exists(input_shp):
        cs_points_gdf = gpd.read_file(input_shp)
    else:  # Create cs points shp
        assert cs_points_df is not None, f'Specify the cs_points_df!'

        cs_points_gdf = gpd.GeoDataFrame(cs_points_df,
                                         geometry=gpd.points_from_xy(cs_points_df[lon_col],
                                                                     cs_points_df[lat_col]),
                                         crs='EPSG:4326')
        cs_points_gdf.to_file(input_shp, encoding='utf-8')

    if os.path.exists(output_dir + '\\' + str(distance) + 'buffer.shp'):
        cs_buffers = gpd.read_file(output_dir + '\\' + str(distance) + 'buffer.shp')
    else:
        ''' Create buffer '''
        points_feature = input_shp
        buffer_feature = output_dir + '\\' + str(
            distance) + 'buffer'  # No file type (e.g., only \\buffer, instead of \\buffer.shp)
        arcpy.gapro.CreateBuffers(points_feature, buffer_feature, "GEODESIC", 'DISTANCE', None,
                                  str(distance) + ' Meters')

        ''' Correct the field '''
        cs_buffer = gpd.read_file(output_dir + '\\' + str(distance) + 'buffer.shp')  # Read arcpy shp

        cs_buffers = cs_points_gdf[points_usecols].merge(cs_buffer[buffer_usecols],
                                                         how='left',
                                                         left_index=True,
                                                         right_index=True)
        cs_buffers = gpd.GeoDataFrame(cs_buffers, geometry=cs_buffers['geometry'])

        cs_buffers.to_file(output_dir + '\\' + str(distance) + 'buffer.shp')
    return cs_buffers


def cal_poi(
        state_kw: str or None,  # State kew word
        country_kw: str or None,  # country key word
        cs_buffer: gpd.GeoDataFrame,
        cs_kw_field: str,  # The field name of country or state
        poi_root_dir: str,
        poi_df_lon: str,  # The field name of lon in poi_df
        poi_df_lat: str,
        join_gdf_idx: str,  # The field of cs name in sjoin gdf
        cs_buffer_name: str,  # The field cs name in cs_buffer
        region=None,
        eu_country_dict: dict = None,
):
    ''' configuration '''
    if region == 'cn' and join_gdf_idx is None:
        join_gdf_idx = 'name_left'

    def filter_folder(kw: str,
                      dir: str):

        folders = os.listdir(dir)  # all folder name
        results = [(string_similar(kw, f), f) for f in folders]
        result_list = list(filter(lambda x: x[0] == max([i[0] for i in results]), results))
        if len(result_list) > 1 or len(result_list) == 0:
            print(results)
            print(state_kw)
            print(result_list)
            result = input('Incorrect result in the list, plz specify the correct one!')
        else:
            result = result_list[0][1]
            print(result)
        return result

    ''' Specify the poi file dir '''
    if region in ['usa', 'cn']:  # not eu
        state_fname = filter_folder(state_kw, poi_root_dir)  # Get exact folder name of this state
        target_dir = poi_root_dir + '\\' + state_fname


    else:  # eu
        state_fname = filter_folder(eu_country_dict.get(country_kw), poi_root_dir)
        # if country_fname in ['france', 'germany', 'great-britain', 'italy', 'netherlands', 'poland', 'russia', 'spain']:
        #     state_fname = filter_folder(state_kw, poi_root_dir + '\\' + country_fname)
        #     target_dir = poi_root_dir + '\\' + country_fname + '\\' + state_fname
        # else:
        target_dir = poi_root_dir + '\\' + state_fname

    ''' Merge 3 types poi data for eu and usa '''
    if region in ['usa', 'eu'] and state_fname not in ['france', 'germany', 'great-britain', 'italy', 'netherlands',
                                                         'poland', 'russia', 'spain']:
        poi_df = pd.DataFrame()
        for f in os.listdir(target_dir):
            df = pd.read_csv(target_dir + '\\' + f)
            df['category'] = f.replace('.csv', '') if 'ltf' not in f else 'lt'
            poi_df = pd.concat([poi_df, df])
    else:
        poi_df = pd.read_csv(target_dir + '\\' + 'total_poi.csv')

    ''' Spatial join '''
    # Filter a slice of cs correcponding to the state or country kw
    # if region == 'eu' and country_fname in ['france', 'germany', 'great-britain', 'italy', 'netherlands', 'poland', 'russia', 'spain']:
    #     slice_cs: gpd.GeoDataFrame = cs_buffer.query(cs_kw_field + " == @state_fname")
    if region == 'eu':
        # and country_fname not in ['france', 'germany', 'great-britain', 'italy', 'netherlands', 'poland', 'russia', 'spain']:
        slice_cs: gpd.GeoDataFrame = cs_buffer.query(cs_kw_field + " == @country_kw")
    else:
        slice_cs: gpd.GeoDataFrame = cs_buffer.query(cs_kw_field + " == @state_kw")

    # Convert poi_df into gdf
    poi_gdf = gpd.GeoDataFrame(poi_df, geometry=gpd.points_from_xy(poi_df[poi_df_lon], poi_df[poi_df_lat]),
                               crs='EPSG:4326')

    # sjoin
    cs2poi = gpd.sjoin(slice_cs, poi_gdf, how='inner', predicate='contains')

    ''' Count 3 types poi number '''
    # Pivot Table
    pt = pd.pivot_table(cs2poi,
                        index=[join_gdf_idx],
                        values=['geometry'],
                        aggfunc='count',
                        columns=['category'],
                        fill_value=0
                        )
    pt.columns = pt.columns.droplevel()

    # Merge the number to sliced cs_buffer
    slice_cs = slice_cs.merge(pt, how='left', left_on=cs_buffer_name, right_on=join_gdf_idx)
    # return pt, slice_cs
    ''' Calculate '''
    # Ratio
    slice_cs.fillna(0, inplace=True)
    slice_cs['adm_r'] = slice_cs['adm'] / (slice_cs['adm'] + slice_cs['com'] + slice_cs['lt'])
    slice_cs['com_r'] = slice_cs['com'] / (slice_cs['adm'] + slice_cs['com'] + slice_cs['lt'])
    slice_cs['lt_r'] = slice_cs['lt'] / (slice_cs['adm'] + slice_cs['com'] + slice_cs['lt'])

    # Mix
    slice_cs['Mix'] = -1 * np.sum(
        [np.log(slice_cs[col].to_numpy() + 1e-5) * (slice_cs[col].to_numpy() + 1e-5) / np.log(3) for col in
         ['adm_r', 'com_r', 'lt_r']], axis=0)

    return slice_cs


def string_similar(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()


def country_full_name(eu_cs_df,
                      ):
    # Get country acronym in cs df
    eu_country_list = eu_cs_df['location_country'].drop_duplicates().to_list()
    url = 'https://www.iban.com/country-codes'
    code_resource = requests.get(url).text
    results = bs(code_resource, 'html.parser')
    world_countries = results.find('tbody').findAll('tr')
    world_state_dict = {list(filter(lambda td: len(td.text) == 2 and not td.text.isdigit(), item.findAll('td')))[0].text:
                        list(filter(lambda td: len(td.text) > 3 and not td.text.isdigit(), item.findAll('td')))[0].text
                        for item in world_countries}
    eu_country_dict = {c: world_state_dict.get(c) for c in eu_country_list}
    return eu_country_dict

