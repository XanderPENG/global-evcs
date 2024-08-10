"""
Author: Xander Peng
Date: 2024/7/26
Description: Run this script to calculate the road density around EVCS
"""
import os

import numpy as np
import pandas as pd
import geopandas as gpd
import codes.utils.tools.network_tool as network_tool


BOUNDARY_DIR = r"../data/input/boundary//"
RADIUS_LIST = [300, 800, 1000]
EVCS_BUFFER_DIR = r"../data/interim/evcs_buffers//"
OUTPUT_DIR = r"../data/output/texts/network//"

city_area_all = pd.read_csv(r'..data/interim/support/area_table/city-level-area.csv',
                            usecols=['city', 'state', 'area'])

country_area_all = pd.read_csv(r'..data/interim/support/area_table/country-level-area.csv')
country_area_all.columns = ['country', 'area']

""" China """
# Load EVCS
cn_evcs = network_tool.load_evcs('china')
# Load road network
china_road = network_tool.load_road('china')

# Load city-level boundary
china_city_bound = gpd.read_file(BOUNDARY_DIR+'china/地级.shp',
                                 include_fields=['地名', '地级', '省级', 'area'])

# # City-level road density (optional)
# cn_city2roads = gpd.sjoin(china_city_bound,
#                           china_road,
#                           how='left',
#                           predicate='contains').groupby(['省级', '地名'])['length'].sum().reset_index()
# cn_city2roads = cn_city2roads.merge(china_city_bound[['省级', '地名', 'area']],
#                                     on=['省级', '地名'],
#                                     how='left')
# cn_city2roads['city_dens'] = cn_city2roads['length'] / cn_city2roads['area']
# _cn_city2roads = cn_city2roads.copy()  # Can be used to observe how many NA records

# Density around EVCS
for radius in RADIUS_LIST:
    print("start radius = ", radius)
    # For get unqiue ID of EVCS, helpful for susequent identification and match
    region_cs = cn_evcs.reset_index().rename(columns={'index': 'id'})

    current_buffer = gpd.read_file(EVCS_BUFFER_DIR + 'cn//' + 'cn_buffer' + str(radius) + '.shp')
    if current_buffer.crs is None:
        current_buffer.crs = 'EPSG:4326'
    # For get unqiue match EVCS id, which is consistent with @region_cs
    current_buffer = current_buffer.reset_index().rename(columns={'index': 'id'})
    print("start spatial join ")
    ''' Spatial join '''
    cs_roads: gpd.GeoDataFrame = gpd.sjoin(left_df=current_buffer,
                                           right_df=china_road,
                                           how='inner',
                                           predicate='contains')

    ''' Calculate roads density of each EVCS '''
    density_df: pd.DataFrame = cs_roads.drop(columns='geometry').groupby('id').sum()
    density_df['density'] = density_df['length'] / ((radius * 0.001) ** 2 * np.pi)

    region_cs = region_cs.merge(density_df.reset_index()[['id', 'length', 'density']],
                                how='left',
                                on='id')
    region_cs.dropna(inplace=True)

    # Calculate the ratio of cs roads density to the country density
    region_cs['c_density'] = region_cs['length'] / 9600000
    region_cs['density_r'] = region_cs['density'] / region_cs['c_density']

    # '''
    # Calculate the city-level road density
    # '''
    # ''' Merge city road density to EVCS '''
    # region_cs = region_cs.merge(cn_city2roads[['省级', '地名', 'city_dens']],
    #                             left_on=['pname', '地名'],
    #                             right_on=['省级', '地名'],
    #                             how='left')
    # # Process NA value
    # # region_cs['city_dens'] = region_cs['city_dens'].fillna(0.436138)
    # region_cs.dropna(inplace=True)
    # region_cs['city_den_r'] = region_cs['density'] / region_cs['city_dens']

    # Output the results
    os.makedirs(OUTPUT_DIR + 'cn//', exist_ok=True)
    region_cs.to_csv(OUTPUT_DIR + 'cn//' + str(radius) + '_roads.csv')


