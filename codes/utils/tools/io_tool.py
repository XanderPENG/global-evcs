"""
Author: Xander Peng
Date: 2024/8/1
Description: This module contains path/functions to read and write data.
"""
import os

import pandas as pd
import geopandas as gpd

import codes.preprocessing.tools

global_input_path = r"../data/input/"
global_output_path = r"../data/output/"


def load_boundary(region: str) -> gpd.GeoDataFrame:
    """
    Load the boundary of the specified region.
    """
    # Check if the region is valid, if not, raise an error and remind the user to check the input.
    assert region in ["world", "china", "usa", "europe"]

    if region == "world":
        boundary = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
        return boundary

    # Configure the default file name for the boundary of the specified region.
    file_name = ''

    if region == "china":
        file_name = '2021年国家矢量.shp'
    elif region == "usa":
        file_name = 'gadm41_USA_0.shp'
    elif region == "europe":
        file_name = 'eu_bound.shp'
    else:
        raise ValueError("Invalid region name.")

    boundary = gpd.read_file(global_input_path + "boundary/" + f"{region}/" + file_name)

    return boundary


def load_city_evcs(region: str) -> gpd.GeoDataFrame:
    """
    Load the city-level EVCS distribution data for the sake of city-cluster analysis.
    """
    # Check if the region is valid, if not, raise an error and remind the user to check the input.
    assert region in ["china", "usa", "europe"]

    # Configure the default file name for the boundary of the specified region.
    file_name = ''

    if region == "china":
        file_name = 'cn_css_city.shp'
    elif region == "usa":
        file_name = 'us_css_city.shp'
    elif region == "europe":
        file_name = 'eu_cs_country_V2.shp'
    else:
        raise ValueError("Invalid region name.")

    city_evcs = gpd.read_file(global_input_path + "interim/evcs_dist/" + f"{region}/" + file_name)

    return city_evcs


def load_state_evcs(region: str) -> gpd.GeoDataFrame:
    """
    Load the state-level EVCS distribution data.
    """
    # Check if the region is valid, if not, raise an error and remind the user to check the input.
    assert region in ["china", "usa", "europe"]

    # Configure the default file name for the specified region.
    file_name = ''

    if region == "china":
        file_name = 'cn_cs_ratio.shp'
    elif region == "usa":
        file_name = 'us_cs_ratio.shp'
    elif region == "europe":
        file_name = 'eu_cs_country_V2.shp'
    else:
        raise ValueError("Invalid region name.")

    state_evcs = gpd.read_file(global_input_path + "interim/evcs_dist/" + f"{region}/" + file_name,
                               encoding='utf-8')

    return state_evcs


def load_europe_stat_cities(input_path: str = global_input_path + "interim/support/eu_sample_ratio.xlsx") -> list:
    df = pd.read_excel(input_path, sheet_name="Sheet2")
    city_names: list = df['country_shp_name'].tolist()

    return city_names


def load_raw_evcs(region: str,
                  output_filename: str,
                  ) -> pd.DataFrame:
    """
    Load the raw EVCS/EV charging points data.
    :param region:
    :param output_filename:
    :return:
    """
    assert region in ["china", "usa", "europe"], f'Invalid region name: {region}'

    file_name = ''
    if region == "china":
        file_name = 'cn_evcs.csv'

    pass


def load_preprocessed_evcs(region: str,
                           usecols=None,
                           index_col=None,
                           ) -> pd.DataFrame:
    """
    Load the preprocessed EVCS data.
    :param region:
    :param output_filename:
    :return:
    """

    assert region in ["china", "usa", "europe"], f'Invalid region name: {region}'

    file_name = ''
    if region.lower() == "china":
        file_name = 'clean_china.csv.gz'
    elif region.lower() == "usa":
        file_name = 'clean_usa.csv.gz'
    elif region.lower() == "europe":
        file_name = 'clean_europe.csv.gz'

    evcs = pd.read_csv(r'../data/' + "interim/cleaned_evcs/" + file_name, index_col=index_col)
    if usecols is not None:
        evcs = evcs[usecols]

    return evcs

def load_processed_evcs_fusion_boundary(region: str,
                                        evcs_usecols=None,
                                        evcs_lat_col='wgs84_lat',
                                        evcs_lon_col='wgs84_lng',
                                        boundary_usecols=None,
                                        boundary_level='state',
                                        index_col=None,
                                        ) -> pd.DataFrame:
    assert region.lower() in ["china", "usa", "europe"], f'Invalid region name: {region}'
    file_name = ''
    if region.lower() == "china":
        file_name = 'clean_china.csv.gz'
        if boundary_level == 'state':
            boundary = gpd.read_file(global_input_path + "boundary/" + f"{region}/" + '2021年国家矢量.shp')
        elif boundary_level == 'city':
            boundary = gpd.read_file(global_input_path + "boundary/" + f"{region}/" + '地级.shp')
        else:
            raise ValueError("Invalid boundary level.")

    elif region.lower() == "usa":
        file_name = 'clean_usa.csv.gz'
        if boundary_level == 'state':
            boundary = gpd.read_file(global_input_path + "boundary/" + f"{region}/" + 'gadm41_USA_1.shp')
        elif boundary_level == 'city':
            boundary = gpd.read_file(global_input_path + "boundary/" + f"{region}/" + 'gadm41_USA_2.shp')
        else:
            raise ValueError("Invalid boundary level.")

    elif region.lower() == "europe":
        file_name = 'clean_europe.csv.gz'
        if boundary_level == 'state':
            boundary = codes.preprocessing.tools.load_europe_boundary('state')
        elif boundary_level == 'city':
            boundary = codes.preprocessing.tools.load_europe_boundary('city')
        else:
            raise ValueError("Invalid boundary level.")

    evcs = pd.read_csv(r'../data/' + "interim/cleaned_evcs/" + file_name, index_col=index_col)
    if evcs_usecols is not None:
        evcs = evcs[evcs_usecols]
        evcs_gdf = gpd.GeoDataFrame(evcs, geometry=gpd.points_from_xy(evcs[evcs_lon_col], evcs[evcs_lat_col]))
        if evcs_gdf.crs is None:
            evcs_gdf.crs = "EPSG:4326"

    if boundary_usecols is not None:
        boundary = boundary[boundary_usecols+['geometry']]

    evcs_with_boundary = gpd.sjoin(evcs_gdf, boundary, how='left', predicate='within').drop(columns=['geometry'])
    return evcs_with_boundary

def check_output_dir(output_dir: str):
    """
    Check if the output directory exists, if not, create it.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
