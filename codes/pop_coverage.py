"""
Author: Xander Peng
Date: 2024/7/26
Description:
"""
import os

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import codes.utils.tools.pop_tool as pop_tool
import codes.preprocessing.tools as clean_tool
import transbigdata as tbd


""" Calculate the population coverage of EVCS for China"""
china_evcs = pd.read_csv("../data/interim/cleaned_evcs/china_evcs.csv", index_col=0)

china_county = pop_tool.load_county("../data/input/boundary/china/地级.shp",
                                    usecols=['地名', '区划码', '地级', '省级', 'ENG_NAME', 'geometry'])

china_pop = pop_tool.load_population('china')
china_pop_gdf = gpd.GeoDataFrame(china_pop,
                                 geometry=gpd.points_from_xy(china_pop['X'], china_pop['Y']))

# Match population grid with EVCS
pop_cs, pop_cs_gdf = pop_tool.pop2cs_cn(china_evcs, china_pop_gdf,
                                        ['wgs84_lon', 'wgs84_lat'],
                                        ['X', 'Y'])
# Add county information to the pop_cs_gdf
county_pop_cs = pop_tool.county2_pop2cs(china_county, pop_cs_gdf)

# Calculate the population stats of each county
county_pop = pop_tool.county2pop(china_county, china_pop_gdf, '区划码', 'Z')

# Calculate the population coverage of EVCS
cs_pop_cov = pop_tool.cal_v(county_pop, county_pop_cs, '区划码',
                            'Z')
cs_pop_cov = cs_pop_cov[cs_pop_cov['V'].between(0, 1)]

cs_pop_cov.to_csv("../data/output/texts/population/china_evcs4plot.csv")


""" Calculate the population coverage of EVCS for the US """
# Get the PopGrid sheets list and state name list
pop_state_name, us_pop_sheets = pop_tool.load_us_pop_sheets()

# Load the US EVCS
us_evcs = pd.read_csv("../data/input/raw_data/USA.csv",
                      usecols=['Station Name', 'City', 'State', 'Latitude', 'Longitude'],
                      index_col=0)
cs_states_set = set(us_evcs['State'].to_list())
diff_states = list(cs_states_set.difference(pop_state_name))

us_evcs = us_evcs.loc[~us_evcs['State'].isin(diff_states)]
us_evcs.reset_index(inplace=True)
us_evcs.rename(columns={'index': 'origin_idx'}, inplace=True)

# Start Match and get the pop2cs
us_pop2cs = pd.DataFrame()
for idx, s in enumerate(list(cs_states_set)):
    if idx == 0:
        current_pop2cs = pop_tool.us_pop2cs(us_evcs, s,
                                            pop_tool.us_pop_dir,
                                            us_pop_sheets)
        us_pop2cs = current_pop2cs
    else:
        current_pop2cs = pop_tool.us_pop2cs(us_evcs, s,
                                            pop_tool.us_pop_dir,
                                            us_pop_sheets)
        us_pop2cs = pd.concat([us_pop2cs, current_pop2cs])

us_pop2cs = us_pop2cs[us_pop2cs['dist'] <= 585]
us_pop2cs_gdf = gpd.GeoDataFrame(us_pop2cs,
                                 geometry=gpd.points_from_xy(us_pop2cs['Longitude'], us_pop2cs['Latitude']))

# Load county shapefile
us_county_gdf = pop_tool.load_county("../data/input/boundary/usa/gadm41_USA_2.shp.shp")

# Add county information to the pop_cs_gdf
us_county_pop_cs = pop_tool.county2_pop2cs(us_county_gdf, us_pop2cs_gdf)

# Merge all the pop file
us_pop = pd.DataFrame()
for idx, s in enumerate(us_pop_sheets):
    if idx == 0:
        current_pop = pd.read_csv(pop_tool.us_pop_dir + '\\' + s)
        us_pop = current_pop
    else:
        current_pop = pd.read_csv(pop_tool.us_pop_dir + '\\' + s)
        us_pop = pd.concat([us_pop, current_pop])
us_pop_gdf = gpd.GeoDataFrame(us_pop,
                                geometry=gpd.points_from_xy(us_pop['X'], us_pop['Y']))
# Add county information to the pop_cs_gdf
us_county_pop = pop_tool.county2pop(us_county_gdf, us_pop_gdf, 'GID_2', 'Z')

# Calculate the population coverage of EVCS
us_cs_pop_cov = pop_tool.cal_v(us_county_pop, us_county_pop_cs, 'GID_2',
                                'Z')
us_cs_pop_cov = us_cs_pop_cov[us_cs_pop_cov['V'].between(0, 1)]
us_cs_pop_cov = clean_tool.filter_county(us_cs_pop_cov,
                                         cols=['NAME_1', 'NAME_2'])
us_cs_pop_cov.to_csv("../data/output/texts/population/us_evcs4plot.csv")

""" Calculate the population coverage of EVCS for Europe """
# Load the EVCS data
eu_evcs = clean_tool.evcp2evcs(clean_tool.EUROPE_EVCS_PATH)
eu_evcs = clean_tool.drop_duplicated(eu_evcs,
                                     cols=['value', 'location_unique_id', 'location_country'])
# EU country 2-code name list
eu_country_name_list = eu_evcs['location_country'].drop_duplicates().to_list()
# Load the EU boundary list
eu_bound_root = pop_tool.eu_bound_dir
eu_bound_folder_list = list(filter(lambda x: '(o)' not in x and '.zip' not in x, os.listdir(eu_bound_root)))
# Load the EU population list
eu_pop_root = pop_tool.eu_pop_dir
eu_pop_file_list = list(filter(lambda x: '(o)' not in x and '.zip' not in x, os.listdir(eu_pop_root)))

