"""
Author: Xander Peng
Date: 2025/3/4
Description: This script is used to generate the geo files (at province/state and city/county levels) for each analysis.
"""
import logging

import numpy as np
import geopandas as gpd
import pandas as pd

from codes.utils.tools.enums import AggLevel, Region
from codes.utils.tools.geo_file_tool import output_geo_files

logging.basicConfig(level=logging.INFO)

logging.info("Start to read boundary.")
''' Boundary '''
china_city_boundary = gpd.read_file(r"../data/input/boundary/china/地级.shp")
usa_county_boundary = gpd.read_file(r"../data/input/boundary/usa/gadm41_USA_2.shp")
europe_city_boundary = gpd.read_file(r"../data/input/boundary/europe/europe_city_boundary.shp.zip")



''' Population '''
def read_pop_data(region: Region):
    logging.info(f"Start to read {region.value} population data.")
    if region == Region.CHINA:
        return pd.read_csv(r"../data/output/texts/population/china_evcs_pop.csv.gz")
    elif region == Region.USA:
        return pd.read_csv(r"../data/output/texts/population/usa_evcs_pop.csv.gz")
    elif region == Region.EUROPE:
        return pd.read_csv(r"../data/output/texts/population/europe_evcs_pop.csv.gz")
    else:
        raise ValueError("Invalid region name.")


def output_region_pop_geo_files(region: Region, pop_results):
    logging.info(f"Start to output {region.value} geo-pop files.")
    pop_geo_output_dir = r"../data/output/geo_files/population"
    if region == Region.CHINA:
        output_geo_files(data=pop_results,
                         boundary=china_city_boundary,
                         agg_col=['省级', '地名'],
                         anls_col='V',
                         region=Region.CHINA,
                         level=AggLevel.COUNTY,
                         output_dir=pop_geo_output_dir,
                         output_filename='population.geojson',
                         )
    elif region == Region.USA:
        output_geo_files(data=pop_results,
                         boundary=usa_county_boundary,
                         agg_col=['NAME_1', 'NAME_2'],
                         anls_col='V',
                         region=Region.USA,
                         level=AggLevel.COUNTY,
                         output_dir=pop_geo_output_dir,
                         output_filename='population.geojson',
                         )
    elif region == Region.EUROPE:
        output_geo_files(data=pop_results,
                         boundary=europe_city_boundary,
                         agg_col=['GID_2'],
                         anls_col='V',
                         region=Region.EUROPE,
                         level=AggLevel.COUNTY,
                         output_dir=pop_geo_output_dir,
                         output_filename='population.geojson',
                         )
    else:
        raise ValueError("Invalid region name.")

''' POI '''


def read_poi_results(region: Region):
    if region == Region.CHINA:
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
            china_poi_results[radius] = cn_poi_results_with_bound_gdf_[
                china_poi_result_.columns.tolist() + ['地名', '地级', '省级']]

        return china_poi_results

    elif region == Region.USA:
        logging.info("Start to read usa poi data.")
        usa_poi_results = {radius: pd.read_csv(f"../data/output/texts/poi/usa/{radius}dist.csv.gz")
                           for radius in [300, 800, 1000]}
        return usa_poi_results

    elif region == Region.EUROPE:
        logging.info("Start to read europe poi data.")
        europe_poi_results = {radius: pd.read_csv(f"../data/output/texts/poi/europe/{radius}dist.csv.gz")
                              for radius in [300, 800, 1000]}

        for radius, eu_result in europe_poi_results.items():
            if eu_result['Mix'].max() == np.inf or eu_result['Mix'].min() == -np.inf:
                logging.warning(f"poi mix has inf value in {radius} radius - delete it.")
                europe_poi_results[radius] = eu_result.query("Mix != inf")
                eu_result.to_csv(f"../data/output/texts/poi/europe/{radius}dist.csv.gz")

        for radius, europe_poi_result_ in europe_poi_results.items():
            eu_poi_results_gdf_ = gpd.GeoDataFrame(europe_poi_result_,
                                                   geometry=gpd.points_from_xy(europe_poi_result_['Longitude'],
                                                                               europe_poi_result_['Latitude']),
                                                   crs="EPSG:4326")
            eu_poi_results_with_bound_gdf_ = gpd.sjoin(eu_poi_results_gdf_,
                                                       europe_city_boundary.drop(columns=['COUNTRY']),
                                                       how='left',
                                                       predicate='within')
            europe_poi_results[radius] = eu_poi_results_with_bound_gdf_[
                europe_poi_result_.columns.tolist() + ['NAME_1', 'NAME_2', 'GID_0', 'GID_2']]
        return europe_poi_results

    else:
        raise ValueError("Invalid region name.")


