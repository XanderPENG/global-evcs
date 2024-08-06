"""
Author: Xander Peng
Date: 2024/8/6
Description: Clean the evcs data after calculate the population coverage,
this version of evcs is for the final plotting
"""
import pandas as pd
import codes.preprocessing.tools as tool

'''China'''
china_evcs = pd.read_csv(r"../data/output/texts/population/china_evcs4plot.csv",
                         usecols=['name', 'pname', 'cityname', 'wgs84_lon',
                                  'wgs84_lat', 'Z', 'V', '地名', '地级'])
china_evcs = tool.filter_county(china_evcs,
                                cols=['pname', 'cityname'],
                                threshold=10)
china_evcs.to_csv(r"../data/interim/cleaned_evcs/china_evcs4plot.csv", encoding='utf-8-sig')

'''Europe'''
europe_evcs = pd.read_csv(r"../data/output/texts/population/eu_evcs4plot.csv",
                          usecols=['value', 'location_unique_id',
                                   'location_country', 'location_lng', 'location_lat',
                                   'COUNTRY', 'NAME_1', 'NAME_2', 'V']
                          )
"""EU countries for analysis"""
eu_country_names = pd.read_excel(r'../css_sample_rate/eu_sample_ratio.xlsx',
                                                   sheet_name='Sheet2')
eu_country_names = eu_country_names['country_shp_name'].tolist()

europe_evcs = europe_evcs.query("COUNTRY in @eu_country_names")

europe_evcs = tool.filter_county(europe_evcs,
                                 cols=['NAME_1', 'NAME_2'],
                                 threshold=10)
europe_evcs.to_csv(r"../data/interim/cleaned_evcs/eu_evcs4plot.csv", encoding='utf-8')

"""USA"""
us_evcs = pd.read_csv(r"../data/output/texts/population/us_evcs4plot.csv",
                      usecols=['Station Name', 'Latitude', 'Longitude', 'NAME_1', 'NAME_2', 'V']
                      )
us_evcs.reset_index(inplace=True)
us_evcs = us_evcs.rename(columns={'index': 'Station_id'})
us_evcs = tool.filter_county(us_evcs,
                             cols=['NAME_1', 'NAME_2'],
                             threshold=10)
us_evcs.to_csv(r"../data/interim/cleaned_evcs/us_evcs4plot.csv", encoding='utf-8')



