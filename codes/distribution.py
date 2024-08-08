"""
Author: Xander Peng
Date: 2024/7/26
Description: Run this script to analyze the distributions of EVCS in these 3 study areas entirely,
which can be modified according to the specific required analysis.
"""
import codes.utils.configs.city_clusters_config as cluster_config
import codes.utils.configs.gdp_config as gdp_config
# from codes.utils.tools import plot_tool as plot_tool
import codes.utils.tools.io_tool as io_tool
from codes.utils.tools import distribution_tool as dist_tool

'''
Global public EV charging points 
'''
# Configure the global public EV charging points data (see stats from IEA-2022)
GLOBAL_PCP = 2700000  # 2.7 million
EU_PCP = 540000  # 540k
US_PCP = 128000  # 128k
CN_PCP = 1760000  # 1.76 million

SAMPLE_RATIO = (EU_PCP + US_PCP + CN_PCP) / GLOBAL_PCP
# Plot the public PCP distribution in the world
dist_tool.plot_global_pcp(global_pcp=GLOBAL_PCP,
                          europe_pcp=EU_PCP,
                          usa_pcp=US_PCP,
                          cn_pcp=CN_PCP)

''' Calculate the EVCS info of city-clusters '''
# Load the city-level EVCS distribution data
cn_city_gdf = io_tool.load_city_evcs("china")
us_city_gdf = io_tool.load_city_evcs("usa")
eu_city_gdf = io_tool.load_city_evcs("europe")

# Calculate the EVCS info of the city-clusters in China
JJJ_evcs_stat = dist_tool.cal_city_cluster_evcs(region="China",
                                                df=cn_city_gdf,
                                                cluster=cluster_config.JJJ,
                                                css_num_col="css_num",
                                                area_col="area",
                                                city_col="地名")

CSJ_evcs_stat = dist_tool.cal_city_cluster_evcs(region="China",
                                                df=cn_city_gdf,
                                                cluster=cluster_config.CSJ,
                                                css_num_col="css_num",
                                                area_col="area",
                                                city_col="地名")

ZSJ_evcs_stat = dist_tool.cal_city_cluster_evcs(region="China",
                                                df=cn_city_gdf,
                                                cluster=cluster_config.ZSJ,
                                                css_num_col="css_num",
                                                area_col="area",
                                                city_col="地名")

# Calculate the EVCS info of the city-clusters in the Europe
WE_evcs_stat = dist_tool.cal_city_cluster_evcs(region="Europe",
                                               df=eu_city_gdf,
                                               cluster=cluster_config.WE,
                                               css_num_col="eu_cs_num",
                                               area_col="Area",
                                               city_col="COUNTRY")

NE_evcs_stat = dist_tool.cal_city_cluster_evcs(region="Europe",
                                               df=eu_city_gdf,
                                               cluster=cluster_config.NE,
                                               css_num_col="eu_cs_num",
                                               area_col="Area",
                                               city_col="COUNTRY")

# Calculate the EVCS info of the city-clusters in the USA
NM_evcs_stat = dist_tool.cal_city_cluster_evcs(region="USA",
                                               df=us_city_gdf,
                                               cluster=cluster_config.NM,
                                               css_num_col="css_num",
                                               area_col="area",
                                               city_col="HASC_2")

BayArea_evcs_stat = dist_tool.cal_city_cluster_evcs(region="usa",
                                                    df=us_city_gdf,
                                                    cluster=cluster_config.BAY_AREA,
                                                    css_num_col="css_num",
                                                    area_col="area",
                                                    city_col="HASC_2")

''' 
Stats of the collected EVCS dataset
'''
eu_stat_city_names = io_tool.load_europe_stat_cities()
eu_stat_gdf = dist_tool.get_eu_evcs_stat(eu_city_gdf,
                                         eu_stat_city_names)

# Calculate the total number of EVCS in 3 study areas
total_cn_evcs = cn_city_gdf["css_num"].sum()
total_us_evcs = us_city_gdf["css_num"].sum()
# total_eu_evcs = eu_city_gdf["eu_cs_num"].sum()
total_eu_evcs = eu_stat_gdf["eu_cs_num"].sum()