def output_region_poi_geo_files(region: Region, poi_results):
    logging.info(f"Start to output {region.value} geo-poi files.")
    poi_geo_output_dir = r"../data/output/geo_files/poi"

    if region == Region.CHINA:
        for radius, china_poi_result in poi_results.items():
            output_geo_files(data=china_poi_result,
                             boundary=china_city_boundary,
                             agg_col=['省级', '地名'],
                             anls_col='Mix',
                             region=Region.CHINA,
                             level=AggLevel.COUNTY,
                             output_dir=poi_geo_output_dir,
                             output_filename=f"poi_{radius}dist.geojson",
                             )
    elif region == Region.USA:
        for radius, usa_poi_result in poi_results.items():
            output_geo_files(data=usa_poi_result,
                             boundary=usa_county_boundary,
                             agg_col=['NAME_1', 'NAME_2'],
                             anls_col='Mix',
                             region=Region.USA,
                             level=AggLevel.COUNTY,
                             output_dir=poi_geo_output_dir,
                             output_filename=f"poi_{radius}dist.geojson",
                             )
    elif region == Region.EUROPE:
        for radius, europe_poi_result in poi_results.items():
            output_geo_files(data=europe_poi_result,
                             boundary=europe_city_boundary,
                             agg_col=['GID_2'],
                             anls_col='Mix',
                             region=Region.EUROPE,
                             level=AggLevel.COUNTY,
                             output_dir=poi_geo_output_dir,
                             output_filename=f"poi_{radius}dist.geojson",
                             )
    else:
        raise ValueError("Invalid region name.")


''' Road network '''


def read_road_results(region: Region):
    logging.info(f"Start to read {region.value} road data.")
    if region == Region.CHINA:
        china_road_results = {radius: pd.read_csv(f"../data/output/texts/network/china/{radius}_roads.csv.gz")
                              for radius in [300, 800, 1000]}
        return china_road_results

    elif region == Region.USA:
        usa_road_results = {radius: pd.read_csv(f"../data/output/texts/network/usa/{radius}_roads.csv.gz")
                            for radius in [300, 800, 1000]}
        return usa_road_results

    elif region == Region.EUROPE:
        europe_road_results = {radius: pd.read_csv(f"../data/output/texts/network/europe/{radius}_roads.csv.gz")
                               for radius in [300, 800, 1000]}

        for radius, eu_result in europe_road_results.items():
            if eu_result['city_den_r'].max() == np.inf:
                logging.warning(f"city_den_r has inf value in {radius} radius - delete it.")
                europe_road_results[radius] = eu_result.query("city_den_r != inf")
                eu_result.to_csv(f"../data/output/texts/network/europe/{radius}_roads.csv.gz")

        ''' Since there is no GID_2 field, add it by sjoin with the boundary data '''
        # for radius, europe_road_result_ in europe_road_results.items():
        #     eu_road_results_gdf_ = gpd.GeoDataFrame(europe_road_result_,
        #                                             geometry=gpd.points_from_xy(europe_road_result_['Longitude'],
        #                                                                         europe_road_result_['Latitude']),
        #                                             crs="EPSG:4326")
        #     eu_road_results_with_bound_gdf_ = gpd.sjoin(eu_road_results_gdf_,
        #                                                 europe_city_boundary.drop(
        #                                                     columns=['COUNTRY', 'NAME_1', 'NAME_2']),
        #                                                 how='left',
        #                                                 predicate='within')
        #     europe_road_results[radius] = eu_road_results_with_bound_gdf_[
        #         europe_road_result_.columns.tolist() + ['GID_0', 'GID_2']]

        return europe_road_results

    else:
        raise ValueError("Invalid region name.")


