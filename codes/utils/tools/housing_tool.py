"""
Author: Xander Peng
Date: 2024/8/11
Description: 
"""
import os

import numpy as np
import pandas as pd
import geopandas as gpd


def data_clean(region: str,
               data: pd.DataFrame
               ):
    def to_float(x):
        try:
            return float(x)
        except ValueError:
            return 0

    data_ = data.copy()
    if region in ['us', 'usa', "USA", "US"]:

        '''Clean wrong data'''
        # Filter wrong data
        data_ = data_.query("homeType not in ['LOT', 'MANUFACTURED']")
        # Transfer price col into float, and filter wrong data
        data_['unitPrice'] = data_['unitPrice'].apply(lambda y: to_float(y))
        data_ = data_[data_['unitPrice'] > 0]

        ''' Sort the data '''
        data_ = data_.sort_values('unitPrice')
        total_num = len(data_)

        # Delete head/tail 5% data
        oidx, didx = round(0.05 * total_num), total_num - round(0.05 * total_num)
        data_ = data_.iloc[oidx: didx]

        return data_

    elif region in ['cn', 'China', 'china', 'CN', 'CHINA']:
        pass

    else:
        raise ValueError('Incorrect region name!')


def load_housing_data(region: str,
                      cn_housing_data_dir = None,
                      us_housing_file_dir = None,):
    if region.lower() == "china":
        if cn_housing_data_dir is None:
            cn_housing_data_dir = r"../data/input/housing//china//"
        cn_housing_file_list = os.listdir(cn_housing_data_dir)
        # Concatenate all the housing data in China
        cn_housing_data = pd.DataFrame()
        for file in cn_housing_file_list:
            current_df = pd.read_csv(cn_housing_data_dir + file,
                                     usecols=['name', 'price', 'wgs_lon', 'wgs_lat'])
            cn_housing_data = pd.concat([cn_housing_data, current_df])

        # Convert the DataFrame to GeoDataFrame
        cn_housing_data_gdf = gpd.GeoDataFrame(cn_housing_data,
                                               geometry=gpd.points_from_xy(cn_housing_data.wgs_lon,
                                                                           cn_housing_data.wgs_lat))
        return cn_housing_data, cn_housing_data_gdf

    elif region.lower() == "usa":
        if us_housing_file_dir is None:
            us_housing_file_dir = r"../data/input/housing//USRealEstate.csv"

        us_housing_data = pd.read_csv(us_housing_file_dir,
                                      usecols=['unitPrice', 'zpid', 'latitude', 'longitude', 'homeType'])
        us_housing_data = data_clean(region="usa", data=us_housing_data)
        us_housing_data_gdf = gpd.GeoDataFrame(us_housing_data,
                                               geometry=gpd.points_from_xy(us_housing_data.longitude,
                                                                           us_housing_data.latitude))
        return us_housing_data, us_housing_data_gdf

    else:
        raise ValueError("Region is not available now.")


