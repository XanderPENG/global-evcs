"""
Author: Xander Peng
Date: 2024/8/1
Description: 
"""

import os

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
from statsmodels import api as sm

import codes.utils.tools.io_tool as uio


def plot_worldmap(output_filename: str = 'worldmap.png'):
    """
    Plot the world map with the 3 study areas
    :return: a figure of the world map
    """
    worldmap = uio.load_boundary("world")
    projection = ccrs.Robinson()

    fig, ax = plt.subplots(figsize=(12, 6),
                           dpi=230,
                           subplot_kw={'projection': projection})

    worldmap.to_crs(projection.proj4_init).plot(color="lightgrey", ax=ax)

    ''' 
    Add the 3 study areas
    '''
    # China
    china = uio.load_boundary("china")
    china.to_crs(projection.proj4_init).plot(color="#CC6E0E", ax=ax)

    # USA
    usa = uio.load_boundary("usa")
    usa.to_crs(projection.proj4_init).plot(color="#9497c5", ax=ax)

    # Europe
    europe = uio.load_boundary("europe")
    europe.to_crs(projection.proj4_init).plot(color="#95A54A", ax=ax)

    antarctica = worldmap.query("continent == 'Antarctica'")
    antarctica.to_crs(projection.proj4_init).plot(color='whitesmoke', ax=ax)

    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.axis('off')
    plt.tight_layout()
    # Try to make the output path if it does not exist
    try:
        os.makedirs(uio.global_output_path + "plots/")
    except FileExistsError:
        pass

    fig.savefig(uio.global_output_path + "plots/" + output_filename)
    plt.show()


def simple_regplot(
        x, y, n_std=2, n_pts=100, ax=None, scatter_kws=None, line_kws=None, ci_kws=None
):
    """ Draw a regression line with error interval. """
    ax = plt.gca() if ax is None else ax

    # calculate best-fit line and interval
    x_fit = sm.add_constant(x)
    fit_results = sm.OLS(y, x_fit).fit()

    eval_x = sm.add_constant(np.linspace(np.min(x), np.max(x), n_pts))
    pred = fit_results.get_prediction(eval_x)

    # draw the fit line and error interval
    ci_kws = {} if ci_kws is None else ci_kws
    ax.fill_between(
        eval_x[:, 1],
        pred.predicted_mean - n_std * pred.se_mean,
        pred.predicted_mean + n_std * pred.se_mean,
        alpha=0.5,
        **ci_kws,
    )
    line_kws = {} if line_kws is None else line_kws
    h = ax.plot(eval_x[:, 1], pred.predicted_mean, **line_kws)

    # draw the scatterplot
    scatter_kws = {} if scatter_kws is None else scatter_kws
    ax.scatter(x, y, c=h[0].get_color(), **scatter_kws)

    return fit_results
