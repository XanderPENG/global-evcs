"""
Author: Xander Peng
Date: 2024/8/8
Description: Run to plot poi-related figures.
 NOTE: the general figure (comparing the poi mix of 3 study area) is not included in this script, which can be found in
    '../data/output/plots/poi/POI_matrix.excel'
"""

import os
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import codes.utils.configs.city_clusters_config as cluster_config

def city_groups(v_file: pd.DataFrame,
                county_field: str
                ):
    # Calculate the average V for each city
    city_avgV: pd.Series = v_file.groupby(county_field)['Mix'].mean()
    # Group cities based on the V; interval: 0.1
    city_groups = {}
    region_statics = {}
    for i in range(1, 11):
        current_group = city_avgV[city_avgV.between((i - 1) * 0.1, 0.1 * i)]
        city_groups.update({str(round((i - 1) * 0.1, 1)) + '-' + str(round(i * 0.1, 1)): current_group})
        region_statics.update(
            {str(round((i - 1) * 0.1, 1)) + '-' + str(round(i * 0.1, 1)): current_group.count() / city_avgV.count()})

    return city_groups, region_statics


def plot_stat(poi_group_results: dict,  # [str, pd.DataFrame]
              radius_list: list,
              cluster_name: str,
              output_dir: str,
              cluster_composition: list,
              county_field: str,
              region: str = 'non-us'
              ):
    ''' get the cluster results '''
    cluster_results = {}
    for radius in radius_list:
        cluster_poi = poi_group_results.get(radius)
        cluster_poi = cluster_poi.query("@county_field in @cluster_composition")
        if region != 'non-us':
            county_field = 'NAME_2'
        cluster1, cluster2 = city_groups(cluster_poi, county_field)
        cluster_results.update({radius: cluster2})

    ''' Stacked horizontal bar plot '''

    fig, ax = plt.subplots(figsize=(4, 3),
                           dpi=300)
    # ax.set_facecolor('whitesmoke')
    ''' Divide into 10 groups '''
    categories = [str(_) for _ in radius_list]
    groups = []
    for interval in list(cluster_results.get(300).keys()):
        group = []
        for cat in radius_list:
            group.append(cluster_results.get(cat).get(interval))
        groups.append(group)

    groups = np.sum(np.array(groups).reshape(-1, 5, 2, 3), axis=-2).reshape(-1, 3)

    bar_width = 0.6

    colors = ['#caad9d', '#9a8870', '#7dabcf', '#627b7f', '#992813']
    for idx, label_ in enumerate(['0.0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.0']):
        if idx == 0:
            ax.barh(radius_list,
                    groups[idx],
                    height=bar_width,
                    # color=tab20_colors[-(idx*2+1)],
                    color=colors[idx],
                    label=label_)
        elif idx == 1:
            ax.barh(categories, groups[idx], height=bar_width,
                    left=groups[idx - 1],

                    color=colors[idx],
                    label=label_
                    )
        else:
            ax.barh(categories, groups[idx], height=bar_width,
                    left=np.sum(np.array(groups)[:idx, :], axis=0),
                    color=colors[idx],
                    label=label_
                    )

    # ax.set_xlabel('Value')
    # ax.set_ylabel('Radius')

    ax.set_xticks([0, 0.5, 1.0])
    # ax.tick_params(axis='both', which='both',
    #                left=False,
    #                bottom=False,
    #                top=False)
    ax.tick_params(axis='both', labelsize=12, colors='#8A964C')
    # ax.set_xticklabels([])
    # ax.set_yticklabels([])
    # ax.tick_params(axis='both', labelsize=12, colors='#606646')

    # ax.legend(fontsize=16, prop={'size': 16,
    #                              'family': 'Times New Roman',
    #                              },
    #                      bbox_to_anchor=(1.01, 0.9),
    #                      ncol=1,
    #                      frameon=False,
    #                      # labelspacing=0.1,
    #                      columnspacing = 6)
    # ax.spines['left'].set_color('#8A964C')
    # ax.spines['bottom'].set_color('#8A964C')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.tight_layout()

    if output_dir is not None:
        os.makedirs(output_dir, exist_ok=True)
        ax.savefig(output_dir + cluster_name + '.png', dpi=300)

    plt.show()


def load_poi_stats(region: str,
                   poi_stats_dir: str
                   ):
    """
    Load the poi stats data (the analysis results of poi data) from the specified directory.
    :param region:
    :param poi_stats_dir:
    :return:
    """
    if region.lower() in ['cn', 'china']:
        cn_dataset = {}
        for radius in [300, 800, 1000]:
            cn_css_poi = pd.read_csv(poi_stats_dir + 'cn//' + str(radius) + 'dist.csv')
            cn_css_poi = cn_css_poi.rename(columns={'Unnamed: 0': 'station_id'})

            ''' Filter cities with less than 10 EVCS '''
            cn_cs_counts_city = cn_css_poi.groupby('cityname').count().iloc[:, :1]
            cn_filter_city_list = cn_cs_counts_city.query("station_id<=10").index.tolist()
            ''' Clean '''
            cn_css_poi = cn_css_poi.query("cityname not in @cn_filter_city_list")

            cn_dataset.update({radius: cn_css_poi})

        return cn_dataset
    elif region.lower() in ['eu', 'europe']:
        eu_dataset = {}
        for radius in [300, 800, 1000]:
            eu_css_poi = pd.read_csv(poi_stats_dir + 'eu//' + str(radius) + 'dist.csv')
            eu_css_poi = eu_css_poi.rename(columns={'Unnamed: 0': 'station_id'})

            ''' Filter countries '''
            eu_css_poi = eu_css_poi.query("COUNTRY in @eu_country_names")
            ''' Filter cities with less than 10 EVCS '''
            eu_filter_city_list = eu_css_poi.groupby('NAME_2').count().iloc[:, :1].query(
                "station_id<=10").index.tolist()
            eu_css_poi = eu_css_poi.query("NAME_2 not in @eu_filter_city_list")

            eu_dataset.update({radius: eu_css_poi})

        return eu_dataset

    elif region.lower() in ['us', 'usa']:
        us_dataset = {}
        for radius in [300, 800, 1000]:
            us_css_poi = pd.read_csv(poi_stats_dir + 'us//' + str(radius) + 'dist.csv')
            us_css_poi = us_css_poi.rename(columns={'Unnamed: 0': 'station_id'})

            ''' Filter cities with less than 10 EVCS '''
            us_filter_city_list = us_css_poi.groupby('NAME_2').count().iloc[:, :1].query(
                "station_id<=10").index.tolist()
            us_css_poi = us_css_poi.query("NAME_2 not in @us_filter_city_list")

            us_dataset.update({radius: us_css_poi})

        return us_dataset

    else:
        raise ValueError('Region not supported!')

