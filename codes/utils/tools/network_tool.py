"""
Author: Xander Peng
Date: 2024/8/8
Description:
    1. V1 process the raw road shp from osm data
    2. V2 is based on the pre-processed road shp
    3. V3 is just for plotting
"""
import difflib
import os

import numpy as np
import pandas as pd
import geopandas as gpd
from haversine import haversine, Unit


def load_evcs(region: str):
    evcs_dir = r"../data/interim/cleaned_evcs//"

    if region.lower() == "china":
        return pd.read_csv(evcs_dir + 'china_evcs4plot.csv',
                           usecols=['name', 'pname', 'cityname', 'wgs84_lon', 'wgs84_lat', '地名', '地级'])

    elif region.lower() == "usa":
        return pd.read_csv(evcs_dir + 'us_evcs4plot.csv',
                           usecols=['Station Name', 'Latitude', 'Longitude', 'NAME_1', 'NAME_2', 'HASC_2'])

    elif region.lower() in ["europe", 'eu']:
        return pd.read_csv(evcs_dir + 'eu_evcs4plot.csv',
                           usecols=['value', 'location_unique_id',
                                    'location_country', 'location_lng', 'location_lat',
                                    'COUNTRY', 'NAME_1', 'NAME_2'])


def load_road(region: str):
    road_dir = r"../data/input/road//"

    if region.lower() == "china":
        return gpd.read_file(road_dir + 'cn/cn_roads.shp',
                             include_fields=['length', 'fclass'])

    elif region.lower() == "usa":
        raise ValueError("US road network is not available now.")
        # return gpd.read_file(road_dir + 'us/us_roads.shp',
        #                      usecols=['name', 'pname', 'cityname', 'wgs84_lon', 'wgs84_lat', '地名', '地级'])

    elif region.lower() in ["europe", 'eu']:
        raise ValueError("EU road network is not available now.")
        # return pd.read_csv(road_dir + 'eu_roads4plot.csv',
        #                    usecols=['name', 'pname', 'cityname', 'wgs84_lon', 'wgs84_lat', '地名', '地级'])

    else:
        raise ValueError("Region is not available now.")


def load_roads(dirs: str,
               nrows=None
               ):
    """
    Just for EU
    :param dirs:
    :param nrows:
    :return:
    """
    sub_names = os.listdir(dirs)

    filenames = list(filter(lambda x: '.shp' in x and 'roads' in x, sub_names))
    foldernames = list(set(sub_names).difference(filenames))

    if len(filenames) > 1:
        print(dirs)
        raise ValueError('More than one roads.shp in the folder')
    elif len(filenames) == 1:  # Read the roads.shp
        current_roads = gpd.read_file(dirs+'\\'+filenames[0], rows=nrows,
                                      include_fields=['fclass'])
    elif len(filenames) == 0:  # No shpfile in this dir
        if len(foldernames) > 0:
            current_roads = gpd.GeoDataFrame()
            for n in foldernames:
                current_dir = dirs+'\\'+n
                sub_roads = load_roads(current_dir)
                current_roads = pd.concat([current_roads, sub_roads])
            current_roads = gpd.GeoDataFrame(current_roads,
                                             geometry=current_roads['geometry'])
        else:
            raise ValueError('No folders')
        # print(dirs)
        # raise ValueError('No roads.shp in the folder')
    else:
        raise ValueError(dirs)

    return current_roads


def cal_length(geo):

    lat, lon = geo.xy[1].tolist(), geo.xy[0].tolist()
    dists = 0
    for i in range(len(lat)):
        if i+1 != len(lat):
            dist = haversine((lat[i], lon[i]), (lat[i+1], lon[i+1]), unit=Unit.KILOMETERS)
            dists += dist
    return dists


def identify_country(kw: str,
                     l: list):
    results = [(string_similar(kw, f), f) for f in l]
    result_list = list(filter(lambda x: x[0] == max([i[0] for i in results]), results))
    if len(result_list) > 1 or len(result_list) == 0:
        print(kw, ' is not recoginized')
        print(results)

        print(result_list)
        result = input('Incorrect result in the list, plz specify the correct one!')
    else:
        result = result_list[0][1]
        print(result)
    return result


def string_similar(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()


def filter_folder(kw: str,
                  dir_: str):
    folders = os.listdir(dir_)  # all folder name
    results = [(string_similar(kw, f), f) for f in folders]
    result_list = list(filter(lambda x: x[0] == max([i[0] for i in results]), results))
    if len(result_list) > 1 or len(result_list) == 0:
        print(kw, ' is not recoginized')
        print(results)

        print(result_list)
        result = input('Incorrect result in the list, plz specify the correct one!')
    else:
        result = result_list[0][1]
        print(result)
    return result