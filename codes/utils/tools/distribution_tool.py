"""
Author: Xander Peng
Date: 2024/7/26
Description: 
"""
import os

import pandas as pd
import geopandas as gpd
from typing import List, Dict
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
from codes.utils.tools.io_tool import global_output_path
import seaborn as sns


def cal_city_cluster_evcs(region: str,
                          df: pd.DataFrame or gpd.GeoDataFrame,
                          cluster: List[str],
                          css_num_col: str,
                          area_col: str,
                          city_col: str,
                          ):
    """

    :param region: one of the 3 study areas: 'USA', 'China', 'Europe'
    :param df: the dataframe/GeoDataFrame containing the city and EVCS information;
        see the sample data in ".data/interim/evcs_dist"
    :param cluster:  A list of cities in this city-cluster
    :param css_num_col:  the column name of the EVCS number
    :param area_col: the column name of the area
    :param city_col: the column name of the city
    :return: a tuple of the (total EVCS number， the EVCS density) of this city-cluster
    """
    if region.lower() not in ['usa', 'us']:
        total_css = 0
        total_area = 0
        for city in cluster:
            try:
                # city_css_num = df[df[city_col] == city][css_num_col].values[0]
                city_css_num = df[df[city_col].str.contains(city)][css_num_col].values[0]
                total_css += city_css_num

                # city_area = df[df[city_col] == city][area_col].values[0]
                city_area = df[df[city_col].str.contains(city)][area_col].values[0]
                total_area += city_area
            except IndexError:
                print(city)
                city_rename = input('The correct city name')

                city_css_num = df[df[city_col] == city_rename][css_num_col].values[0]
                total_css += city_css_num

                city_area = df[df[city_col] == city_rename][area_col].values[0]
                total_area += city_area
    else:
        total_css = 0
        total_area = 0
        for city in cluster:
            try:
                # city_css_num = df[df[city_col] == city][css_num_col].values[0]
                city_css_num = df[df[city_col].str.contains(city)][css_num_col].values[0]
                total_css += city_css_num

                # city_area = df[df[city_col] == city][area_col].values[0]
                city_area = df[df[city_col].str.contains(city)][area_col].values[0]
                total_area += city_area
            except IndexError:
                print(city)
                pass

                # city_rename = input('The correct city name')
                # if city_rename is None:
                #     continue
                # city_css_num = df[df[city_col] == city_rename][css_num_col].values[0]
                # total_css += city_css_num

                # city_area = df[df[city_col] == city_rename][area_col].values[0]
                # total_area += city_area
    return total_css, total_css / total_area


def plot_global_pcp(global_pcp: int,
                    cn_pcp: int,
                    europe_pcp: int,
                    usa_pcp: int,
                    output_filename: str = 'global_pcp.png'
                    ):
    fig, ax = plt.subplots(figsize=(6, 4),
                           dpi=300)
    ax.pie([europe_pcp, usa_pcp, cn_pcp, global_pcp - europe_pcp - usa_pcp - cn_pcp],
           #   labels=['EU', 'USA', 'China', 'Others'],
           colors=['#C2CC8E', '#ADB0D3', '#F7C089', 'silver'],
           startangle=30,
           explode=[0.00, 0.00, 0.00, 0.1],

           # shadow={'shade': 0.1, 'color': 'white'},

           wedgeprops={'linewidth': 0.8,
                       'edgecolor': 'snow'}

           )
    plt.tight_layout()
    # Try to make the output path if it does not exist
    try:
        os.makedirs(global_output_path + "plots/" + "distribution/")
    except FileExistsError:
        pass
    fig.savefig(global_output_path + "plots/" + "distribution/" + output_filename)
    plt.show()


def get_eu_evcs_stat(eu_evcs_gdf: gpd.GeoDataFrame,
                     city_names: list,
                     country_col: str = 'COUNTRY'):
    """
    Filter the eu_evcs_gdf to get the EVCS info of the specified cities.
    :param eu_evcs_gdf:
    :param city_names:
    :param country_col:
    :return:
    """

    stat_gdf = eu_evcs_gdf[eu_evcs_gdf[country_col].isin(city_names)]
    return stat_gdf