eu_evcs_pop = gpd.GeoDataFrame()
for eu_country_idx, eu_country in enumerate(eu_country_name_list):

    """ 
    Prepare data 
    """

    ''' Load population '''
    current_country_pop = pd.read_csv(eu_pop_root + '\\' + 'eu_' + eu_country + '_pop.csv',
                                      usecols=[1, 2, 3])

    ''' Load boundary: 2nd-level boundary '''
    current_country_bound_files_list = os.listdir(
        eu_bound_root + '\\' + 'EU_' + eu_country)  # all level of boundary shp of current country

    if any(list(map(lambda x: '_2.shp' in x, current_country_bound_files_list))):  # if the 2nd level is available

        current_country_bound_filename: str = list(filter(lambda x: '_2.shp' in x, current_country_bound_files_list))[0]
        current_country_bound = gpd.read_file(
            eu_bound_root + '\\' + 'EU_' + eu_country + '\\' + current_country_bound_filename,
            include_fields=['GID_0', 'COUNTRY', 'NAME_1', 'NAME_2'],
            crs='EPSG: 4326')
    elif any(list(map(lambda x: '_1.shp' in x, current_country_bound_files_list))):  # if the 1st level is available

        current_country_bound_filename: str = list(filter(lambda x: '_1.shp' in x, current_country_bound_files_list))[0]
        current_country_bound: gpd.GeoDataFrame = gpd.read_file(
            eu_bound_root + '\\' + 'EU_' + eu_country + '\\' + current_country_bound_filename,
            include_fields=['GID_0', 'COUNTRY', 'NAME_1'],
            crs='EPSG: 4326')
        current_country_bound['NAME_2'] = current_country_bound['NAME_1']
        current_country_bound = current_country_bound.reindex(
            columns=['GID_0', 'COUNTRY', 'NAME_1', 'NAME_2', 'geometry'])
    else:  # Only the 0-level boundary
        current_country_bound_filename: str = list(filter(lambda x: '_0.shp' in x, current_country_bound_files_list))[0]
        current_country_bound: gpd.GeoDataFrame = gpd.read_file(
            eu_bound_root + '\\' + 'EU_' + eu_country + '\\' + current_country_bound_filename,
            crs='EPSG: 4326')
        current_country_bound['NAME_1'] = current_country_bound['COUNTRY']
        current_country_bound['NAME_2'] = current_country_bound['COUNTRY']
        current_country_bound = current_country_bound.reindex(
            columns=['GID_0', 'COUNTRY', 'NAME_1', 'NAME_2', 'geometry'])

    ''' Current country css '''
    current_country_evcs = eu_evcs[eu_evcs['location_country'] == eu_country]

    """ Match css with population grid, based on the nearest distance """
    current_country_evcs2pop = tbd.ckdnearest(current_country_evcs,
                                              current_country_pop,
                                              ['location_lng', 'location_lat'],
                                              ['X', 'Y']
                                              )

    """ 
        Match county with population, 
        so as to calculate the 'max-min' population of each county 
    """

    ''' Convert population df into gdf'''
    current_country_pop_gdf = gpd.GeoDataFrame(current_country_pop,
                                               geometry=gpd.points_from_xy(current_country_pop['X'],
                                                                           current_country_pop['Y']),
                                               crs='EPSG: 4326')
    # Spatial join the bound and population (at the 2nd level)
    current_country_bound2pop: gpd.GeoDataFrame = gpd.sjoin(current_country_bound,
                                                            current_country_pop_gdf,
                                                            how='left',
                                                            predicate='contains')
    # Get max and min population in each county
    current_country_county_pop_maxAndmin = current_country_bound2pop.groupby(['GID_0', 'NAME_1', 'NAME_2'])['Z'].agg(
        ['max', 'min'])
    current_country_county_pop_maxAndmin.reset_index(inplace=True)

    """ Match css2pop with county (boundary), to figure out which state(county) the css within """
    current_country_css2pop2county: gpd.GeoDataFrame = gpd.sjoin(current_country_evcs2pop,
                                                                 current_country_bound,
                                                                 how='left',
                                                                 predicate='within'
                                                                 )
    """
    Integrate the county 'max-min population' into css2pop2county DataFrame
    """
    current_country_css_county_pop_mm = current_country_css2pop2county.merge(current_country_county_pop_maxAndmin,
                                                                             how='left',
                                                                             on=['GID_0', 'NAME_1', 'NAME_2'])

    """ 
    Calculate 'V' value for each css 
    """
    current_country_css_county_pop_mm['V'] = (current_country_css_county_pop_mm['Z'] -
                                              current_country_css_county_pop_mm['min']) / (
                                                         current_country_css_county_pop_mm['max'] -
                                                         current_country_css_county_pop_mm['min'])

    eu_evcs_pop = pd.concat([eu_evcs_pop, current_country_css_county_pop_mm])

eu_evcs_pop = eu_evcs_pop[eu_evcs_pop['V'].between(0, 1)]
eu_evcs_pop = clean_tool.filter_county(eu_evcs_pop,
                                       cols=['NAME_1', 'NAME_2'])
eu_evcs_pop.to_csv("../data/output/texts/population/eu_evcs4plot.csv")
