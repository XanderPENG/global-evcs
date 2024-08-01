"""
Author: Xander Peng
Date: 2024/8/1
Description: 
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt





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