def get_county_housing(region: str,
                       bound: gpd.GeoDataFrame,
                       housing_data: gpd.GeoDataFrame,
                       county_field: str or None = None,
                       price_field: str or None = None,
                       sjoin_how='left',
                       sjoin_method='contains',
                       value_type='both'):
    if region in ['us', 'usa', "USA", "US"]:
        county_housing = gpd.sjoin(left_df=bound,
                                   right_df=housing_data.set_crs(
                                       "EPSG: 4326") if housing_data.crs is None else housing_data,
                                   how=sjoin_how,
                                   predicate=sjoin_method)

        if value_type == 'both':
            county_housing_count = pd.pivot_table(data=county_housing,
                                                  index=['NAME_1', 'NAME_2'] if county_field is None else county_field,
                                                  values='unitPrice' if price_field is None else price_field,
                                                  aggfunc='count').reset_index().rename(
                columns={'unitPrice' if price_field is None else price_field: 'count'})
            min_county_housing = pd.pivot_table(data=county_housing,
                                                index=['NAME_1', 'NAME_2'] if county_field is None else county_field,
                                                values='unitPrice' if price_field is None else price_field,
                                                aggfunc='min').reset_index().rename(
                columns={'unitPrice' if price_field is None else price_field: 'min_price'})
            max_county_housing = pd.pivot_table(data=county_housing,
                                                index=['NAME_1', 'NAME_2'] if county_field is None else county_field,
                                                values='unitPrice' if price_field is None else price_field,
                                                aggfunc='max').reset_index().rename(
                columns={'unitPrice' if price_field is None else price_field: 'max_price'})
            mean_county_housing = pd.pivot_table(data=county_housing,
                                                 index=['NAME_1', 'NAME_2'] if county_field is None else county_field,
                                                 values='unitPrice' if price_field is None else price_field,
                                                 aggfunc='mean').reset_index().rename(
                columns={'unitPrice' if price_field is None else price_field: 'mean_price'})
            std_county_housing = pd.pivot_table(data=county_housing,
                                                index=['NAME_1', 'NAME_2'] if county_field is None else county_field,
                                                values='unitPrice' if price_field is None else price_field,
                                                aggfunc='std').reset_index().rename(
                columns={'unitPrice' if price_field is None else price_field: 'std_price'})

            merged_data = pd.merge(left=min_county_housing,
                                   right=max_county_housing,
                                   how='inner',
                                   on=['NAME_1', 'NAME_2'] if county_field is None else county_field)
            merged_data = pd.merge(left=merged_data,
                                   right=county_housing_count,
                                   how='inner',
                                   on=['NAME_1', 'NAME_2'] if county_field is None else county_field).query(
                "count >= 20")
            merged_data = pd.merge(left=merged_data,
                                   right=mean_county_housing,
                                   how='inner',
                                   on=['NAME_1', 'NAME_2'] if county_field is None else county_field)
            merged_data = pd.merge(left=merged_data,
                                   right=std_county_housing,
                                   how='inner',
                                   on=['NAME_1', 'NAME_2'] if county_field is None else county_field)

            return merged_data

    elif region in ['cn', 'China', 'china', 'CN', 'CHINA']:
        county_housing = gpd.sjoin(left_df=bound,
                                   right_df=housing_data.set_crs(
                                       "EPSG: 4326") if housing_data.crs is None else housing_data,
                                   how=sjoin_how,
                                   predicate=sjoin_method)

        if value_type == 'both':
            county_housing_count = pd.pivot_table(data=county_housing,
                                                  index='地名' if county_field is None else county_field,
                                                  values='price' if price_field is None else price_field,
                                                  aggfunc='count').reset_index().rename(
                columns={'price' if price_field is None else price_field: 'count'})
            min_county_housing = pd.pivot_table(data=county_housing,
                                                index='地名' if county_field is None else county_field,
                                                values='price' if price_field is None else price_field,
                                                aggfunc='min').reset_index().rename(
                columns={'price' if price_field is None else price_field: 'min_price'})
            max_county_housing = pd.pivot_table(data=county_housing,
                                                index='地名' if county_field is None else county_field,
                                                values='price' if price_field is None else price_field,
                                                aggfunc='max').reset_index().rename(
                columns={'price' if price_field is None else price_field: 'max_price'})
            mean_county_housing = pd.pivot_table(data=county_housing,
                                                 index='地名' if county_field is None else county_field,
                                                 values='price' if price_field is None else price_field,
                                                 aggfunc='mean').reset_index().rename(
                columns={'price' if price_field is None else price_field: 'mean_price'})
            std_county_housing = pd.pivot_table(data=county_housing,
                                                index='地名' if county_field is None else county_field,
                                                values='price' if price_field is None else price_field,
                                                aggfunc='std').reset_index().rename(
                columns={'price' if price_field is None else price_field: 'std_price'})

            merged_data = pd.merge(left=min_county_housing,
                                   right=max_county_housing,
                                   how='inner',
                                   on='地名' if county_field is None else county_field)
            merged_data = pd.merge(left=merged_data,
                                   right=county_housing_count,
                                   how='inner',
                                   on='地名' if county_field is None else county_field).query("count >= 20")
            merged_data = pd.merge(left=merged_data,
                                   right=mean_county_housing,
                                   how='inner',
                                   on='地名' if county_field is None else county_field)
            merged_data = pd.merge(left=merged_data,
                                   right=std_county_housing,
                                   how='inner',
                                   on='地名' if county_field is None else county_field)
            return merged_data
    else:
        raise ValueError("Incorrect region!")


