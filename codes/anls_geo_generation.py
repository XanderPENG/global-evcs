"""
Author: Xander Peng
Date: 2025/3/4
Description: This script is used to generate the geo files (at province/state and city/county levels) for each analysis.
"""
from codes.utils.tools.geo_file_tool import output_geo_files
from codes.utils.tools.enums import AggLevel, Region
import pandas as pd
import geopandas as gpd
import logging

logging.basicConfig(level=logging.INFO)

logging.info("Start to read boundary.")
''' Boundary '''
china_city_boundary = gpd.read_file(r"../data/input/boundary/china/地级.shp")
usa_county_boundary = gpd.read_file(r"../data/input/boundary/usa/gadm41_USA_2.shp")
europe_city_boundary = gpd.read_file(r"../data/input/boundary/europe/europe_city_boundary.shp.zip")

"""
logging.info("Start to read population data.")
''' Population '''
china_pop_results = pd.read_csv(r"../data/output/texts/population/china_evcs_pop.csv.gz")
usa_pop_results = pd.read_csv(r"../data/output/texts/population/usa_evcs_pop.csv.gz")
europe_pop_results = pd.read_csv(r"../data/output/texts/population/europe_evcs_pop.csv.gz")

pop_geo_output_dir = r"../data/output/geo_files/population"

logging.info("Start to output china geo-pop files.")
output_geo_files(data=china_pop_results,
                    boundary=china_city_boundary,
                    agg_col=['省级','地名'],
                    anls_col='V',
                    region=Region.CHINA,
                    level=AggLevel.COUNTY,
                    output_dir=pop_geo_output_dir,
                    output_filename='population.geojson',
                    )

logging.info("Start to output usa geo-pop files.")
output_geo_files(data=usa_pop_results,
                    boundary=usa_county_boundary,
                    agg_col=['NAME_1','NAME_2'],
                    anls_col='V',
                    region=Region.USA,
                    level=AggLevel.COUNTY,
                    output_dir=pop_geo_output_dir,
                    output_filename='population.geojson',
                    )

logging.info("Start to output europe geo-pop files.")
output_geo_files(data=europe_pop_results,
                    boundary=europe_city_boundary,
                    agg_col=['GID_0','NAME_1', 'NAME_2'],
                    anls_col='V',
                    region=Region.EUROPE,
                    level=AggLevel.COUNTY,
                    output_dir=pop_geo_output_dir,
                    output_filename='population.geojson',
                    )
"""

