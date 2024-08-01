"""
Author: Xander Peng
Date: 2024/8/1
Description: This module contains path/functions to read and write data.
"""

import pandas as pd
import geopandas as gpd

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
                           ) -> pd.DataFrame:
    """
    Load the preprocessed EVCS data.
    :param region:
    :param output_filename:
    :return:
    """

    assert region in ["china", "usa", "europe"], f'Invalid region name: {region}'

    file_name = ''
    if region == "china":
        file_name = 'cn_evcs_cleaned.csv'
    elif region == "usa":
        file_name = 'us_evcs_cleaned.csv'
    elif region == "europe":
        file_name = 'eu_evcs_cleaned.csv'

    evcs = pd.read_csv(global_input_path + "interim/evcs_dist/" + f"{region}/" + file_name)

    return evcs