def output_region_road_geo_files(region: Region, road_results):
    logging.info(f"Start to output {region.value} geo-road files.")
    road_geo_output_dir = r"../data/output/geo_files/network"

    if region == Region.CHINA:
        for radius, china_road_result in road_results.items():
            output_geo_files(data=china_road_result,
                             boundary=china_city_boundary,
                             agg_col=['省级', '地名'],
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

    elif region == Region.USA:
        for radius, usa_road_result in road_results.items():
            output_geo_files(data=usa_road_result,
                             boundary=usa_county_boundary,
                             agg_col=['NAME_1', 'NAME_2'],
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

    elif region == Region.EUROPE:
        for radius, europe_road_result in road_results.items():
            output_geo_files(data=europe_road_result,
                             boundary=europe_city_boundary,
                             agg_col=['GID_2'],
                             anls_col='density',
                             region=Region.EUROPE,
                             level=AggLevel.COUNTY,
                             output_dir=road_geo_output_dir,
                             output_filename=f"road_density_{radius}dist.geojson",
                             )

            output_geo_files(data=europe_road_result,
                             boundary=europe_city_boundary,
                             agg_col=['GID_2'],
                             anls_col='city_den_r',
                             region=Region.EUROPE,
                             level=AggLevel.COUNTY,
                             output_dir=road_geo_output_dir,
                             output_filename=f"road_density_ratio_{radius}dist.geojson",
                             )

    else:
        raise ValueError("Invalid region name.")


''' housing '''


def read_housing_results(region: Region):
    logging.info(f"Start to read {region.value} housing data.")
    if region == Region.CHINA:
        china_housing_results = {radius: pd.read_csv(f"../data/output/texts/housing/china/{radius}.csv.gz")
                                 for radius in [300, 800, 1000]}
        return china_housing_results

    elif region == Region.USA:
        usa_housing_results = {radius: pd.read_csv(f"../data/output/texts/housing/usa/{radius}.csv.gz")
                               for radius in [300, 800, 1000]}
        return usa_housing_results

    else:
        raise ValueError("Invalid region name.")


def output_region_housing_geo_files(region: Region, housing_results):
    logging.info(f"Start to output {region.value} geo-housing files.")
    housing_geo_output_dir = r"../data/output/geo_files/housing"

    if region == Region.CHINA:
        for radius, china_housing_result in housing_results.items():
            output_geo_files(data=china_housing_result,
                             boundary=china_city_boundary,
                             agg_col=['省级', '地名'],
                             anls_col='norm',
                             region=Region.CHINA,
                             level=AggLevel.COUNTY,
                             output_dir=housing_geo_output_dir,
                             output_filename=f"housing_density_{radius}dist.geojson",
                             )

    elif region == Region.USA:
        for radius, usa_housing_result in housing_results.items():
            output_geo_files(data=usa_housing_result,
                             boundary=usa_county_boundary,
                             agg_col=['NAME_1', 'NAME_2'],
                             anls_col='norm',
                             region=Region.USA,
                             level=AggLevel.COUNTY,
                             output_dir=housing_geo_output_dir,
                             output_filename=f"housing_density_{radius}dist.geojson",
                             )

    else:
        raise ValueError("Invalid region name.")


if __name__ == '__main__':
    """ population """
    # for region in [
    #     # Region.CHINA,
    #     # Region.USA,
    #     Region.EUROPE
    # ]:
    #     pop_results = read_pop_data(region)
    #     output_region_pop_geo_files(region, pop_results)

    """ poi """
    # for region in [
    #     # Region.CHINA,
    #     # Region.USA,
    #     Region.EUROPE
    # ]:
    #     poi_results = read_poi_results(region)
    #     output_region_poi_geo_files(region, poi_results)

    """ road """
    for region in [
        # Region.CHINA,
        # Region.USA,
        Region.EUROPE
    ]:
        road_results = read_road_results(region)
        output_region_road_geo_files(region, road_results)

    """ housing """
    # for region in [
    #     # Region.CHINA,
    #     # Region.USA
    # ]:
    #     housing_results = read_housing_results(region)
    #     output_region_housing_geo_files(region, housing_results)
