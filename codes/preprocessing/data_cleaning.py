"""
Author: Xander Peng
Date: 2024/8/1
Description:
    1. drop the duplicated data
    2. drop the county/city (with data) less than 10
"""
import codes.preprocessing.tools as tool
import logging

''' China '''
cn_evcs = tool.load_cn_evcs_v2024(tool.CN_EVCS_FOLDER_DIR,
                                  usecols=['name', 'province', 'city', 'ad', 'wgs84_lng', 'wgs84_lat'])
logging.warning(f"Original EVCS data shape: {cn_evcs.shape}")

cn_evcs = tool.drop_duplicated(cn_evcs,
                               cols=['name', 'ad', 'wgs84_lng', 'wgs84_lat'])
logging.warning(f"Drop duplicated EVCS data shape: {cn_evcs.shape}")

cn_evcs = tool.filter_county(cn_evcs,
                             cols=['province', 'city'],
                             threshold=10)

logging.warning(f"Filtered EVCS data shape: {cn_evcs.shape}")
cn_evcs.to_csv(tool.CN_EVCS_OUTPUT_DIR, encoding='utf-8', compression='gzip')


''' Europe '''
# load EVCS for Europe
eu_evcs = tool.evcp2evcs(filepath=tool.EUROPE_EVCS_PATH)
logging.warning(f"Original EVCS data shape: {eu_evcs.shape}")

eu_evcs = tool.drop_duplicated(eu_evcs,
                               cols=['location_unique_id', 'location_country'])
logging.warning(f"Drop duplicated EVCS data shape: {eu_evcs.shape}")

# Create Europe boundary (both country and city levels)
# tool.create_europe_boundary()

# Load Europe city-level boundary
eu_city_boundary = tool.load_europe_boundary("city")

# Spatial join the EVCS with city boundary
eu_evcs = tool.sjoin_europe_evcs(eu_evcs, eu_city_boundary)

# # Filter the eu_evcs after matching the state
eu_evcs = tool.filter_county(eu_evcs,
                             cols=['location_country', 'NAME_1', 'NAME_2'],
                             threshold=10)
# Drop the geometry column
eu_evcs = eu_evcs.drop(columns=['geometry'])

logging.warning(f"Filtered EVCS data shape: {eu_evcs.shape}")
eu_evcs.to_csv(tool.EUROPE_EVCS_OUTPUT_DIR, encoding='utf-8', compression='gzip')

''' USA'''
# load EVCS for USA
usa_evcs = tool.load_usa_evcs()
logging.warning(f"Original EVCS data shape: {usa_evcs.shape}")

usa_evcs = tool.sjoin_usa_evcs(usa_evcs,
                               r'../data/input/boundary/usa/gadm41_USA_2.shp')

usa_evcs = tool.filter_county(usa_evcs,
                              cols=['NAME_1', 'NAME_2'],
                              threshold=10)

logging.warning(f"Filtered EVCS data shape: {usa_evcs.shape}")
usa_evcs.to_csv(tool.USA_EVCS_OUTPUT_DIR, encoding='utf-8', compression='gzip')





