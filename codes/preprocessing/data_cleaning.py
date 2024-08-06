"""
Author: Xander Peng
Date: 2024/8/1
Description:
    1. drop the duplicated data
    2. drop the county/city (with data) less than 10
"""
import codes.preprocessing.tools as tool

cn_evcs = tool.load_cn_evcs(tool.CN_EVCS_FOLDER_DIR,
                            usecols=['name', 'pname', 'cityname', 'adname', 'wgs84_lon', 'wgs84_lat'])

cn_evcs = tool.drop_duplicated(cn_evcs,
                               cols=['name', 'adname', 'wgs84_lon', 'wgs84_lat'])

cn_evcs = tool.filter_county(cn_evcs,
                             cols=['pname', 'cityname'],
                             threshold=10)

# cn_evcs.to_csv('filtered_cn_evcs.csv', index=False, encoding='utf-8')


# load EVCS for Europe
eu_evcs = tool.evcp2evcs(tool.EUROPE_EVCS_PATH,
                         )
eu_evcs = tool.drop_duplicated(eu_evcs,
                               cols=['value', 'location_unique_id', 'location_country'])

# Filter the eu_evcs after matching the state
eu_evcs = tool.filter_county(eu_evcs,
                             cols=['pname', 'cityname'],
                             threshold=10)







