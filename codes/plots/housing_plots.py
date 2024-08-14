"""
Author: Xander Peng
Date: 2024/8/11
Description: 
"""

import numpy as np
import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
import codes.utils.configs.city_clusters_config as cluster_config

def load_dataset(region: str,
                 radius_list: list = None,
                 root_dir: str = None):
    """
    Load the dataset according to the region
    :param region: str, the region of the dataset
    :return: pd.DataFrame, the dataset
    """
    if root_dir is None:
        root_dir = r"../data/output/texts/housing//"
    if radius_list is None:
        radius_list = [300, 800, 1000]

    dataset = {}
    if region.lower() in ["china", 'cn']:
        for radius in radius_list:
            dataset[radius] = pd.read_csv(root_dir + "china//" + str(radius) + ".csv").dropna()

    elif region.lower() in ['us', "usa"]:
        for radius in radius_list:
            dataset[radius] = pd.read_csv(root_dir + "us//" + str(radius) + ".csv").dropna()

    else:
        raise ValueError("Region is not available now.")

    return dataset


def plot_housing_comparison(cn_dataset: dict,
                            us_dataset: dict,
                            output_dir: str = None
                            ):
    region_results = {'cn-300': cn_dataset.get(300),
                      'cn-800': cn_dataset.get(800),
                      'cn-1000': cn_dataset.get(1000),
                      'us-300': us_dataset.get(300),
                      'us-800': us_dataset.get(800),
                      'us-1000': us_dataset.get(1000),
                      }

    data = [x['norm'] for x in list(region_results.values())]

    plt.style.use('seaborn-whitegrid')
    plt.figure(figsize=(9, 6), dpi=230)

    ''' axes configuration '''
    ax = plt.subplot()
    # ax.set_facecolor('#FFF7EF')
    # ax.set_xlabel('Region', fontsize=23)
    # ax.set_ylabel('Density', fontsize=23)

    box_img = ax.boxplot(data,
                         labels=list(region_results.keys()),
                         notch=False,  # whether rectangle
                         patch_artist=True,
                         showbox=True,
                         showfliers=False,
                         boxprops={'facecolor': 'sandybrown'},
                         medianprops={'color': 'lightseagreen',
                                      'linewidth': 1.5},
                         meanline=True,
                         showmeans=True,
                         meanprops={'color': 'orangered',
                                    'linewidth': 1.5}
                         )

    samples = [box_img.get('medians')[0], box_img.get('means')[0]]

    box_colors = ['#FFD3A7', '#FFAB57', '#CE7319',
                  '#A6ABCA', '#656EA3', '#3F4569',
                  #  '#B7BD9D', '#939C6C', '#5C6242'
                  ]

    edge_colors = ['#FFA74F', '#CE7319', '#864300',
                   '#656EA3', '#3F4569', '#171927',
                   #    '#939C6C', '#5C6242', '#4C5036'
                   ]

    ''' Adjust the color of each box '''
    for i in range(6):
        box = box_img['boxes'][i]
        box.set(edgecolor=edge_colors[i], facecolor=box_colors[i], linewidth=1)

        # Adjust the color of whiskers and caps
        whisker_lines = box_img['whiskers'][i * 2:(i + 1) * 2]
        cap_lines = box_img['caps'][i * 2:(i + 1) * 2]

        # flier_lines = box_img['fliers'][i]

        for line in whisker_lines + cap_lines:
            line.set(color=edge_colors[i])

    # Set face color of 3 groups
    ax.axvspan(0.5, 3.5, facecolor='#FFD3A7', alpha=0.2)
    ax.axvspan(3.5, 6.5, facecolor='#656EA3', alpha=0.15)
    # ax.axvspan(6.5, 9.5, facecolor='#939C6C', alpha=0.15)

    # ax.legend(handles=samples,
    #             labels=['Median', 'Mean'],
    #             prop={'family': 'Times New Roman', 'size':16},
    #             loc='upper left',
    #             # bbox_to_anchor=(1.12, 1.022),

    #             facecolor='lightgrey',
    #             # frameon=True
    #             )
    # ax.set_xticks([1.5, 4.5, 7.5])
    # ax.set_xticklabels(['Group 1', 'Group 2', 'Group 3'])
    # ax.set_xticks([1, 2, 3, 4, 5, 6, 7, 8, 9], minor=True)
    # ax.set_xticklabels(['Data 1', 'Data 2', 'Data 3', 'Data 4', 'Data 5', 'Data 6', 'Data 7', 'Data 8', 'Data 9'], minor=True)
    # ax.set_xticklabels(list(region_results.keys()), fontdict={'fontsize': 18})
    plt.yticks(fontsize=14,
               fontfamily='Times New Roman')
    ax.set_xticklabels(['300', '800', '1000'] * 2,
                       fontdict={'family': 'Times New Roman', 'size': 14})
    ax.tick_params(axis='both', labelsize=14, pad=8, )
    plt.tight_layout()
    if output_dir is not None:
        os.makedirs(output_dir, exist_ok=True)
        ax.savefig(output_dir+'housing_comparison.png')
    plt.show()