# Plot the collected EVCS distribution
dist_tool.plot_collected_evcs(regional_counts={"China": total_cn_evcs,
                                               "Europe": total_eu_evcs,
                                               "USA": total_us_evcs},
                              cn_cluster_counts={"JJJ": JJJ_evcs_stat["css_num"].sum(),
                                                 "CSJ": CSJ_evcs_stat["css_num"].sum(),
                                                 "ZSJ": ZSJ_evcs_stat["css_num"].sum()},
                              europe_cluster_counts={"NE": NE_evcs_stat["eu_cs_num"].sum(),
                                                     "WE": WE_evcs_stat["eu_cs_num"].sum()},
                              usa_cluster_counts={"NM": NM_evcs_stat["css_num"].sum(),
                                                  "Bay Area": BayArea_evcs_stat["css_num"].sum()})

'''
Explore the association between the EVCS distribution and the GDP of the provinces/states
'''
# Load the state-level EVCS distribution data
cn_state_gdf = io_tool.load_state_evcs("china")
us_state_gdf = io_tool.load_state_evcs("usa")
eu_state_gdf = io_tool.load_state_evcs("europe")

cn_state_gdf['GDP'] = cn_state_gdf['ENG_NAME'].map(lambda x: gdp_config.CN_GDP.get[x])
# Check if there are any missing values in the GDP column, if so, raise an error
if cn_state_gdf['GDP'].isnull().sum() > 0:
    raise ValueError("Missing GDP values in the state-level EVCS distribution data.")

# Plot the regression and get the summary (optional)
# cn_reg = plot_tool.simple_regplot(x=cn_state_gdf['GDP'],
#                                   y=cn_state_gdf['css_num'])
# print(cn_reg.summary())

# Plot China
dist_tool.plot_gdp_evcs(
    region='china',
    dataset=cn_state_gdf,
    x_col='GDP',
    y1_col='css_num',
    y2_col='cs_dense',
    backgroud_color='#fff3e0',
    back_alpha=0.5,
    line1_color='#D7730F',
    line2_color='#546e7a',
    y1_lim=[-1000, 13000],
    y2_lim=[-0.071, 0.9],
    x_nbins=5,
    y1_nbins=5,
    y2_nbins=5,
    x_label='GDP (billion RMB)',
    output=True,
    # fig_height=4,
    # fig_width=8,
)

us_state_gdf['GDP'] = us_state_gdf['NAME_1'].map(lambda x: gdp_config.US_GDP.get[x])
if us_state_gdf['GDP'].isnull().sum() > 0:
    raise ValueError("Missing GDP values in the state-level EVCS distribution data.")

# Plot USA
dist_tool.plot_gdp_evcs(
    region='usa',
    dataset=us_state_gdf,
    x_col='GDP',
    y1_col='css_stat',
    y2_col='cs_dens',
    backgroud_color='#DFE0ED',
    back_alpha=0.2,
    line1_color='#4E5390',
    line2_color='#546e7a',
    y1_lim=[-1000, 14000],
    y2_lim=[-0.071, 0.9],
    x_nbins=7,
    y1_nbins=6,
    y2_nbins=5,
    x_label='GDP (billion US dollars)',
    output=True,
    # fig_height=4,
    # fig_width=8,
)

eu_stat_gdf['GDP'] = eu_state_gdf['country_co'].map(lambda x: gdp_config.EU_GDP.get[x])

# Plot Europe
dist_tool.plot_gdp_evcs(
    region='europe',
    dataset=eu_stat_gdf,
    x_col='GDP',
    y1_col='eu_cs_num',
    y2_col='cs_dense',
    backgroud_color='#EEF1DF',
    back_alpha=0.2,
    line1_color='#5E682E',
    line2_color='#546e7a',
    y1_lim=[-1000, 23000],
    y2_lim=[-0.071, 0.9],
    x_nbins=7,
    y1_nbins=6,
    y2_nbins=5,
    x_label='GDP (billion euros)',
    output=True,
    # fig_height=4,
    # fig_width=8,
)