""" USA """
us_evcs = network_tool.load_evcs('usa')
us_city_bound = gpd.read_file(BOUNDARY_DIR + 'usa//gadm41_USA_2.shp',
                              includ_fields=['NAME_1', 'NAME_2', 'area'])

''' calculate the road density around EVCS by state loop due to the huge data size '''
us_buffers = {radius: gpd.read_file(EVCS_BUFFER_DIR + 'us//' + 'us_buffer' + str(radius) + '.shp')
              for radius in [300, 800, 1000]}
results_cs = {radius: pd.DataFrame()
              for radius in [300, 800, 1000]}

region_cs = us_buffers.get(300).drop(columns=['geometry', 'BUFF_DIST'])
states = set(us_buffers.get(300)['NAME_1'])

''' Read roads and processing cs by state '''
country_road_length = 0
for idx, state_name in enumerate(states):

    print('Processing: ' + str(idx) + ':' + state_name)

    ''' Load current state road with length '''
    state_road_shp = gpd.read_file(r"../data/input/road/us//" + state_name + '//len_roads.shp')

    country_road_length += state_road_shp['length'].sum()
    """ 
    Calculate the city road density
    """

    ''' Spatial join the city bound with road shp '''
    # 3 fields in @us_city_road: ['NAME_1', 'NAME_2', 'length']
    us_city_road = gpd.sjoin(us_city_bound,
                             state_road_shp,
                             how='inner',
                             predicate='contains').groupby(['NAME_1', 'NAME_2'])['length'].sum().reset_index()
    us_city_road = us_city_road.merge(us_city_bound[['NAME_1', 'NAME_2', 'area']],
                                      on=['NAME_1', 'NAME_2'],
                                      how='inner')
    # 5 fields in @us_city_road: ['NAME_1', 'NAME_2', 'length', 'area', 'city_dens']
    us_city_road['city_dens'] = us_city_road['length'] / us_city_road['area']
    us_city_road.dropna(inplace=True)

    ''' EVCS with roads '''
    for radius, buffer in us_buffers.items():
        # Correct the CRS
        if buffer.crs is None:
            buffer.crs = 'EPSG:4326'

        ''' Spatial join '''
        # 2 fields in @cs_roads: [ORIG_FID, length]
        cs_roads: gpd.GeoDataFrame = gpd.sjoin(left_df=buffer,
                                               right_df=state_road_shp,
                                               how='inner',
                                               predicate='contains').groupby('ORIG_FID')['length'].sum().reset_index()

        ''' Calculate road density of each EVCS '''
        cs_roads['density'] = cs_roads['length'] / ((radius * 0.001) ** 2 * np.pi)

        # Merge the results into clip cs file
        clip_cs = region_cs.query("NAME_1 == @state_name")  # A part of cs with state as state_name
        clip_cs = clip_cs.merge(cs_roads,
                                how='left',
                                on='ORIG_FID')
        ''' Add city road density into each EVCS record '''
        clip_cs = clip_cs.merge(us_city_road[['NAME_1', 'NAME_2', 'city_dens']],
                                on=['NAME_1', 'NAME_2'],
                                how='inner'
                                )
        # Calculate city-level road density ratio
        clip_cs['city_den_r'] = clip_cs['density'] / clip_cs['city_dens']
        clip_cs = clip_cs.dropna(0)

        ''' Update the result cs '''
        result_cs_df = results_cs.get(radius)
        result_cs_df = pd.concat([result_cs_df, clip_cs])
        results_cs.update({radius: result_cs_df})

''' Calculate the region-level road density and the ratio '''
us_area = country_area_all.query("country == 'usa'").iloc[0, 1]
region_density: float = country_road_length / us_area  # km/km^2

# Calculate the region road density ratio and output
for radius, result_cs in results_cs.items():
    result_cs['region_density'] = region_density
    result_cs['density_r'] = result_cs['density'] / result_cs['region_density']

    os.makedirs(OUTPUT_DIR + 'us//', exist_ok=True)
    result_cs.to_csv(OUTPUT_DIR + 'us//' + str(radius) + '_roads.csv')


""" Europe """
eu_raw_road_dir = r"../data/input/poi/europe/shp//"
eu_buffers = {radius: gpd.read_file(EVCS_BUFFER_DIR + 'eu//' + 'eu_buffer' + str(radius) + '.shp')
              for radius in [300, 800, 1000]}

