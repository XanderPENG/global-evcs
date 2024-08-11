"""
Author: Xander Peng
Date: 2024/7/26
Description:
"""

import geopandas as gpd
import codes.utils.tools.housing_tool as housing_tool


'''Load the housing data'''
# Load the housing data in China
cn_housing_data, cn_housing_data_gdf = housing_tool.load_housing_data(region="China")
us_housing_data, us_housing_data_gdf = housing_tool.load_housing_data(region="USA")

''' Load the boundary data (county/city level) '''
us_bound = gpd.read_file(r"../data/input/boundary/usa/gadm41_USA_2.shp",
                         include_fields=['NAME_1', 'NAME_2'])
cn_bound = gpd.read_file(r"../data/input/boundary/china/地级.shp",
                         include_fields=['地名', '地级', '省级'])

''' Match housing data with county '''
us_county_housing = housing_tool.get_county_housing(region='us',
                                                    bound=us_bound,
                                                    housing_data=us_housing_data).query("count >= 200")

cn_city_housing = housing_tool.get_county_housing(region='cn',
                                                  bound=cn_bound,
                                                  housing_data=cn_housing_data).query("count >= 200")

''' Match housing price to EVCS; x/Mean'''
# USA
radius_list = [300, 800, 1000]
us_buffer_root = r'../data/interim/evcs_buffers/us//'
us_housing_output_dir = r'../data/output/texts/housing/us//'
for radius in radius_list:
    # Read buffer
    current_buffer = gpd.read_file(us_buffer_root+'us_buffer'+str(radius)+'.shp')
    # Match housing price with buffer
    us_cs_housing = housing_tool.match_housing2cs(region='us',
                                                  buffer=current_buffer,
                                                  housing_data=us_housing_data_gdf)
    us_cs_county_housing = us_cs_housing.merge(us_county_housing,
                                               on=['NAME_1', 'NAME_2'],
                                               how='left')
    # normalization
    us_cs_county_housing['norm'] = us_cs_county_housing['unitPrice'] / us_cs_county_housing['mean_price']
    us_cs_county_housing = us_cs_county_housing.dropna()
    us_county_housing_norm = us_cs_county_housing.groupby('NAME_2')[['norm', 'unitPrice']].mean()

    us_county_housing_norm.to_csv(us_housing_output_dir+str(radius)+'.csv')

# China
cn_buffer_root = r'../data/interim/evcs_buffers/cn//'
cn_housing_output_dir = r'../data/output/texts/housing/china//'
for radius in radius_list:
    # Read buffer
    current_buffer = gpd.read_file(cn_buffer_root+'cn_buffer'+str(radius)+'.shp')
    # Match housing price with buffer
    cn_cs_housing = housing_tool.match_housing2cs(region='cn',
                                                  buffer=current_buffer,
                                                  housing_data=cn_housing_data_gdf)
    cn_cs_city_housing = cn_cs_housing.merge(cn_city_housing,
                                             left_on='cityname',
                                             right_on='地名',
                                             how='left')
    cn_cs_city_housing.dropna(inplace=True)
    # normalization
    cn_cs_city_housing['norm'] = cn_cs_city_housing['price'] / cn_cs_city_housing['mean_price']
    cn_cs_city_housing = cn_cs_city_housing.dropna()
    cn_city_housing_norm = cn_cs_city_housing.groupby('cityname')[['norm', 'price']].mean()

    cn_city_housing_norm.to_csv(cn_housing_output_dir+str(radius)+'.csv')