def plot_collected_evcs(regional_counts: Dict[str, int],
                        cn_cluster_counts: Dict[str, int],
                        europe_cluster_counts: Dict[str, int],
                        usa_cluster_counts: Dict[str, int],
                        output_filename: str = 'collected_evcs_dist.png'
                        ):
    regions = ['China', 'Europe', 'USA']
    region_count = [regional_counts['China'],
                    regional_counts['Europe'],
                    regional_counts['USA']]

    # China
    cn_zones = ['ZSJ', 'CSJ', 'JJJ', 'Others (China)']
    cn_count = [cn_cluster_counts['ZSJ'],
                cn_cluster_counts['CSJ'],
                cn_cluster_counts['JJJ'],
                regional_counts['China'] - sum(cn_cluster_counts.values())]

    cn_colors = ['#F3A353', '#DF770F', '#F6B676', 'gainsboro']

    # Europe
    eu_zones = ['NE', 'WE', 'Others (EU)']
    eu_count = [europe_cluster_counts['NE'],
                europe_cluster_counts['WE'],
                regional_counts['Europe'] - sum(europe_cluster_counts.values())]
    eu_colors = ['#B4C175', '#909E48', 'gainsboro']

    # USA
    usa_zones = ['Bay Area', 'NM', 'Others (USA)']
    usa_count = [usa_cluster_counts['Bay Area'],
                 usa_cluster_counts['NM'],
                 regional_counts['USA'] - sum(usa_cluster_counts.values())]
    usa_colors = ['#A3A6CD', '#989BC8', 'gainsboro']

    ''' Check if the lists contains None values '''
    for count in [region_count, cn_count, eu_count, usa_count]:
        for i in range(len(count)):
            if count[i] is None:
                raise ValueError("The count list contains None values.")

    ''' Configure the figure '''
    fig, ax = plt.subplots(figsize=(5, 5),
                           dpi=300)
    # Plot the outer pie
    ax.pie(cn_count + eu_count + usa_count,
           labels=cn_zones + eu_zones + usa_zones,
           startangle=90,
           autopct='%1.1f%%',
           pctdistance=1.2,
           colors=cn_colors + eu_colors + usa_colors,
           wedgeprops={'edgecolor': 'white'}
           )

    # Plot the intermidiate pie
    ax.pie(region_count,
           # labels=regions,
           autopct='%1.1f%%',
           radius=0.7,
           startangle=90,
           colors=['#F7C089', '#C2CC8E', '#ADB0D3'],
           wedgeprops={'edgecolor': 'white'})

    # Plot the inner pie
    center_circle = plt.Circle((0, 0), 0.3, color='snow')
    ax.add_artist(center_circle)

    ax.axis('equal')

    # Try to make the output path if it does not exist
    try:
        os.makedirs(global_output_path + "plots/" + "distribution/")
    except FileExistsError:
        pass

    fig.savefig(global_output_path + "plots/" + "distribution/" + output_filename)
    plt.show()