def match_housing2cs(region: str,
                     buffer: gpd.GeoDataFrame,
                     housing_data: gpd.GeoDataFrame,
                     join_how: str = 'left',
                     join_method: str = 'contains'
                     ):
    if region in ['us', 'usa', "USA", "US"]:
        # Spatial join the EVCS buffer and housing data
        sjoin_data = gpd.sjoin(left_df=buffer,
                               right_df=housing_data,
                               how=join_how,
                               predicate=join_method
                               )
        ''' Since there must be EVCS without join housing unit, filter them '''
        ''' For Matched data '''
        matched_data = sjoin_data.dropna()[[i for i in buffer.columns] + ['unitPrice']].reset_index().rename(
            columns={'index': 'cs_idx'})
        # Cal mean for each cs
        mean_housing = pd.pivot_table(data=matched_data,
                                      index='cs_idx',
                                      #    columns=['NAME_1'],
                                      values='unitPrice',
                                      aggfunc='mean')

        matched_mean_housing = pd.merge(
            left=matched_data.drop_duplicates('cs_idx')[['cs_idx', 'name', 'NAME_1', 'NAME_2']],
            right=mean_housing,
            how='left',
            on='cs_idx')
        if len(matched_mean_housing.dropna()) != len(matched_data.drop_duplicates('cs_idx')):
            raise ValueError('Unmatched dfs!')

        ''' For unmatched data '''
        na_data = sjoin_data[sjoin_data['index_right'].isna()]
        # Find the nearest housing for unmatched ones
        near_housing = gpd.sjoin_nearest(left_df=na_data[[i for i in buffer.columns]],
                                         right_df=housing_data,
                                         how='left',
                                         #   max_distance='100',
                                         distance_col='near_dist'
                                         ).reset_index().drop_duplicates('index').rename(columns={'index': 'cs_idx'})[
            ['name', 'NAME_1', 'NAME_2', 'unitPrice', 'cs_idx']]

        merged_data = pd.concat([matched_mean_housing, near_housing])

        if len(merged_data) != len(sjoin_data.reset_index().drop_duplicates('index')):
            raise ValueError('The length of new merged df is not consistent with that in split dfs!')

        # return merged_data
        return matched_mean_housing

    elif region in ['cn', 'China', 'china', 'CN', 'CHINA']:
        # Spatial join the EVCS buffer and housing data
        sjoin_data = gpd.sjoin(left_df=buffer,
                               right_df=housing_data,
                               how=join_how,
                               predicate=join_method
                               )
        ''' Since there must be EVCS without join housing unit, filter them '''
        ''' For Matched data '''
        matched_data = sjoin_data.dropna()[[i for i in buffer.columns] + ['price']].reset_index().rename(
            columns={'index': 'cs_idx'})
        # Cal mean for each cs
        mean_housing = pd.pivot_table(data=matched_data,
                                      index='cs_idx',
                                      #    columns=['NAME_1'],
                                      values='price',
                                      aggfunc='mean')

        matched_mean_housing = pd.merge(
            left=matched_data.drop_duplicates('cs_idx')[['cs_idx', 'name', 'pname', 'cityname']],
            right=mean_housing,
            how='left',
            on='cs_idx')
        if len(matched_mean_housing.dropna()) != len(matched_data.drop_duplicates('cs_idx')):
            raise ValueError('Unmatched dfs!')

        ''' For unmatched data '''
        na_data = sjoin_data[sjoin_data['index_right'].isna()]
        if len(na_data) == 0:
            pass
        else:
            # Find the nearest housing for unmatched ones
            near_housing = gpd.sjoin_nearest(left_df=na_data[[i for i in buffer.columns]],
                                             right_df=housing_data,
                                             how='left',
                                             #   max_distance='100',
                                             distance_col='near_dist'
                                             ).reset_index().drop_duplicates('index').rename(
                columns={'index': 'cs_idx'})[['name', 'pname', 'cityname', 'price', 'cs_idx']]

        merged_data = pd.concat([matched_mean_housing, near_housing])

        if len(merged_data) != len(sjoin_data.reset_index().drop_duplicates('index')):
            raise ValueError('The length of new merged df is not consistent with that in split dfs!')
        return matched_mean_housing
        # return merged_data