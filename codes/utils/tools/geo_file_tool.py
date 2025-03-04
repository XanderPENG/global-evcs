"""
Author: Xander Peng
Date: 2025/3/4
Description: This script provides the functions to generate the geo files (at province/state and city/county levels)
    for each analysis.
"""

from codes.utils.tools.io_tool import check_output_dir
import pandas as pd
import geopandas as gpd
from codes.utils.tools.enums import AggLevel, Region



def output_geo_files(data: pd.DataFrame,
                     boundary: gpd.GeoDataFrame,
                     # Columns
                     agg_col: list,  # The columns to aggregate
                     anls_col: str,
                     # Enums
                     region: Region,
                     level: AggLevel,
                     # Output Settings
                     output_dir: str,
                     output_filename: str,
                     # merge columns
                     boundary_merge_on=None
                     ):

    # Check the output directory
    check_output_dir(f"{output_dir}//{region.value}")

    # Agg data and get the mean for specific level
    pv_data = data.pivot_table(index=agg_col,
                               values=anls_col,
                               aggfunc='mean').reset_index()

    geo_data = boundary.merge(pv_data,
                                left_on=boundary_merge_on if boundary_merge_on is not None else agg_col,
                                right_on=agg_col,
                                how='left')

    # Output the geo file
    geo_data.to_file(f"{output_dir}//{region.value}//{level.value}_{output_filename}",
                     encoding='utf-8',
                     )

    return geo_data
