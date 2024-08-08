"""
Author: Xander Peng
Date: 2024/8/8
Description: Re-classify the raw POI data into 3 categories: administrative, commercial, and leisure.
"""
import os
import poi_classification_tools as pct


china_prov_folder_list = os.listdir(pct.POI_ROOT_DIR+"china/POI_CityLevel//")

''' Classify the POI data in China and output the results '''
pct.classify_china_poi(province_list=china_prov_folder_list,
                       cn_root_dir=pct.POI_ROOT_DIR+"china/POI_CityLevel//",
                       cn_output_dir=pct.POI_OUPUT_DIR+"china//"
                       )

''' Classify the POI data in the US and output the results '''
pct.classify_us_poi(usa_root_dir=pct.POI_ROOT_DIR+"usa//",
                    usa_shp_root_dir=pct.POI_ROOT_DIR+"usa/shp//",
                    usa_output_dir=pct.POI_OUPUT_DIR+"usa//"
                    )

''' Classify the POI data in the Europe and output the results '''
pct.classify_eu_poi(eu_root_dir=pct.POI_ROOT_DIR+"europe//",
                    eu_shp_dir=pct.POI_ROOT_DIR+"europe/shp//",
                    eu_output_dir=pct.POI_OUPUT_DIR+"europe//"
                    )




