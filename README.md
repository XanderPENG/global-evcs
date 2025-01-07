# Overview
This repository contains all codes and (sample) dataset of the paper - 
***Where Are Public Electric Vehicle Charging Stations Located Globally? Insights from a Spatial Planning Perspective***. 

Note that the **full dataset** can be requested through our [Global EV Data Initiative](https://globalevdata.github.io/data.html).

# Requirements and Installation
The whole analysis-related codes (except for some data collection codes in the dir `./codes/data_collection/...`) 
should run with a **Python** environment, regardless of operating systems theoretically. 
We successfully execute all the codes in both Windows (Win10, Win11) machines and a macOS (Sequoia 15.2) machine.
More detailed info is as below:

## Prerequisites 
It is highly recommended to install and use the following versions of python/packages to run the codes:
- ``python``: 3.10.6
- ``numpy``: 1.26.4
- ``pandas``: 2.2.1
- ``matplotlib``: 3.8.0
- ``seaborn``: 0.12.2
- ``shapely``: 2.0.1
- ``geopandas``: 0.14.2
- ``transbigdata``: 0.5.3
- ``networkx``: 3.1
- ``statsmodels``: 0.14.0
- ``cartopy``: 0.23.0
- ``arcpy``: It is highly recommended to install [ArcGIS Pro](https://www.esri.com/en-us/arcgis/products/arcgis-pro/overview) 
 **with version 2.8** to run the **arcpy-related codes**. 
 Even though the related-functions could also be implemented by other packages (e.g., geopandas), 
 the arcpy package is more efficient and convenient for the spatial analysis and geometry operations.

## Installation
It is highly recommended to download [AnaConda](https://www.anaconda.com) to create/manage Python environments.
You can create a new Python environment and install required aforementioned packages (except for `arcpy`) via both the GUI or Command Line.
Typically, the installation should be prompt (around _10-20 min_ from a "_clean_" machine to "_ready-to-use_" machine, but highly dependent on the Internet speed)
- via **Anaconda GUI**
  1. Open the Anaconda
  2. Find and click "_Environments_" at the left sidebar
  3. Click "_Create_" to create a new Python environment
  4. Select the created Python environment in the list, and then search and install all packages one by one.


- via **Command Line** (using **_Terminal_** for macOS machine and **_Anaconda Prompt_** for Windows machine, respectively)
  1. Create your new Python environment )
     ```
     conda create --name <input_your_environment_name> python=3.10.6
     ```
  2. Activate the new environment 
     ```
     conda activate <input_your_environment_name>
     ```
  3. Install all packages one by one 
     ```
     conda install <package_name>=<specific_version>
     ```

# Usage
1. Git clone/download the repository to your local disk.
2. Unzip the full datasets (which can be provided upon request, see [Overview](https://github.com/XanderPENG/global-evcs?tab=readme-ov-file#overview))
   > The structure of the provided full datasets should look like as below:
   > 
   > ```
   > - gdp
   > - evcs.7z
   > - housing.7z
   > - poiAndNetwork.7z
   > - population.7z
   > ```
3. Unzip each compressed dataset (``.7z`` file) and drag folders/files into corresponding dir of this repo. 
 For example, extract all files from the ``population.7z`` to the dir ``./data/input/population/``.
4. Run
   1. **preprocessing**: run each script in the dir ``./codes/preprocessing``
   2. **analysis**: run each script (shown as below) in the dir ``./codes/`` and some intermediate data 
   will be produced (can be found in the dir ``./data/interim/...``) then 
      > - distribution.py
      > - housing.py
      > - poi.py
      > - pop_coverage.py
      > - road_network.py
   3. **plot**: to plot figures as presented in the manuscript, run each script in the dir ``./codes/plots/``
5. Outputs (including text files and figures) will be stored in the dir ``./data/output/texts/`` and ``./data/output/plots/``, respectively.

# Contact
- Leave questions in [Issues on GitHub](https://github.com/XanderPENG/global-evcs/issues)
- Get in touch with the Corresponding Author: [Dr. Chengxiang Zhuge](mailto:chengxiang.zhuge@polyu.edu.hk)
or visit our research group website: [The TIP](https://thetipteam.editorx.io/website) for more information

# License
This repository is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

