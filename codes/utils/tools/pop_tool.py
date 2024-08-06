"""
Author: Xander Peng
Date: 2024/8/1
Description: 
"""
import os

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import transbigdata as tbd

us_pop_dir = r"../data/input/population/USA/"
eu_bound_dir = r"../data/input/boundary/europe/"
eu_pop_dir = r"../data/input/population/EU/"


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


def load_population(region: str):

    if region == 'china':
        pop = pd.read_csv("../data/input/population/China/China.csv")


    return pop


def pop2cs_cn(cs_df, pop_df,
              cs_xy_field=None,
              pop_xy_field=None,
              clean_drift=True,
              drift_dist=585
              ):
    pop_cs = tbd.ckdnearest(cs_df, pop_df,
                            cs_xy_field,
                            pop_xy_field)
    if clean_drift:
        pop_cs = pop_cs[pop_cs['dist'] <= drift_dist]

    # Create pop2cs GeoDataFrame
    pop_cs_gdf = gpd.GeoDataFrame(pop_cs,
                                  geometry=gpd.points_from_xy(pop_cs[cs_xy_field[0]],
                                                              pop_cs[cs_xy_field[1]]))
    return pop_cs, pop_cs_gdf


def county2_pop2cs(county_filtered: gpd.GeoDataFrame,
                   pop2cs_gdf: gpd.GeoDataFrame):
    """
    Match the county with the pop2cs file

    :param county_filtered: County file after cleaning and filtering
    :param pop2cs_gdf: The GeoDataFrame of pop2cs
    :return: Matched county-pop-cs gdf
    """
    if county_filtered.crs is not None:
        county_filtered = county_filtered.to_crs("EPSG:4326")
    else:
        county_filtered.crs = "EPSG:4326"
    if pop2cs_gdf.crs is not None:
        pop2cs_gdf = pop2cs_gdf.to_crs("EPSG:4326")
    else:
        pop2cs_gdf.crs = "EPSG:4326"

    # Spatial join
    county_pop2cs = gpd.sjoin(pop2cs_gdf, county_filtered, how='left', op='within')
    return county_pop2cs


def county2pop(county_gdf: gpd.GeoDataFrame, all_pop_gdf: gpd.GeoDataFrame,
               group_field='GID_2', pop_field='Z'):
    """
    Merge and match county with population grids, then get the max-min df

    :param county_gdf:
    :param all_pop_gdf:
    :param group_field: The 'groupby' field in the matched file, which is unique in the county file
    :param pop_field: The population field in the pop file
    :return: county-max-min-pop df
    """
    if county_gdf.crs is not None:
        county_gdf = county_gdf.to_crs("EPSG:4326")
    else:
        county_gdf.crs = "EPSG:4326"
    if all_pop_gdf.crs is not None:
        all_pop_gdf = all_pop_gdf.to_crs("EPSG:4326")
    else:
        all_pop_gdf.crs = "EPSG:4326"

    # Spatial join
    county_pop = gpd.sjoin(all_pop_gdf, county_gdf, how='left', op='within')
    county_pop.dropna(inplace=True)
    # Get max and min value of each county's population
    county_pop_maxmin = county_pop.groupby(group_field).agg(['max', 'min'])

    return county_pop_maxmin[pop_field]


def cal_v(county_pop_maxmin: pd.DataFrame,
          pop_county_cs: gpd.GeoDataFrame,
          merge_field='GID_2',
          pop_field='Z',
          output_dir=None):
    """
    Calculate the V value (population_coverage) of each charging station and output (option)

    :param county_pop_maxmin: Derive from @county2pop func
    :param pop_county_cs: Derive from @county2_pop2cs func
    :param merge_field: Field name for merging (join)
    :param pop_field: Population value field
    :param output_dir: Directory (including file name) of output (option)
    """
    county_pop_maxmin.reset_index(inplace=True)
    # Merge the pop-county-cs file with county_maxmin_pop
    matched_cs = pd.merge(pop_county_cs, county_pop_maxmin, how='left', on=merge_field)
    # Calculate V
    matched_cs['V'] = (matched_cs[pop_field] - matched_cs['min']) / (matched_cs['max'] - matched_cs['min'])

    if output_dir is not None:
        matched_cs.to_csv(output_dir)
    else:
        return matched_cs


def load_us_pop_sheets(pop_dir: str = us_pop_dir,
                       ):
    pop_sheets = list(filter(lambda x: x.endswith('.csv'), os.listdir(pop_dir)))
    state_names = list(map(lambda x: x[3:5], pop_sheets))
    return state_names, pop_sheets


def us_pop2cs(cs: pd.DataFrame, state: str,
           pop_dir: str, pop_sheets: list):
    '''
    A state-level match func.
    @state: State name (current state needed for matching)
    @pop_dir: Directory of population files
    @pop_sheets: A list containing all the pop files name
    return: A DataFrame with matching results
    '''
    # Read current state pop file
    current_pop_file = list(filter(lambda x: '-' + state in x, pop_sheets))
    if len(current_pop_file) > 1:
        print(current_pop_file)
        raise NameError('Too many population files are found')
    else:
        current_pop_file = current_pop_file[0]
    current_pop_dir = pop_dir + '\\' + current_pop_file
    current_pop = pd.read_csv(current_pop_dir)

    # Get a clip of cs records with current state
    current_cs = cs.query("State == @state")

    # Match the nearest point
    pop_cs = tbd.ckdnearest(current_cs, current_pop,
                            ['Longitude', 'Latitude'], ['X','Y'])
    return pop_cs

