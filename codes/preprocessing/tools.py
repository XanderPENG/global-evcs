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

CN_EVCS_FOLDER_DIR = r"../data/input/raw_data/evcs-text/china.csv.gz"
EUROPE_EVCS_PATH = r"../data/input/raw_data/evcs-text/europe.csv.gz"
USA_EVCS_PATH = r"../data/input/raw_data/evcs-text/usa.csv.gz"

CN_EVCS_OUTPUT_DIR = r"../data/interim/cleaned_evcs/clean_china.csv.gz"
EUROPE_EVCS_OUTPUT_DIR = r"../data/interim/cleaned_evcs/clean_europe.csv.gz"
USA_EVCS_OUTPUT_DIR = r"../data/interim/cleaned_evcs/clean_usa.csv.gz"

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

def load_cn_evcs_v2024(evcs_dir: str,
                       usecols=None,):
    df = pd.read_csv(evcs_dir, usecols=usecols)
    return df


def load_usa_evcs(evcs_dir: str or None = None,
                  usecols: list or None = None,
                    ) -> pd.DataFrame:
    if evcs_dir is None:
        evcs_dir = USA_EVCS_PATH
    if usecols is None:
        usecols = ['Station Name', 'City', 'State', 'Latitude', 'Longitude']
    return pd.read_csv(evcs_dir, usecols=usecols)

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
        cols = ['location_unique_id', 'location_country']
    if df is None:
        evcp = pd.read_csv(filepath, usecols=['location_unique_id', 'location_country',
                                            'Latitude', 'Longitude'])
        evcs = evcp.drop_duplicates(cols)

    else:
        evcs = df.drop_duplicates(cols)

    return evcs


"""
Util for creating the spatial boundary data 
"""

def create_europe_boundary(europe_boundary_dir=None,):
    if europe_boundary_dir is None:
        europe_boundary_dir = r"../data/input/boundary/europe//"

    if not os.path.isdir(europe_boundary_dir) or os.listdir(europe_boundary_dir) == []:
        raise FileNotFoundError("Europe boundary directory is not exist or no file in the directory. pLease check it.")

    # Get the subdirectory list (Country level)
    country_boundary_list = os.listdir(europe_boundary_dir)
    country_boundary_list = list(filter(lambda x: "." not in x, country_boundary_list))

    ''' Read and create the 1st (country) level boundary data '''
    europe_country_boundary = gpd.GeoDataFrame()
    for country_folder in country_boundary_list:
        country_boundary_files = os.listdir(europe_boundary_dir + country_folder)
        # Filter and get the country_level boundary file
        country_level_filename = list(filter(lambda x: "_0.shp" in x and '.xml' not in x, country_boundary_files))[0]
        country_boundary = gpd.read_file(europe_boundary_dir + country_folder + "//" + country_level_filename)
        europe_country_boundary = pd.concat([europe_country_boundary, country_boundary])

    if europe_country_boundary.crs is None:
        europe_country_boundary.crs = "EPSG:4326"

    ''' Read and create the 2nd (city) level boundary data '''
    europe_city_boundary = gpd.GeoDataFrame()
    for country_folder in country_boundary_list:
        country_boundary_files = os.listdir(europe_boundary_dir + country_folder)
        # Filter and get the city_level boundary file
        city_level_filename = list(filter(lambda x: "_2.shp" in x and '.xml' not in x, country_boundary_files))
        # If the city_level file is exist, then read it
        if city_level_filename:
            city_boundary = gpd.read_file(europe_boundary_dir + country_folder + "//" + city_level_filename[0])
            europe_city_boundary = pd.concat([europe_city_boundary, city_boundary])

    if europe_city_boundary.crs is None:
        europe_city_boundary.crs = "EPSG:4326"

    ''' Output the boundary data '''
    europe_country_boundary.to_file(europe_boundary_dir + "europe_country_boundary.shp.zip", driver='ESRI Shapefile')
    europe_city_boundary.to_file(europe_boundary_dir + "europe_city_boundary.shp.zip", driver='ESRI Shapefile')


def load_europe_boundary(level: str,):
    if level.lower() == 'state':
        europe_boundary = gpd.read_file("../data/input/boundary/europe/europe_country_boundary.shp.zip")
    elif level.lower() == 'city':
        europe_boundary = gpd.read_file("../data/input/boundary/europe/europe_city_boundary.shp.zip")
    else:
        raise ValueError("Please input the correct level: state or city")
    return europe_boundary


""" Util for spatial join Europe EVCS with Europe boundary data """

def sjoin_europe_evcs(europe_evcs: pd.DataFrame,
                      europe_boundary: gpd.GeoDataFrame,
                      ) -> gpd.GeoDataFrame:
    """
    Spatial join the Europe EVCS with Europe boundary data
    :param europe_evcs: DataFrame
    :param europe_boundary: GeoDataFrame
    :return: GeoDataFrame
    """
    europe_evcs_gdf = gpd.GeoDataFrame(europe_evcs,
                                       geometry=gpd.points_from_xy(europe_evcs['Longitude'], europe_evcs['Latitude']))
    europe_evcs_gdf.crs = "EPSG:4326"

    origin_cols = list(europe_evcs_gdf.columns)

    europe_evcs_boundary = gpd.sjoin(europe_evcs_gdf, europe_boundary, how='left', predicate='within')
    europe_evcs_boundary = europe_evcs_boundary[origin_cols + ['COUNTRY', 'NAME_1', 'NAME_2', 'HASC_2']]

    return europe_evcs_boundary

def sjoin_usa_evcs(us_evcs: pd.DataFrame,
                   usa_boundary_path: str,
                   ) -> gpd.GeoDataFrame:
    """
    Spatial join the USA EVCS with USA boundary data
    :param us_evcs: DataFrame
    :param usa_boundary: GeoDataFrame
    :return: GeoDataFrame
    """
    us_evcs_gdf = gpd.GeoDataFrame(us_evcs,
                                   geometry=gpd.points_from_xy(us_evcs['Longitude'], us_evcs['Latitude']))
    us_evcs_gdf.crs = "EPSG:4326"

    origin_cols = list(us_evcs_gdf.columns)

    us_boundary = gpd.read_file(usa_boundary_path)
    if us_boundary.crs is None:
        us_boundary.crs = "EPSG:4326"

    us_evcs_boundary = gpd.sjoin(us_evcs_gdf, us_boundary, how='left', predicate='within')
    us_evcs_boundary = us_evcs_boundary[origin_cols + ['NAME_1', 'NAME_2', 'HASC_2']]

    return us_evcs_boundary.drop(columns=['geometry'])