# Initialize some df to store results
results_cs = {radius: pd.DataFrame()
              for radius in [300, 800, 1000]}

country_list = list(set(eu_buffers.get(300)['COUNTRY']))

''' Read roads and processing cs by country '''
eu_road_length = 0  # Initilize the road length

for idx, row in eu_buffers.get(300)[['location_c', 'COUNTRY']].drop_duplicates().reset_index(drop=True).iterrows():
    country_name = row['COUNTRY']
    country_abr = row['location_c']

    print('Processing: ' + str(idx) + ':' + country_name)

    """ 
        Load after length-calculation road;
        Otherwise, 
        Load original road, and calculate the length    
    """
    out_roads_dir = r'../data/input/road/eu//'

    ''' 1. Load road with length file (if applicable) '''
    if os.path.isfile(out_roads_dir + country_name + '//' + 'len_roads.shp'):
        print(' Load roads ')
        road_shp = gpd.read_file(out_roads_dir + country_name + '//' + 'len_roads.shp',
                                 crs='EPSG: 4326')
        eu_road_length += road_shp['length'].sum()

    else:  # ''' 2. No such file '''
        road_shp_folder = network_tool.filter_folder(country_name, eu_raw_road_dir)  # Get the corresponding country folder name
        print('finish find folder')
        ''' Load current country road '''
        road_shp: gpd.GeoDataFrame = network_tool.load_roads(eu_raw_road_dir + '//' + road_shp_folder)
        print('finish load road')
        class_str = ['motorway', 'motorway_link', 'trunk', 'trunk_link', 'primary', 'primary_link',
                     'secondary', 'secondary_link', 'tertiary', 'tertiary_link', 'unclassified',
                     'residential', 'living_street', 'service']

        road_shp = road_shp.query("fclass in @class_str")  # Filter target class roads

        ''' Caculate the road length '''
        road_shp['length'] = road_shp['geometry'].map(lambda x: network_tool.cal_length(x))
        print('finish cal length')
        eu_road_length += road_shp['length'].sum()  # Update the country-level roads length

        ''' Output the roads shp '''

        os.makedirs(out_roads_dir + country_name + '//', exist_ok=True)
        road_shp.to_file(out_roads_dir + country_name + '//' + 'len_roads.shp')

        print('finish output road')

    ''' EVCS with roads (This can only get one country's cs-road_density)'''
    for radius, buffer in eu_buffers.items():
        print("Start " + str(radius) + ' Meter Buffer')
        # Correct the CRS
        if buffer.crs is None:
            buffer.crs = 'EPSG:4326'
        print("Start spatial join EVCS and roads")
        ''' Spatial join '''
        cs_roads: gpd.GeoDataFrame = gpd.sjoin(left_df=buffer,
                                               right_df=road_shp,
                                               how='inner',
                                               predicate='contains')

        ''' Calculate road density of each cs '''
        cs_road_density: pd.DataFrame = cs_roads.drop(columns=['geometry']).groupby('ORIG_FID').sum()
        cs_road_density['density'] = cs_road_density['length'] / ((radius * 0.001) ** 2 * np.pi)
        cs_road_density = cs_road_density[['length', 'density']]
        ''' Calculate the city-level density ratio, i.e., 
            the road density of EVCS / the density of road in this city'''
        ''' Spatial join the city-level bound with the road'''
        # Load boundary: 2nd-level boundary
        eu_bound_root = BOUNDARY_DIR + 'europe'
        current_country_bound_files_list = os.listdir(
            eu_bound_root + '//' + 'EU_' + country_abr)  # all level of boundary shp of current country

        if any(list(map(lambda x: '_2.shp' in x, current_country_bound_files_list))):  # if the 2nd level is available

            current_country_bound_filename: str = \
            list(filter(lambda x: '_2.shp' in x, current_country_bound_files_list))[0]
            current_country_bound = gpd.read_file(
                eu_bound_root + '\\' + 'EU_' + country_abr + '\\' + current_country_bound_filename,
                include_fields=['GID_0', 'COUNTRY', 'NAME_1', 'NAME_2'],
                crs='EPSG: 4326')
        elif any(list(map(lambda x: '_1.shp' in x, current_country_bound_files_list))):  # if the 1st level is available

            current_country_bound_filename: str = \
            list(filter(lambda x: '_1.shp' in x, current_country_bound_files_list))[0]
            current_country_bound: gpd.GeoDataFrame = gpd.read_file(
                eu_bound_root + '\\' + 'EU_' + country_abr + '\\' + current_country_bound_filename,
                include_fields=['GID_0', 'COUNTRY', 'NAME_1'],
                crs='EPSG: 4326')
            current_country_bound['NAME_2'] = current_country_bound['NAME_1']
            current_country_bound = current_country_bound.reindex(
                columns=['GID_0', 'COUNTRY', 'NAME_1', 'NAME_2', 'geometry'])
        else:  # Only the 0-level boundary
            current_country_bound_filename: str = \
            list(filter(lambda x: '_0.shp' in x, current_country_bound_files_list))[0]
            current_country_bound: gpd.GeoDataFrame = gpd.read_file(
                eu_bound_root + '\\' + 'EU_' + country_abr + '\\' + current_country_bound_filename,
                crs='EPSG: 4326')
            current_country_bound['NAME_1'] = current_country_bound['COUNTRY']
            current_country_bound['NAME_2'] = current_country_bound['COUNTRY']
            current_country_bound = current_country_bound.reindex(
                columns=['GID_0', 'COUNTRY', 'NAME_1', 'NAME_2', 'geometry'])

        # current country road-density
        tem_query_cname = network_tool.identify_country(kw=country_name,
                                                        l=country_area_all['country'].tolist())
        current_country_area = country_area_all.query("country == @tem_query_cname").iloc[0, 1]
        current_country_road_density: float = road_shp['length'].sum() / current_country_area

        print("Start spatial join city bounds and roads")
        # Spatial join the city-level bound with the road
        city_bound2road = gpd.sjoin(left_df=current_country_bound,
                                    right_df=road_shp,
                                    how='left',
                                    predicate='contains')
        tem_city_road_length = city_bound2road.groupby(['NAME_1', 'NAME_2'])['length'].sum().reset_index()
        tem_city_road_density = city_area_all.merge(tem_city_road_length,
                                                    left_on=['state', 'city'],
                                                    right_on=['NAME_1', 'NAME_2'],
                                                    how='right')
        tem_city_road_density['city_dens'] = tem_city_road_density['length'] / tem_city_road_density['area']
        tem_city_road_density['city_dens'].fillna(tem_city_road_density['length'] / current_country_road_density,
                                                  inplace=True)

        print("Start merge result")
        ''' City-level density ratio '''
        tem_cs_idx = cs_road_density.index.tolist()
        tem_cs = buffer.query(" @tem_cs_idx in ORIG_FID")
        tem_cs = tem_cs.merge(cs_road_density.reset_index()[['ORIG_FID', 'density']],
                              on='ORIG_FID',
                              how='left')
        tem_cs = tem_cs.merge(tem_city_road_density[['NAME_1', 'NAME_2', 'city_dens']],
                              on=['NAME_1', 'NAME_2'],
                              how='left')

        tem_cs['city_den_r'] = tem_cs['density'] / tem_cs['city_dens']
        tem_cs.dropna(inplace=True)

        results_cs.update({radius: pd.concat([results_cs.get(radius), tem_cs]
                                             )
                           })

""" Finish all countries;
    Calculate the region road density, and the region-road-density-ratio
    for all buffers
    """

eu_area = country_area_all.query("country not in ['china','usa']")['area'].sum()
region_density: float = eu_road_length / eu_area  # km/km^2

# Calculate the ratio and output
for radius, result_cs in results_cs.items():
    result_cs['region_density'] = region_density
    result_cs['density_r'] = result_cs['density'] / result_cs['region_density']
    os.makedirs(OUTPUT_DIR + 'eu//')
    result_cs.to_csv(OUTPUT_DIR + 'eu//' + str(radius) + '_roads.csv')

