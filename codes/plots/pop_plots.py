"""
Author: Xander Peng
Date: 2024/8/6
Description: Run to plot population-related figures.
"""

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import codes.utils.configs.city_clusters_config as cluster_config


def city_groups(v_file: pd.DataFrame,
                county_field: str
                ):
    # Calculate the average V for each city
    city_avgV: pd.Series = v_file.groupby(county_field)['V'].mean()
    # Group cities based on the V; interval: 0.1
    city_groups = {}
    region_statics = {}
    for i in range(1, 11):
        current_group = city_avgV[city_avgV.between((i - 1) * 0.1, 0.1 * i)]
        city_groups.update({str(round((i - 1) * 0.1, 1)) + '-' + str(round(i * 0.1, 1)): current_group})
        region_statics.update(
            {str(round((i - 1) * 0.1, 1)) + '-' + str(round(i * 0.1, 1)): current_group.count() / city_avgV.count()})

    return city_groups, region_statics


def plot_stat(region: str,
              region_statics: dict,
              output_dir: str or None,
              y_offset: float = 0.008,
              ):
    plt.style.use('seaborn')
    fig, ax = plt.subplots()
    fig.set_dpi(230)
    fig.set_size_inches(12, 8)
    # ax.set_title(region, fontdict={'fontsize': 18,
    #                                'fontfamily': 'Times New Roman',
    #                                'fontweight': 'bold'})

    ax.bar(x=list(region_statics.keys()), height=region_statics.values(),
           color='#55A14A', alpha=0.85)

    ax.set_xlabel('avg_V', fontdict={'fontsize': 16,
                                     'fontfamily': 'Times New Roman',
                                     'fontweight': 'bold'}
                  )

    ax.set_ylabel('ratio', fontdict={'fontsize': 16,
                                     'fontfamily': 'Times New Roman',
                                     'fontweight': 'bold'}
                  )

    plt.tick_params(axis='both', labelsize=13)

    for x, y in zip(range(10), list(region_statics.values())):
        if y != 0:
            ax.text(x, y + y_offset, round(y, 3), fontdict={'fontsize': 12,
                                                            'ha': 'center'})
    plt.tight_layout()
    plt.show()

    if output_dir is not None:
        fig.savefig(output_dir + '\\' + region + '_stat.png')


def plot_all_area_pop(cn_evcs,
                      us_evcs,
                      eu_evcs,
                      output_dir: str,
                      ):
    """
    Plot the population coverage rate of the 3 study areas.
    :param cn_evcs:
    :param us_evcs:
    :param eu_evcs:
    :param output_dir:
    :return:
    """

    ''' horizontal Version '''
    cn1, cn2 = city_groups(cn_evcs, 'cityname')
    us1, us2 = city_groups(us_evcs, 'NAME_2')
    eu1, eu2 = city_groups(eu_evcs, 'NAME_2')

    fig, ax = plt.subplots(figsize=(10, 8),
                           dpi=300)
    height = 0.2
    y_ = np.arange(10)
    cn_values = np.array(list(cn2.values()))
    us_values = np.array(list(us2.values()))
    eu_values = np.array(list(eu2.values()))

    ax.barh(y_ - height,
            list(cn2.values()),
            height=height,

            color='#CC6E0E',
            alpha=0.8,
            label='China'
            )
    ax.barh(y_,
            list(us2.values()),
            height=height,

            color='#9497c5',
            label='USA'
            )
    ax.barh(y_ + height,
            list(eu2.values()),
            height=height,

            color='#95A54A',
            alpha=0.8,
            label='EU'
            )

     def add_poly_fit_line(x_values, y_positions, color, degree=3):
        # 计算多项式拟合
        f = np.polyfit(y_positions, x_values, degree)
        p = np.poly1d(f)
        _x = np.linspace(min(y_positions), max(y_positions), 100)
        yvals = p(_x)
        ax.plot(yvals, _x, color=color, linestyle='--', linewidth=2)
    
    # 调用函数添加多项式拟合线
    add_poly_fit_line(cn_values+0.01, y_ - height, color='#CC6E0E', degree=3)
    add_poly_fit_line(us_values+0.01, y_, color='#9497c5', degree=5)
    add_poly_fit_line(eu_values, y_ + height, color='#95A54A', degree=5)
    ax.set_yticks(y_)
    ax.set_yticklabels(list(cn2.keys()),
                       fontdict={'family': 'Times New Roman',
                                 'size': 14}
                       )
    ax.set_xticks([0, 0.1, 0.2, 0.3, 0.4])
    ax.set_xticklabels([str(round(i, 2)) for i in ax.get_xticks()],
                       fontdict={'fontsize': 14,
                                 'fontfamily': 'Times New Roman',
                                 }
                       )

    ax.set_ylabel('Population coverage rate',
                  fontdict={'fontsize': 18,
                            'fontfamily': 'Times New Roman',
                            'fontweight': 'bold'},
                  labelpad=10

                  )

    ax.set_xlabel('Percentage of cities',
                  fontdict={'fontsize': 18,
                            'fontfamily': 'Times New Roman',
                            'fontweight': 'bold'},
                  # labelpad=12
                  )
    # sns.regplot(x=x_-width, y=list(cn2.values()), ci=None, color='red')
    # sns.regplot(x=x_, y=list(us2.values()), ci=None, color='green')
    # sns.regplot(x=x_+width, y=list(eu2.values()), ci=None, color='blue')

    ax.grid(axis='x', color='grey', linestyle='--')
    ax.tick_params(axis='both', which='both', left=False, bottom=False, top=False)
    ax.spines.clear()

    legend_ = ax.legend(fontsize=16, prop={'size': 16,
                                           'family': 'Times New Roman',
                                           },
                        bbox_to_anchor=(0.88, 1.15),
                        ncol=3,
                        frameon=False,
                        # labelspacing=0.1,
                        columnspacing=6
                        )
    if output_dir is not None:
        os.makedirs(output_dir, exist_ok=True)
        ax.savefig(output_dir + 'pop_coverage_all.png')

    plt.show()


