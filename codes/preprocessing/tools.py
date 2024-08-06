"""
Author: Xander Peng
Date: 2024/8/2
Description: 
"""
import os

import pandas as pd
import geopandas as gpd

'''
EVCS raw data directory/path
'''

CN_EVCS_FOLDER_DIR = r"../data/input/raw_data/evcs/China"
EUROPE_EVCS_PATH = r"../data/input/raw_data/evcs/Europe/EU.csv"
USA_EVCS_PATH = r"../data/input/raw_data/evcs/USA/USA.csv"


def load_cn_evcs(evcs_dir: str,
                 usecols=None,
                 ) -> pd.DataFrame:
    """
    Load China EVCS data
    :return: DataFrame
    """
    # List all the files in the directory; format: [(province, filename)]
    provinces = os.listdir(evcs_dir)
    cs_county_list = []
    for p in provinces:
        p_county = os.listdir(evcs_dir + "\\" + str(p))  # All counties.txt in the current province dir
        for c in p_county:
            cs_county_list.append((p, c))

    # Read cs file one by one, according to the @cs_county_list
    all_cs = pd.DataFrame()
    for idx, pc in enumerate(cs_county_list):
        current_path = evcs_dir + "\\" + pc[0] + "\\" + pc[1]
        current_cs_df = pd.read_csv(current_path, sep='\t', usecols=usecols)
        if idx == 0:
            all_cs = current_cs_df

        else:
            all_cs = pd.concat([all_cs, current_cs_df])

    return all_cs


def load_county(county_dir: str,
                usecols=None):
    """
    Read and Load the county (or district) file

    :param county_dir: Directory of the county file including file name
    :param usecols: Useful columns
    :return: Filtered county gdf
    """
    # Read county shp
    county_raw: gpd.GeoDataFrame = gpd.read_file(county_dir)
    if usecols is None:
        usecols = ['GID_2', 'NAME_1', 'NAME_2', 'HASC_2', 'geometry']
    county_raw = county_raw[usecols]

    return county_raw


def drop_duplicated(df: pd.DataFrame,
                    cols=None,
                    ) -> pd.DataFrame:
    """
    Drop the duplicated data
    :param cols: usecols
    :param df: DataFrame
    :return: DataFrame
    """
    return df.drop_duplicates(cols)


def filter_county(df: pd.DataFrame,
                  cols = None,
                  threshold: int = 10,
                  ) -> pd.DataFrame:
    """
    Filter the county/city with the EVCS less than the 10
    :param cols: usecols for groupby; expect for a list
    :param df: DataFrame
    :param threshold: int
    :return: DataFrame
    """
    return df.groupby(cols).filter(lambda x: len(x) >= threshold)


def evcp2evcs(df: pd.DataFrame = None,
              filepath: str = None,
              cols=None,
              ) -> pd.DataFrame:
    """
    Convert the EVCP to EVCS for study area Europe
    :param filepath: path of the EVCP file
    :param cols: uscols
    :param df: DataFrame
    :return: DataFrame
    """
    if cols is None:
        cols = ['value', 'location_unique_id', 'location_country']
    if df is None:
        evcp = pd.read_csv(filepath, usecols=['value', 'location_unique_id', 'location_country',
                                            'location_lng', 'location_lat'])
        evcs = evcp.drop_duplicates(cols)

    else:
        evcs = df.drop_duplicates(cols)

    return evcs