def stats2results(dataset: dict,
                  radius_list: list,
                  county_field: str, ):
    results = {}
    for radius in radius_list:
        r1, r2 = city_groups(dataset.get(radius), county_field)
        r2df = pd.DataFrame.from_dict(r2, orient='index').T
        results.update({radius: r2df})

    return results


if __name__ == '__main__':
    plot_output_dir = r'../data/output/plots/poi//'
    ''' China '''
    # Load the poi stats data
    poi_stats_dir = r'../data/output/texts/poi//'
    cn_dataset = load_poi_stats(region='cn',
                                poi_stats_dir=poi_stats_dir
                                )
    cn_region_results = stats2results(dataset=cn_dataset,
                                      radius_list=[300, 800, 1000],
                                      county_field='cityname'
                                      )
    # Get the stats results of the poi mix at different radius, for the sake of plotting
    for radius in [300, 800, 1000]:
        print(cn_region_results.get(radius))

    # Plot the stats results of each city-cluster
    ## JJJ
    plot_stat(poi_group_results=cn_dataset,
              radius_list=[300, 800, 1000],
              cluster_name='JJJ',
              output_dir=plot_output_dir,
              cluster_composition=cluster_config.JJJ,
              county_field='cityname'
              )

    ## CSJ
    plot_stat(poi_group_results=cn_dataset,
              radius_list=[300, 800, 1000],
              cluster_name='CSJ',
              output_dir=plot_output_dir,
              cluster_composition=cluster_config.CSJ,
              county_field='cityname'
              )

    ## YRD (ZSJ)
    plot_stat(poi_group_results=cn_dataset,
              radius_list=[300, 800, 1000],
              cluster_name='ZSJ',
              output_dir=plot_output_dir,
              cluster_composition=cluster_config.ZSJ,
              county_field='cityname'
              )

    ''' Europe '''
    # Double-check the analysis country list
    eu_country_names = pd.read_excel(r'../data/interim/support/eu_sample_ratio.xlsx',
                                     sheet_name='Sheet2')
    eu_country_names = eu_country_names['country_shp_name'].tolist()
    eu_dataset = load_poi_stats(region='eu',
                                poi_stats_dir=poi_stats_dir
                                )
    eu_region_results = stats2results(dataset=eu_dataset,
                                      radius_list=[300, 800, 1000],
                                      county_field='NAME_2'
                                      )
    # Get the stats results of the poi mix at different radius, for the sake of plotting
    for radius in [300, 800, 1000]:
        print(eu_region_results.get(radius))

    # Plot the stats results of each city-cluster
    ## WE
    plot_stat(poi_group_results=eu_dataset,
              radius_list=[300, 800, 1000],
              cluster_name='WE',
              output_dir=plot_output_dir,
              cluster_composition=cluster_config.WE,
              county_field='NAME_2'
              )

    ## NE
    plot_stat(poi_group_results=eu_dataset,
              radius_list=[300, 800, 1000],
              cluster_name='NE',
              output_dir=plot_output_dir,
              cluster_composition=cluster_config.NE,
              county_field='NAME_2'
              )

    ''' USA '''
    # Load the poi stats data
    us_dataset = load_poi_stats(region='us',
                                poi_stats_dir=poi_stats_dir
                                )
    # Merge the HASC_2 field to the us_dataset
    us_city_gdf = gpd.read_file(r'../data/input/boundary/usa/gadm41_USA_2.shp')
    us_dataset = {radius: us_data.merge(us_city_gdf, how='left', on=['NAME_1', 'NAME_2'])
                  for radius, us_data in us_dataset.items()}

    us_region_results = stats2results(dataset=us_dataset,
                                      radius_list=[300, 800, 1000],
                                      county_field='NAME_2'
                                      )
    # Get the stats results of the poi mix at different radius, for the sake of plotting
    for radius in [300, 800, 1000]:
        print(us_region_results.get(radius))

    # Plot the stats results of each city-cluster
    ## NM
    plot_stat(poi_group_results=us_dataset,
              radius_list=[300, 800, 1000],
              cluster_name='NM',
              output_dir=plot_output_dir,
              cluster_composition=cluster_config.NM,
              county_field='HASC_2',
              region='us'
              )

    ## Bay Area
    plot_stat(poi_group_results=us_dataset,
              radius_list=[300, 800, 1000],
              cluster_name='BayArea',
              output_dir=plot_output_dir,
              cluster_composition=cluster_config.BAY_AREA,
              county_field='HASC_2',
              region='us'
              )
