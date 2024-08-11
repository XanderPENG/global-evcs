"""
Author: Xander Peng
Date: 2024/8/9
Description: 
"""
import os

import pandas as pd
import geopandas as gpd
from matplotlib import pyplot as plt
import codes.utils.configs.city_clusters_config as cluster_config


def load_dataset(region: str,
                 radius_list: list,
                 result_dir: str or None = None
                 ):
    dataset = {}
    if result_dir is None:
        result_dir = r"../data/output/texts/network//"
    if region.lower() == "china":
        for radius in radius_list:
            result = pd.read_csv(result_dir + 'cn/' + str(radius) + '_roads.csv')
            result = result.rename(columns={'Unnamed: 0': 'station_id'})
            ''' Filter cities with more than 10 stations '''
            cn_cs_counts_city = result.groupby('cityname').count().iloc[:, :1]
            cn_filter_city_list = cn_cs_counts_city.query("station_id<=10").index.tolist()
            ''' Clean '''
            result = result.query("cityname not in @cn_filter_city_list")
            dataset[radius] = result
    elif region.lower() == "usa":
        for radius in radius_list:
            result = pd.read_csv(result_dir + 'us/' + str(radius) + '_roads.csv')
            result = result.rename(columns={'Unnamed: 0': 'station_id'})
            ''' Filter cities with more than 10 stations '''
            us_cs_counts_city = result.groupby('NAME_2').count().iloc[:, :1]
            us_filter_city_list = us_cs_counts_city.query("station_id<=10").index.tolist()
            ''' Clean '''
            result = result.query("NAME_2 not in @us_filter_city_list")
            dataset[radius] = result

    elif region.lower() in ["europe", 'eu']:
        eu_country_names = pd.read_excel(r'..data/interim/support/eu_sample_ratio.xlsx',
                                         sheet_name='Sheet2')
        eu_country_names = eu_country_names['country_shp_name'].tolist()

        for radius in radius_list:
            result = pd.read_csv(result_dir + 'eu/' + str(radius) + '_roads.csv')
            result = result.rename(columns={'Unnamed: 0': 'station_id'})
            '''Filter countries'''
            result = result.query("COUNTRY in @eu_country_names")
            ''' Filter cities with more than 10 stations '''
            eu_cs_counts_city = result.groupby('NAME_2').count().iloc[:, :1]
            eu_filter_city_list = eu_cs_counts_city.query("station_id<=10").index.tolist()
            ''' Clean '''
            result = result.query("NAME_2 not in @eu_filter_city_list")
            dataset[radius] = result
    else:
        raise ValueError("Region is not available now.")

    return dataset


def plot_network_comparison(cn_data: dict,
                            us_data: dict,
                            eu_data: dict,
                            output_dir: str
                            ):
    ''' Derive the target values as the data for plotting '''

    region_results = {'cn-300': cn_data.get(300),
                      'cn-800': cn_data.get(800),
                      'cn-1000': cn_data.get(1000),
                      'us-300': us_data.get(300),
                      'us-800': us_data.get(800),
                      'us-1000': us_data.get(1000),
                      'eu-300': eu_data.get(300),
                      'eu-800': eu_data.get(800),
                      'eu-1000': eu_data.get(1000),
                      }

    data = [x['density'] for x in list(region_results.values())]

    plt.style.use('seaborn-whitegrid')
    plt.figure(figsize=(9, 6), dpi=230)

    ''' axes configuration '''
    ax = plt.subplot()

    box_img = ax.boxplot(data,
                         labels=list(region_results.keys()),
                         notch=False,  # whether rectangle
                         patch_artist=True,
                         showbox=True,
                         showfliers=False,
                         boxprops={'facecolor': 'sandybrown'},
                         medianprops={'color': 'lightseagreen'},
                         meanline=True,
                         showmeans=True,
                         meanprops={'color': 'orangered'}
                         )

    samples = [box_img.get('medians')[0], box_img.get('means')[0]]

    box_colors = ['#FFD3A7', '#FFAB57', '#CE7319',
                  '#A6ABCA', '#656EA3', '#3F4569',
                  '#B7BD9D', '#939C6C', '#5C6242'
                  ]

    edge_colors = ['#FFA74F', '#CE7319', '#864300',
                   '#656EA3', '#3F4569', '#171927',
                   '#939C6C', '#5C6242', '#4C5036'
                   ]

    ''' Adjust the color of each box '''
    for i in range(9):
        box = box_img['boxes'][i]
        box.set(edgecolor=edge_colors[i], facecolor=box_colors[i], linewidth=1)

        # 调整相关的线条颜色
        whisker_lines = box_img['whiskers'][i * 2:(i + 1) * 2]
        cap_lines = box_img['caps'][i * 2:(i + 1) * 2]

        # flier_lines = box_img['fliers'][i]

        for line in whisker_lines + cap_lines:
            line.set(color=edge_colors[i])

    # Set face color of 3 groups
    ax.axvspan(0.5, 3.5, facecolor='#FFD3A7', alpha=0.2)
    ax.axvspan(3.5, 6.5, facecolor='#656EA3', alpha=0.15)
    ax.axvspan(6.5, 9.5, facecolor='#939C6C', alpha=0.15)

    ax.legend(handles=samples,
              labels=['Median', 'Mean'],
              prop={'family': 'Times New Roman', 'size': 16},
              loc='upper left',
              # bbox_to_anchor=(1.12, 1.022),

              facecolor='lightgrey',
              # frameon=True
              )

    plt.yticks(fontsize=14,
               fontfamily='Times New Roman')
    ax.set_xticklabels(['300', '800', '1000'] * 3,
                       fontdict={'family': 'Times New Roman', 'size': 14})
    ax.tick_params(axis='both', labelsize=14, pad=8, )

    plt.tight_layout()
    if output_dir is not None:
        os.makedirs(output_dir, exist_ok=True)
        ax.savefig(output_dir + 'network_density_comparison.png')

    plt.show()