def plot_gdp_evcs(dataset: pd.DataFrame or gpd.GeoDataFrame,
                  region: str,
                  x_col: str,  # GDP column name
                  y1_col: str,  # EVCS number
                  y2_col: str,  # EVCS density

                  backgroud_color: str or tuple,
                  back_alpha: float,

                  line1_color: str or tuple,  # EVCS number line
                  line2_color: str or tuple,  # EVCS density line

                  y1_lim: List[float or int],
                  y2_lim: list[float or int],

                  x_nbins: int,  # x-axis bins
                  y1_nbins: int,  # y1-axis bins
                  y2_nbins: int,  # y2-axis bins

                  fig_height=4,
                  fig_width=6,

                  x_label='GDP (billion yuan)',
                  output: bool = False,
                  output_filename='gdp_evcs.png'
                  ):
    # Create a FacetGrid object
    grid = sns.FacetGrid(data=dataset)
    grid.fig.set_figheight(fig_height)
    grid.fig.set_figwidth(fig_width)
    grid.fig.set_dpi(350)

    # Use map function to plot lmplot for the first dataset
    grid.map(sns.regplot,
             x_col,
             y1_col,
             color=line1_color,  # '#D7730F'
             label='EVCS number')

    # Set the y-axis label for the first dataset

    grid.ax.set_ylabel('EVCS number',
                       fontdict={'family': 'Times New Roman'},
                       color='k',
                       fontsize=16,
                       labelpad=4, fontweight='bold')

    grid.ax.set_xlabel(x_label,
                       fontdict={'family': 'Times New Roman'},
                       color='k',
                       fontsize=16,
                       labelpad=4, fontweight='bold')
    # Create a twin axes object
    ax2 = grid.axes.flatten()[0].twinx()

    # Plot lmplot for the second dataset on the twin axes
    sns.regplot(x=x_col,
                y=y2_col,
                data=dataset,
                color=line2_color,  # '#546e7a'
                ax=ax2,
                label='EVCS density')

    # Set the y-axis label for the second dataset
    ax2.set_ylabel('EVCS density (num/km$^{\mathregular{2}}$)',
                   fontdict={'family': 'Times New Roman'},
                   color='k',
                   fontsize=16,
                   labelpad=4,
                   fontweight='bold'
                   )
    ax2.set_xlabel(x_label,
                   fontdict={'family': 'Times New Roman'},
                   color='k',
                   fontsize=16,
                   labelpad=4, fontweight='bold')

    # Remove the right spine of the twin axes
    ax2.spines['right'].set_visible(True)

    grid.ax.set_facecolor(backgroud_color)  # '#fff3e0'
    grid.ax.patch.set_alpha(back_alpha)  # default--0.5

    for tem_yt in grid.ax.get_yticklabels():
        tem_yt.set_family('Times New Roman')
        tem_yt.set_fontsize(13)

    for tem_yt in grid.ax.get_xticklabels():
        tem_yt.set_family('Times New Roman')
        tem_yt.set_fontsize(13)

    for tem_xt in ax2.get_xticklabels():
        tem_xt.set_family('Times New Roman')
        tem_xt.set_fontsize(13)

    for tem_xt in ax2.get_yticklabels():
        tem_xt.set_family('Times New Roman')
        tem_xt.set_fontsize(13)

    grid.ax.set_ylim(y1_lim[0], y1_lim[1])  # -1000, 13000
    ax2.set_ylim(y2_lim[0], y2_lim[1])  # -0.0714, 0.9

    grid.ax.xaxis.set_major_locator(MaxNLocator(nbins=x_nbins))
    grid.ax.yaxis.set_major_locator(MaxNLocator(nbins=y1_nbins))
    ax2.yaxis.set_major_locator(MaxNLocator(nbins=y2_nbins))

    ''' Legend '''
    handles1, labels1 = grid.ax.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    all_handles = handles1 + handles2
    all_labels = labels1 + labels2

    # Style 1:
    legend = grid.ax.legend(all_handles, all_labels,
                            loc='best',
                            markerscale=1.5,
                            frameon=True,
                            facecolor='w',
                            edgecolor='grey',
                            prop={'family': 'Times New Roman',
                                  'size': 12}
                            )
    # legend.get_frame().set_linestyle('--')
    legend.get_frame().set_linewidth(0.5)

    # Adjust the layout
    plt.tight_layout()

    # Show the plot
    plt.show()

    # Save
    if output:
        try:
            os.makedirs(global_output_path + "plots/" + "distribution/")
        except FileExistsError:
            pass
        grid.figure.savefig(global_output_path + "plots/" + "distribution/" + region + "_" + output_filename)