def plot_cluster_housing(region: str,
                         region_results: dict,
                         cluster_composition: list,
                         cluster_name: str,
                         county_field: str,
                         us_city_gdf: gpd.GeoDataFrame or None = None,
                         output_dir: str = None
                         ):
    if region.lower() in ["china", 'cn']:
        cluster_results = {radius: r.query("@county_field in @ cluster_composition")
                           for radius, r in region_results.items()}
        box_colors = ['#FFD3A7', '#FFAB57', '#CE7319',
                      ]

        edge_colors = ['#FFA74F', '#CE7319', '#864300',
                       ]
    elif region.lower() in ["usa", 'us']:
        assert us_city_gdf is not None, "US city data is required."
        cluster_results = {radius: r.merge(us_city_gdf[['NAME_2', 'NAME_1', 'HASC_2']],
                                           on='NAME_2',
                                           how='left').query("@county_field in @cluster_composition")
                           for radius, r in region_results.items()}
        box_colors = ['#A6ABCA', '#656EA3', '#3F4569',
                      ]

        edge_colors = ['#656EA3', '#3F4569', '#171927',
                       ]
    else:
        raise ValueError("Region is not available now.")


    ''' Plot '''
    ''' Derive the target values as the data for plotting '''

    data = [x['norm'] for x in list(cluster_results.values())]

    plt.style.use('seaborn-whitegrid')
    plt.figure(figsize=(9, 6), dpi=230)

    ''' axes configuration '''
    ax = plt.subplot()

    box_img = ax.boxplot(data,
                         labels=list(cluster_results.keys()),
                         notch=False,  # whether rectangle
                         patch_artist=True,
                         showbox=True,
                         showfliers=False,
                         boxprops={'facecolor': 'sandybrown'},
                         medianprops={'color': 'lightseagreen'},
                         meanline=True,
                         showmeans=True,
                         meanprops={'color': 'orangered'},
                         vert=False,
                         widths=0.8
                         )

    samples = [box_img.get('medians')[0], box_img.get('means')[0]]


    ''' Adjust the color of each box '''
    for i in range(3):
        box = box_img['boxes'][i]
        box.set(edgecolor=edge_colors[i], facecolor=box_colors[i], linewidth=1)

        # Adjust the color of whiskers and caps
        whisker_lines = box_img['whiskers'][i * 2:(i + 1) * 2]
        cap_lines = box_img['caps'][i * 2:(i + 1) * 2]

        # flier_lines = box_img['fliers'][i]

        for line in whisker_lines + cap_lines:
            line.set(color=edge_colors[i])

    plt.yticks(fontsize=14,
               fontfamily='Times New Roman')
    # ax.set_xlim(0.5, 1.5)

    # ax.tick_params(axis='both', labelbottom=False, labelleft=False)
    plt.tight_layout()
    if output_dir is not None:
        os.makedirs(output_dir, exist_ok=True)
        ax.savefig(output_dir + cluster_name + '_housing.png')
    plt.show()


if __name__ == '__main__':
    ''' Load the dataset '''
    us_dataset = load_dataset(region="us")
    cn_dataset = load_dataset(region="cn")

    ''' Plot the housing price distribution '''
    plot_housing_comparison(cn_dataset=cn_dataset,
                            us_dataset=us_dataset,
                            output_dir=r"../data/output/plots/housing//")

    ''' Load the USA city data '''
    us_city_gdf = gpd.read_file(r"../data/input/boundary/usa/gadm41_USA_2.shp",
                                include_fields=['NAME_1', 'NAME_2', 'HASC_2'])

    ''' Plot the housing price distribution in the clusters '''
    # USA
    plot_cluster_housing(region="us",
                         region_results=us_dataset,
                         cluster_composition=cluster_config.NM,
                         cluster_name="NM",
                         county_field="HASC_2",
                         us_city_gdf=us_city_gdf,
                         output_dir=r"../data/output/plots/housing//")
    plot_cluster_housing(region="us",
                            region_results=us_dataset,
                            cluster_composition=cluster_config.BAY_AREA,
                            cluster_name="BayArea",
                            county_field="HASC_2",
                            us_city_gdf=us_city_gdf,
                            output_dir=r"../data/output/plots/housing//")
    # China
    plot_cluster_housing(region="cn",
                         region_results=cn_dataset,
                         cluster_composition=cluster_config.JJJ,
                         cluster_name="JJJ",
                         county_field="cityname",
                         output_dir=r"../data/output/plots/housing//")
    plot_cluster_housing(region="cn",
                            region_results=cn_dataset,
                            cluster_composition=cluster_config.CSJ,
                            cluster_name="CSJ",
                            county_field="cityname",
                            output_dir=r"../data/output/plots/housing//")
    plot_cluster_housing(region="cn",
                            region_results=cn_dataset,
                            cluster_composition=cluster_config.ZSJ,
                            cluster_name="ZSJ",
                            county_field="cityname",
                            output_dir=r"../data/output/plots/housing//")