def plot_network_ratio_comparison(cn_data: dict,
                                  us_data: dict,
                                  eu_data: dict,
                                  output_dir: str):
    """ Density ratio"""

    ''' Derive the target values as the data for plotting'''

    region_results = {'cn-300': cn_data.get(300),
                      'cn-800': cn_data.get(800),
                      'cn-1000': cn_data.get(1000),
                      'us-300': us_data.get(300),
                      'us-800': us_data.get(800),
                      'us-1000': us_data.get(1000),
                      'eu-300': eu_data.get(300),
                      'eu-800': eu_data.get(800),
                      'eu-1000': eu_data.get(1000),
                      }

    data = [x['density_r'] for x in list(region_results.values())]

    plt.style.use('seaborn-whitegrid')
    plt.figure(figsize=(9, 6), dpi=230)

    ''' axes configuration '''
    ax = plt.subplot()
    box_img = ax.boxplot(data,
                         labels=list(region_results.keys()),
                         notch=False,  # whether rectangle
                         patch_artist=True,
                         showbox=True,
                         showfliers=False,
                         boxprops={'facecolor': 'sandybrown'},
                         medianprops={'color': 'lightseagreen'},
                         meanline=True,
                         showmeans=True,
                         meanprops={'color': 'orangered'}
                         )

    samples = [box_img.get('medians')[0], box_img.get('means')[0]]

    box_colors = ['#FFD3A7', '#FFAB57', '#CE7319',
                  '#A6ABCA', '#656EA3', '#3F4569',
                  '#B7BD9D', '#939C6C', '#5C6242'
                  ]

    edge_colors = ['#FFA74F', '#CE7319', '#864300',
                   '#656EA3', '#3F4569', '#171927',
                   '#939C6C', '#5C6242', '#4C5036'
                   ]

    ''' Adjust the color of each box '''
    for i in range(9):
        box = box_img['boxes'][i]
        box.set(edgecolor=edge_colors[i], facecolor=box_colors[i], linewidth=1)

        # Adjust the color of related lines
        whisker_lines = box_img['whiskers'][i * 2:(i + 1) * 2]
        cap_lines = box_img['caps'][i * 2:(i + 1) * 2]

        # flier_lines = box_img['fliers'][i]

        for line in whisker_lines + cap_lines:
            line.set(color=edge_colors[i])

    # Set face color of 3 groups
    ax.axvspan(0.5, 3.5, facecolor='#FFD3A7', alpha=0.2)
    ax.axvspan(3.5, 6.5, facecolor='#656EA3', alpha=0.15)
    ax.axvspan(6.5, 9.5, facecolor='#939C6C', alpha=0.15)

    ax.legend(handles=samples,
              labels=['Median', 'Mean'],
              prop={'family': 'Times New Roman', 'size': 16},
              loc='upper left',
              # bbox_to_anchor=(1.12, 1.022),

              facecolor='lightgrey',
              # frameon=True
              )

    plt.yticks(fontsize=14,
               fontfamily='Times New Roman')
    ax.set_xticklabels(['300', '800', '1000'] * 3,
                       fontdict={'family': 'Times New Roman', 'size': 14})
    ax.tick_params(axis='both', labelsize=14, pad=8, )
    plt.tight_layout()
    if output_dir is not None:
        os.makedirs(output_dir, exist_ok=True)
        ax.savefig(output_dir + 'network_density_ratio_comparison.png')
    plt.show()


def statMeanMedian(region_dict: dict,
                   den_col: str,
                   den_ratio_col: str
                   ):
    for r in [300, 800, 1000]:
        print(str(r))
        _dataset: pd.DataFrame = region_dict.get(r)
        print('density')
        print("mean: ", _dataset[den_col].mean())
        print("median: ", _dataset[den_col].median())

        print('density_ratio')
        print("mean: ", _dataset[den_ratio_col].mean())
        print("median: ", _dataset[den_ratio_col].median())