def plot_cluster_pop(region: str,
                     region_evcs: pd.DataFrame,
                     cluster_name: str,
                     cluster: list,
                     city_field: str,
                     cluster_filter_field: str,
                     output_dir: str or None,

                     x_ticks: list,
                     y_ticks: list,
                     bar_alpha: float,
                     ):
    cluster_evcs = region_evcs.loc[region_evcs[cluster_filter_field].isin(cluster)]

    face_color_ = ''
    bar_color_ = ''
    if region.lower() == 'china':
        face_color_ = '#fff3e0'
        bar_color_ = '#E0A56A'
    elif region.lower() == 'usa':
        face_color_ = '#ECEDF4'
        bar_color_ = '#4E5390'
    elif region.lower() == 'europe':
        face_color_ = '#F4F6EA'
        bar_color_ = '#939B6D'
    else:
        raise ValueError('Invalid region name.')

    cluster_1, cluster_2 = city_groups(cluster_evcs,
                                       city_field)

    fig, ax = plt.subplots(figsize=(10, 6),
                           dpi=300)
    ax.set_facecolor(face_color_)
    width = 0.8
    x_ = np.arange(10)

    ax.bar(x_,
           list(cluster_2.values()),
           width=width,
           color=bar_color_,
           alpha=bar_alpha,
           #    label='China'
           )

    ax.set_xticks(x_ticks)

    ax.set_xticklabels([])
    ax.set_yticks(y_ticks)

    ax.set_yticklabels([])

    ax.spines[['right', 'top']].set_visible(False)
    ax.spines[['left', 'bottom']].set_linewidth(0.5)
    if output_dir is not None:
        os.makedirs(output_dir, exist_ok=True)
        fig.savefig(output_dir + cluster_name + '_pop_cluster.png')

    plt.show()


if __name__ == '__main__':
    """ plot the population coverage rate of the 3 study areas """
    cn_evcs = pd.read_csv(r"../data/interim/cleaned_evcs/china_evcs4plot.csv")
    us_evcs = pd.read_csv(r"../data/interim/cleaned_evcs/us_evcs4plot.csv")
    eu_evcs = pd.read_csv(r"../data/interim/cleaned_evcs/eu_evcs4plot.csv")

    output_dir = r"../data/output/plots/pop_coverage/"
    plot_all_area_pop(cn_evcs,
                      us_evcs,
                      eu_evcs,
                      output_dir
                      )

    """ Plot the population coverage rate for clusters """
    ''' China '''
    # China - JJJ
    plot_cluster_pop('china',
                     cn_evcs,
                     'JJJ',
                     cluster_config.JJJ,
                     'cityname',
                     'cityname',
                     output_dir,
                     x_ticks=[0, 4, 9],
                     y_ticks=[0, 0.4, 0.8],
                     bar_alpha=0.8
                     )
    # China - CSJ
    plot_cluster_pop('china',
                     cn_evcs,
                     'CSJ',
                     cluster_config.CSJ,
                     'cityname',
                     'cityname',
                     output_dir,
                     x_ticks=[0, 5, 10],
                     y_ticks=[0, 0.4, 0.8],
                     bar_alpha=0.8
                     )

    # China - ZSJ (PRD)
    plot_cluster_pop('china',
                     cn_evcs,
                     'ZSJ',
                     cluster_config.ZSJ,
                     'cityname',
                     'cityname',
                     output_dir,
                     x_ticks=[0, 4, 9],
                     y_ticks=[0, 0.4, 0.8],
                     bar_alpha=0.8
                     )

    ''' USA'''
    # Match HASC_2 with to the us_evcs
    us_city_gdf = gpd.read_file(r"../data/input/boundary/usa/gadm41_USA_2.shp")
    us_city_gdf = us_city_gdf[['HASC_2', 'NAME_1', 'NAME_2']]
    us_evcs = us_evcs.merge(us_city_gdf, on=['NAME_1', 'NAME_2'], how='left')

    # USA - NE
    plot_cluster_pop('usa',
                     us_evcs,
                     'NE',
                     cluster_config.NE,
                     'NAME_2',
                     'HASC_2',
                     output_dir,
                     x_ticks=[0, 4, 9],
                     y_ticks=[0, 0.4, 0.8],
                     bar_alpha=0.7
                     )

    # USA - Bay Area
    plot_cluster_pop('usa',
                     us_evcs,
                     'BayArea',
                     cluster_config.BAY_AREA,
                     'NAME_2',
                     'HASC_2',
                     output_dir,
                     x_ticks=[0, 4, 9],
                     y_ticks=[0, 0.4, 0.8],
                     bar_alpha=0.7
                     )

    ''' Europe '''
    # Europe - WE
    plot_cluster_pop('europe',
                     eu_evcs,
                     'WE',
                     cluster_config.WE,
                     'NAME_2',
                     'COUNTRY',
                     output_dir,
                     x_ticks=[0, 4, 9],
                     y_ticks=[0, 0.1, 0.2, 0.3],
                     bar_alpha=0.8
                     )

    # Europe - NE
    plot_cluster_pop('europe',
                     eu_evcs,
                     'NE',
                     cluster_config.NE,
                     'NAME_2',
                     'COUNTRY',
                     output_dir,
                     x_ticks=[0, 4, 9],
                     y_ticks=[0, 0.1, 0.2, 0.3],
                     bar_alpha=0.8
                     )
