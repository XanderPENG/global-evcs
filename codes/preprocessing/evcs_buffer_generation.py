"""
Author: Xander Peng
Date: 2025/3/1
Description: This script is used to generate the EVCS buffer for the cleaned EVCS data, using ArcPy.
"""
import os

import arcpy
import geopandas as gpd
import pandas as pd

from codes.utils.tools.io_tool import load_preprocessed_evcs


def create_evcs_shp(df: pd.DataFrame,
                    lng_col: str,
                    lat_col: str,
                    output_dir: str, ):
    evcs_gdf = gpd.GeoDataFrame(df,
                                geometry=gpd.points_from_xy(df[lng_col], df[lat_col]),
                                crs='EPSG:4326')
    evcs_gdf.to_file(output_dir, encoding='utf-8',
                     driver='ESRI Shapefile'
                     )


def create_or_read_evcs_buffer(
        input_shp: str,  # the dir of input shp
        output_dir: str,  # The dir of output buffer
        distance: int or float,  # unit: meters
        cs_points_df=None,
        lon_col=None,
        lat_col=None,
        points_usecols=None,
        buffer_usecols=None,
        points_merge_on=None,
        buffer_merge_on=None,
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
    # if os.path.exists(input_shp):
    #     # cs_points_gdf = gpd.read_file(input_shp)
    #     pass
    # else:  # Create cs points shp
    #     assert cs_points_df is not None, f'Specify the cs_points_df!'

    cs_points_gdf = gpd.GeoDataFrame(cs_points_df,
                                     geometry=gpd.points_from_xy(cs_points_df[lon_col],
                                                                 cs_points_df[lat_col]),
                                     crs='EPSG:4326')
    cs_points_gdf.to_file(input_shp, encoding='utf-8')

    if os.path.exists(output_dir + '//' + str(distance) + 'buffer.shp'):
        cs_buffers = gpd.read_file(output_dir + '//' + str(distance) + 'buffer.shp')
    else:
        ''' Create buffer '''
        points_feature = input_shp
        buffer_feature = output_dir + '//' + str(
            distance) + 'buffer'  # No file type (e.g., only \\buffer, instead of \\buffer.shp)
        arcpy.gapro.CreateBuffers(points_feature, buffer_feature, "GEODESIC", 'DISTANCE', None,
                                  str(distance) + ' Meters')

        ''' Correct the field '''
        cs_buffer = gpd.read_file(output_dir + '//' + str(distance) + 'buffer.shp')  # Read arcpy shp

        cs_buffers = cs_points_gdf[points_usecols].merge(cs_buffer[buffer_usecols],
                                                         how='left',
                                                         left_on=points_merge_on,
                                                         right_on=buffer_merge_on
                                                         )
        cs_buffers = gpd.GeoDataFrame(cs_buffers, geometry=cs_buffers['geometry'])

        cs_buffers.to_file(output_dir + '\\' + str(distance) + 'buffer.shp', encoding='utf-8')
    return cs_buffers


if __name__ == '__main__':
    ''' Read the cleaned EVCS data '''
    cleaned_cn_evcs = load_preprocessed_evcs(region='china')
    cleaned_usa_evcs = load_preprocessed_evcs(region='usa',
                                              usecols=['Station Name', 'City', 'State', 'Latitude', 'Longitude'],
                                              index_col=0
                                              )
    cleaned_eu_evcs = load_preprocessed_evcs('europe',
                                             usecols=['location_unique_id', 'location_country', 'Latitude', 'Longitude',
                                                      'COUNTRY'], )

    # ''' Create ShapeFile for each region '''
    # create_evcs_shp(cleaned_cn_evcs, 'wgs84_lng', 'wgs84_lat', r'../data/input/evcs_shp/china/clean_china.shp')
    # create_evcs_shp(cleaned_usa_evcs, 'Longitude', 'Latitude', r'../data/input/evcs_shp/usa/clean_usa.shp')
    # create_evcs_shp(cleaned_eu_evcs, 'Longitude', 'Latitude', r'../data/input/evcs_shp/europe/clean_europe.shp')

    arcpy.env.workspace = r'H:\gitRepo\global-evcs-2024\codes\\'
    ''' Create buffer for each region '''
    for buffer_dist in [300, 800, 1000]:
        # China
        create_or_read_evcs_buffer(input_shp=os.path.abspath(r'../data/input/evcs_shp/china/clean_china.shp'),
                                   # must be absolute path
                                   output_dir=os.path.abspath(r'../data/interim/evcs_buffers/china'),
                                   distance=buffer_dist,
                                   cs_points_df=cleaned_cn_evcs,
                                   lon_col='wgs84_lng',
                                   lat_col='wgs84_lat',
                                   points_usecols=['name', 'province', 'city', 'ad', 'Unnamed: 0'],
                                   buffer_usecols=['wgs84_lng', 'wgs84_lat', 'geometry', 'Unnamed_ 0'],
                                   points_merge_on=['Unnamed: 0'],
                                   buffer_merge_on=['Unnamed_ 0']
                                   )
        # USA
        create_or_read_evcs_buffer(input_shp=os.path.abspath(r'../data/input/evcs_shp/usa/clean_usa.shp'),
                                   output_dir=os.path.abspath(r'../data/interim/evcs_buffers/usa'),
                                   distance=buffer_dist,
                                   cs_points_df=cleaned_usa_evcs,
                                   lon_col='Longitude',
                                   lat_col='Latitude',
                                   points_usecols=['Station Name', 'City', 'State'],
                                   buffer_usecols=['Longitude', 'Latitude', 'geometry', 'Station Na', 'City', 'State'],
                                   points_merge_on=['Station Name', 'City', 'State'],
                                   buffer_merge_on=['Station Na', 'City', 'State']
                                   )
        # Europe
        create_or_read_evcs_buffer(input_shp=os.path.abspath(r'../data/input/evcs_shp/europe/clean_europe.shp'),
                                   output_dir=os.path.abspath(r'../data/interim/evcs_buffers/europe'),
                                   distance=buffer_dist,
                                   cs_points_df=cleaned_eu_evcs,
                                   lon_col='Longitude',
                                   lat_col='Latitude',
                                   points_usecols=['location_unique_id', 'location_country', 'COUNTRY'],
                                   buffer_usecols=['Longitude', 'Latitude', 'geometry', 'location_u'],
                                   points_merge_on=['location_unique_id'],
                                   buffer_merge_on=['location_u']
                                   )