def plot_cluster(region: str,
                 plot_type: str,  # density or density_r?
                 county_field: str,
                 region_results: dict,
                 cluster_composition: list,
                 cluster_name: str,
                 print_stats: bool,
                 output_dir: str
                 ):
    cluster_results = {radius: r.query("@county_field in @cluster_composition") for radius, r in region_results}
    if print_stats:
        statMeanMedian(cluster_results, 'density', 'density_r')

    if region.lower() == 'china':
        box_colors = ['#FFD3A7', '#FFAB57', '#CE7319']
        edge_colors = ['#FFA74F', '#CE7319', '#864300']

    elif region.lower() == 'usa':
        box_colors = ['#A6ABCA', '#656EA3', '#3F4569']
        edge_colors = ['#656EA3', '#3F4569', '#171927']

    elif region.lower() in ['eu', 'europe']:
        box_colors = ['#B7BD9D', '#939C6C', '#5C6242']
        edge_colors = ['#939C6C', '#5C6242', '#4C5036']

    else:
        raise ValueError("Region is not available now.")

    ''' Derive the target values as the data for plotting '''

    data = [x['density_r'] for x in list(cluster_results.values())]

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

        # Adjust the color of related lines
        whisker_lines = box_img['whiskers'][i * 2:(i + 1) * 2]
        cap_lines = box_img['caps'][i * 2:(i + 1) * 2]

        # flier_lines = box_img['fliers'][i]

        for line in whisker_lines + cap_lines:
            line.set(color=edge_colors[i])

    plt.yticks(fontsize=14,
               fontfamily='Times New Roman')
    ax.set_xlim(0, 40)

    ax.tick_params(axis='both', labelbottom=False, labelleft=False)
    plt.tight_layout()
    if output_dir is not None:
        os.makedirs(output_dir, exist_ok=True)
        ax.savefig(output_dir + cluster_name + '_' + plot_type + '.png')
    plt.show()


if __name__ == '__main__':
    ''' Load dataset '''
    cn_dataset = load_dataset(region='china',
                              radius_list=[300, 800, 1000],
                              )
    us_dataset = load_dataset(region='usa',
                              radius_list=[300, 800, 1000],
                              )
    '''Add HASC_2 to the us_dataset'''
    us_city_bound = gpd.read_file(r"../data/input/boundary/usa/gadm41_USA_2.shp",
                                  include_fields=['NAME_1', 'NAME_2', 'HASC_2'])
    us_dataset = {r: pd.merge(us_dataset.get(r),
                              us_city_bound,
                              on=['NAME_1', 'NAME_2'],
                              how='left')
                  for r in list(us_dataset.keys())}
    eu_dataset = load_dataset(region='eu',
                              radius_list=[300, 800, 1000],
                              )

    ''' DIR '''
    network_plot_output_dir = r"../data/output/plots/network//"

    ''' Plot the network density comparison (3 study areas) '''
    plot_network_comparison(cn_data=cn_dataset,
                            us_data=us_dataset,
                            eu_data=eu_dataset,
                            output_dir=network_plot_output_dir
                            )

    ''' Plot the network density ratio (relative development) comparison (3 study areas) '''
    plot_network_ratio_comparison(cn_data=cn_dataset,
                                  us_data=us_dataset,
                                  eu_data=eu_dataset,
                                  output_dir=network_plot_output_dir
                                  )

    ''' Plot the cluster;
        Note: Change the plot_type to 'density_r' for network density ratio (relative development);
    '''

    # China
    plot_cluster(region='china',
                 plot_type='density',  # density: network density; density_r: network density ratio (relative development)
                 county_field='cityname',
                 region_results=cn_dataset,
                 cluster_composition=cluster_config.JJJ,
                 cluster_name='JJJ',
                 print_stats=True,
                 output_dir=network_plot_output_dir
                 )

    plot_cluster(region='china',
                 plot_type='density',  # density: network density; density_r: network density ratio (relative development)
                 county_field='cityname',
                 region_results=cn_dataset,
                 cluster_composition=cluster_config.ZSJ,
                 cluster_name='ZSJ',
                 print_stats=True,
                 output_dir=network_plot_output_dir
                 )

    # USA
    plot_cluster(region='usa',
                 plot_type='density',  # density: network density; density_r: network density ratio (relative development)
                 county_field='HASC_2',
                 region_results=us_dataset,
                 cluster_composition=cluster_config.BAY_AREA,
                 cluster_name='BayArea',
                 print_stats=True,
                 output_dir=network_plot_output_dir
                 )

    plot_cluster(region='usa',
                 plot_type='density',  # density: network density; density_r: network density ratio (relative development)
                 county_field='HASC_2',
                 region_results=us_dataset,
                 cluster_composition=cluster_config.NM,
                 cluster_name='NM',
                 print_stats=True,
                 output_dir=network_plot_output_dir
                 )

    # Europe
    plot_cluster(region='eu',
                 plot_type='density',  # density: network density; density_r: network density ratio (relative development)
                 county_field='COUNTRY',
                 region_results=eu_dataset,
                 cluster_composition=cluster_config.WE,
                 cluster_name='WE',
                 print_stats=True,
                 output_dir=network_plot_output_dir
                 )

    plot_cluster(region='eu',
                 plot_type='density',  # density: network density; density_r: network density ratio (relative development)
                 county_field='COUNTRY',
                 region_results=eu_dataset,
                 cluster_composition=cluster_config.NE,
                 cluster_name='NE',
                 print_stats=True,
                 output_dir=network_plot_output_dir
                 )