"""
''' POI '''
poi_geo_output_dir = r"../data/output/geo_files/poi"

china_poi_results = {radius: pd.read_csv(f"../data/output/texts/poi/china/{radius}dist.csv.gz")
                     for radius in [300, 800, 1000]}
logging.info("start to merge boundary fields into china poi results.")
for radius, china_poi_result_ in china_poi_results.items():
    cn_poi_results_gdf_ = gpd.GeoDataFrame(china_poi_result_,
                                           geometry=gpd.points_from_xy(china_poi_result_['wgs84_lng'],
                                                              china_poi_result_['wgs84_lat']),
                                           crs="EPSG:4326")
    cn_poi_results_with_bound_gdf_ = gpd.sjoin(cn_poi_results_gdf_,
                                               china_city_boundary,
                                               how='left',
                                               predicate='within')
    china_poi_results[radius] = cn_poi_results_with_bound_gdf_[china_poi_result_.columns.tolist() + ['地名', '地级', '省级']]

usa_poi_results = {radius: pd.read_csv(f"../data/output/texts/poi/usa/{radius}dist.csv.gz")
                     for radius in [300, 800, 1000]}

europe_poi_results = {radius: pd.read_csv(f"../data/output/texts/poi/europe/{radius}dist.csv.gz")
                        for radius in [300, 800, 1000]}
for radius, europe_poi_result_ in europe_poi_results.items():
    eu_poi_results_gdf_ = gpd.GeoDataFrame(europe_poi_result_,
                                           geometry=gpd.points_from_xy(europe_poi_result_['Longitude'],
                                                              europe_poi_result_['Latitude']),
                                           crs="EPSG:4326")
    eu_poi_results_with_bound_gdf_ = gpd.sjoin(eu_poi_results_gdf_,
                                               europe_city_boundary.drop(columns=['COUNTRY']),
                                               how='left',
                                               predicate='within')
    europe_poi_results[radius] = eu_poi_results_with_bound_gdf_[europe_poi_result_.columns.tolist() + ['NAME_1', 'NAME_2', 'GID_0']]

logging.info("Start to output china geo-poi files.")
for radius, china_poi_result in china_poi_results.items():
    output_geo_files(data=china_poi_result,
                     boundary=china_city_boundary,
                     agg_col=['省级','地名'],
                     anls_col='Mix',
                     region=Region.CHINA,
                     level=AggLevel.COUNTY,
                     output_dir=poi_geo_output_dir,
                     output_filename=f"poi_{radius}dist.geojson",
                     )

logging.info("Start to output usa geo-poi files.")
for radius, usa_poi_result in usa_poi_results.items():
    output_geo_files(data=usa_poi_result,
                     boundary=usa_county_boundary,
                     agg_col=['NAME_1','NAME_2'],
                     anls_col='Mix',
                     region=Region.USA,
                     level=AggLevel.COUNTY,
                     output_dir=poi_geo_output_dir,
                     output_filename=f"poi_{radius}dist.geojson",
                     )

logging.info("Start to output europe geo-poi files.")
for radius, europe_poi_result in europe_poi_results.items():
    output_geo_files(data=europe_poi_result,
                     boundary=europe_city_boundary,
                     agg_col=['GID_0','NAME_1', 'NAME_2'],
                     anls_col='Mix',
                     region=Region.EUROPE,
                     level=AggLevel.COUNTY,
                     output_dir=poi_geo_output_dir,
                     output_filename=f"poi_{radius}dist.geojson",
                     )
"""
"""
''' Road network '''
road_geo_output_dir = r"../data/output/geo_files/network"

logging.info("Start to read road network data.")
china_road_results = {radius: pd.read_csv(f"../data/output/texts/network/china/{radius}_roads.csv.gz")
                      for radius in [300, 800, 1000]}

usa_road_results = {radius: pd.read_csv(f"../data/output/texts/network/usa/{radius}_roads.csv.gz")
                    for radius in [300, 800, 1000]}

europe_road_results = {radius: pd.read_csv(f"../data/output/texts/network/europe/{radius}_roads.csv.gz")
                          for radius in [300, 800, 1000]}

logging.info("Start to output china geo-road files.")
for radius, china_road_result in china_road_results.items():
    output_geo_files(data=china_road_result,
                     boundary=china_city_boundary,
                     agg_col=['省级','地名'],
                     anls_col='density',
                     region=Region.CHINA,
                     level=AggLevel.COUNTY,
                     output_dir=road_geo_output_dir,
                     output_filename=f"road_density_{radius}dist.geojson",
                     )

    output_geo_files(data=china_road_result,
                     boundary=china_city_boundary,
                     agg_col=['省级', '地名'],
                     anls_col='city_den_r',
                     region=Region.CHINA,
                     level=AggLevel.COUNTY,
                     output_dir=road_geo_output_dir,
                     output_filename=f"road_density_ratio_{radius}dist.geojson",
                     )

logging.info("Start to output usa geo-road files.")
for radius, usa_road_result in usa_road_results.items():
    output_geo_files(data=usa_road_result,
                     boundary=usa_county_boundary,
                     agg_col=['NAME_1','NAME_2'],
                     anls_col='density',
                     region=Region.USA,
                     level=AggLevel.COUNTY,
                     output_dir=road_geo_output_dir,
                     output_filename=f"road_density_{radius}dist.geojson",
                     )

    output_geo_files(data=usa_road_result,
                     boundary=usa_county_boundary,
                     agg_col=['NAME_1', 'NAME_2'],
                     anls_col='city_den_r',
                     region=Region.USA,
                     level=AggLevel.COUNTY,
                     output_dir=road_geo_output_dir,
                     output_filename=f"road_density_ratio_{radius}dist.geojson",
                     )

logging.info("Start to output europe geo-road files.")
for radius, europe_road_result in europe_road_results.items():
    output_geo_files(data=europe_road_result,
                     boundary=europe_city_boundary,
                     agg_col=['COUNTRY','NAME_1', 'NAME_2'],
                     anls_col='density',
                     region=Region.EUROPE,
                     level=AggLevel.COUNTY,
                     output_dir=road_geo_output_dir,
                     output_filename=f"road_density_{radius}dist.geojson",
                     )

    output_geo_files(data=europe_road_result,
                     boundary=europe_city_boundary,
                     agg_col=['COUNTRY', 'NAME_1', 'NAME_2'],
                     anls_col='city_den_r',
                     region=Region.EUROPE,
                     level=AggLevel.COUNTY,
                     output_dir=road_geo_output_dir,
                     output_filename=f"road_density_ratio_{radius}dist.geojson",
                     )
"""
''' housing '''
housing_geo_output_dir = r"../data/output/geo_files/housing"

logging.info("Start to read housing data.")
china_housing_results = {radius: pd.read_csv(f"../data/output/texts/housing/china/{radius}.csv.gz")
                         for radius in [300, 800, 1000]}
usa_housing_results = {radius: pd.read_csv(f"../data/output/texts/housing/usa/{radius}.csv.gz")
                          for radius in [300, 800, 1000]}

logging.info("Start to output china geo-housing files.")

for radius, china_housing_result in china_housing_results.items():
    output_geo_files(data=china_housing_result,
                     boundary=china_city_boundary,
                     agg_col=['省级','地名'],
                     anls_col='norm',
                     region=Region.CHINA,
                     level=AggLevel.COUNTY,
                     output_dir=housing_geo_output_dir,
                     output_filename=f"housing_density_{radius}dist.geojson",
                     )

logging.info("Start to output usa geo-housing files.")

for radius, usa_housing_result in usa_housing_results.items():
    output_geo_files(data=usa_housing_result,
                     boundary=usa_county_boundary,
                     agg_col=['NAME_1','NAME_2'],
                     anls_col='norm',
                     region=Region.USA,
                     level=AggLevel.COUNTY,
                     output_dir=housing_geo_output_dir,
                     output_filename=f"housing_density_{radius}dist.geojson",
                     )
