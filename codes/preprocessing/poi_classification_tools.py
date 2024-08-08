"""
Author: Xander Peng
Date: 2024/8/8
Description: 
"""
import os
import zipfile

import pandas as pd
import geopandas as gpd

POI_ROOT_DIR = r'../data/input/poi/'  # The raw POI data should be stored in the subdirectories of this directory.
POI_OUPUT_DIR = r'../data/interim/poi_classified/'



def classify_cn_poi(input_df: pd.DataFrame
                    ):
    """
    Classify the raw POI data (Only for China) into 3 categories: administrative, commercial, and leisure.
    :param input_df:
    :return:
    """
    ''' 1st group: Administrative and public facilities '''
    adm_pf_sql = "(大类 == '汽车服务' and 中类 in ['加油站', '加气站', '充电站', '其它能源站']) \
                  or (大类 == '生活服务' and 中类 == '邮局') \
                  or (大类 in ['医疗保健服务', '政府机构及社会团体', '科教文化服务', '公共设施']) \
                  or (大类 == '道路附属设施' and 中类 == '服务区') \
                  or (大类 == '风景名胜' and 中类 == '教堂') \
                  or (大类 == '交通设施服务' and 小类 not in ['进站口/检票口','出站口','机场出发/到达','站台','售票','退票','改签','公安制证','票务相关','票务相关',\
                    '进港','出港','进站','出站','出入口','停车场入口','停车场出口','停车场出入口','出境','入境'])\
                    "
    adm_pf = input_df.query(adm_pf_sql)
    adm_pf['category'] = 'adm'

    ''' 2nd group: Commercial and business facilities'''
    com_bf_sql = "(大类 == '汽车服务' and 中类 not in ['加油站', '加气站', '充电站', '其它能源站']) \
                  or (大类 in ['汽车销售', '汽车维修', '摩托车服务', '餐饮服务', '购物服务','金融保险服务','公司企业']) \
                  or (大类 == '生活服务' and 中类 != '邮局')"
    com_bf = input_df.query(com_bf_sql)
    com_bf['category'] = 'com'

    ''' 3rd group: Facilities for leisure and tourism '''
    ltf_sql = "(大类 in ['体育休闲服务', '住宿服务']) or (大类 == '风景名胜' and 中类 != '教堂')"
    ltf = input_df.query(ltf_sql)
    ltf['category'] = 'lt'

    return adm_pf,  com_bf, ltf


def classify_china_poi(province_list: list,
                       cn_root_dir: str,
                       cn_output_dir: str
                       ):
    for idp, p in enumerate(province_list):  # Provinces
        # if idp >= 2:
        #     break
        current_dir = cn_root_dir + '\\' + p
        current_dir_files = os.listdir(current_dir)  # Read current provinces files
        ''' Create 3 empty df to store state-lelvel classified poi '''
        state_adm = pd.DataFrame()
        state_com = pd.DataFrame()
        state_ltf = pd.DataFrame()

        for idx, f in enumerate(current_dir_files):  # Process each city-level file in current province
            city_name = f.replace('.txt', '')  # Get this city name
            # Read txt file
            poi = pd.read_csv(current_dir + '\\' + f, sep='\t',
                              usecols=['name', 'pname', 'cityname', 'wgs84_lon', 'wgs84_lat', '大类', '中类', '小类'])
            # Classify the poi in city-level
            adm_pf, com_bf, ltf = classify_cn_poi(poi)
            city_poi = pd.concat([adm_pf, com_bf, ltf])

            # Merge current city level df into the corresponding state-levle df
            state_adm = pd.concat([state_adm, adm_pf])
            state_com = pd.concat([state_com, com_bf])
            state_ltf = pd.concat([state_ltf, ltf])

            ''' Output the classified poi '''
            # Check dir
            state_dir = cn_output_dir + '\\' + p
            if os.path.isdir(state_dir):
                pass
            else:
                os.makedirs(state_dir)

            # Output city-level file
            city_poi.to_csv(state_dir + '\\' + city_name + '.csv')

            # Check if this is the last city in this state (province); and then output state-level file
            if idx == len(current_dir_files) - 1:
                pd.concat([state_adm, state_com, state_ltf]).to_csv(state_dir + '\\' + 'total_poi.csv')


def zipfile_extract(input_dir: str,
                    output_dir: str
                    ):
    ''' Extract zipped file into specified path '''
    file = zipfile.ZipFile(input_dir)
    if os.path.isdir(output_dir):
        pass
    else:
        os.makedirs(output_dir)
    file.extractall(output_dir)


def shp2df(input_dir: str,
           shp_type:str
           ):
    file: gpd.GeoDataFrame = gpd.read_file(input_dir)[['osm_id', 'code', 'fclass', 'geometry']]
    if shp_type == 'point':
        pass
    elif shp_type == 'area':
        file['geometry'] = file.centroid
    else:
        raise ValueError('Incorrect shape type value!')
    # Extract lon and lat
    file['lon'] = file['geometry'].map(lambda x: x.coords[0][0])
    file['lat'] = file['geometry'].map(lambda x: x.coords[0][1])
    # convert into a DataFrame
    file_df = file[['osm_id', 'code', 'fclass', 'lon', 'lat']]
    return file_df


def load_all_shp(input_dir: str,
                 kw_list=None
                 ):
    if kw_list is None:
        kw_list = ['pofw', 'pois', 'traffic', 'transport']
    files = os.listdir(input_dir)  # all files in this dir

    def load_shp_type(kw: str,
                      all_files: list):
        file_list = list(
            filter(lambda x: kw in x and '.shp' in x, all_files))  # Get the 2 shp filename with corresponding type kw
        # print(file_list)
        # Get the shp files with this type
        dfs_type_1: list = list(map(lambda x: shp2df(input_dir=input_dir + '\\' + x,
                                                     shp_type='area' if '_a_' in x else 'point'),
                                    file_list))
        df = pd.concat(dfs_type_1)

        return df

    dfs = [load_shp_type(i, files) for i in kw_list]  # All dfs with 4 types

    return dfs


def classify_osm_poi(
        file1: pd.DataFrame,  # file type 1
        file2: pd.DataFrame,  # file type 2
        file3: pd.DataFrame,  # file type 3
        file4: pd.DataFrame  # file type 4
):
    # Initialize 3 df
    # adm_pf = pd.DataFrame()
    # com_bf = pd.DataFrame()
    # ltf = pd.DataFrame()

    ''' adm_pf class '''
    adm_pf = pd.concat([file1, file4])
    # Filter the file2
    adm_pf = pd.concat([adm_pf, file2.loc[file2['code'].between(2000, 2199)]])
    # Filter the file3
    tem_f3 = file3.query("code in [5250, 5251, 5260, 5261, 5262, 5263, 5270]")
    adm_pf = pd.concat([adm_pf, tem_f3])

    ''' com_bf '''
    com_bf = file2.query("(code >= 2300 & code <= 2307) \
                                 or (code >= 2500 & code <= 2602) \
                                 ")

    ''' ltf '''
    ltf = file2.query("(code >= 2200 & code <= 2206) \
                      or (code >= 2250 & code <= 2257) \
                      or (code >= 2401 & code <= 2406) \
                      or (code >= 2420 & code <= 2424) \
                      or (code >= 2721 & code <= 2744) \
                        ")

    ''' Delete useless cols '''
    adm_pf = adm_pf[['code', 'lon', 'lat']]
    com_bf = com_bf[['code', 'lon', 'lat']]
    ltf = ltf[['code', 'lon', 'lat']]

    return (adm_pf, com_bf, ltf)


def output_class_poi(dfs: list,
                     out_dir: str,
                     is_output: bool = True
                     ):
    flist = ['adm', 'com', 'ltf']
    class_dfs = classify_osm_poi(dfs[0], dfs[1], dfs[2], dfs[3])

    if is_output:
        if os.path.isdir(out_dir):
            pass
        else:
            try:
                os.makedirs(out_dir)
            except:
                os.mkdir(out_dir)
        for f in range(3):
            class_dfs[f].to_csv(out_dir + '\\' + flist[f] + '.csv')

    return class_dfs


def classify_us_poi(usa_root_dir,
                    usa_shp_root_dir,
                    usa_output_dir
                    ):

    us_files = os.listdir(usa_root_dir)  # All (state) files in the USA root dir (including zip and folders)

    zipped_states: list = list(filter(lambda x: '.zip' in x, us_files))
    folders_states: list = list(filter(lambda x: '.zip' not in x, us_files))

    ''' Process zipped states '''
    for zip_state in zipped_states:
        out_state = zip_state.replace('-latest-free.shp.zip', '')
        # Extract the zipped file
        zipfile_extract(input_dir=usa_root_dir + '\\' + zip_state,
                        output_dir=usa_shp_root_dir + '\\' + out_state + '\\')
        # Read shp and convert it into df
        dfs = load_all_shp(usa_shp_root_dir + '\\' + out_state)
        adm, com, ltf = output_class_poi(dfs, usa_output_dir + '\\' + out_state)

    for fstate in folders_states:  # fstate is the state name
        zipped_city = os.listdir(usa_root_dir + '\\' + fstate)  # Get all zipped fname of this state

        # Initialize 3 df
        adm_all = pd.DataFrame()
        com_all = pd.DataFrame()
        ltf_all = pd.DataFrame()

        ''' Process zipped city '''
        for zip_city in zipped_city:  # zip_state is format as the "state-latest-free.shp.zip"
            out_city_name = zip_city.replace('-latest-free.shp.zip', '')
            zipfile_extract(input_dir=usa_root_dir + '\\' + fstate + '\\' + zip_city,
                            output_dir=usa_shp_root_dir + '\\' + fstate + '\\' + out_city_name + '\\')
            dfs = load_all_shp(usa_shp_root_dir + '\\' + fstate + '\\' + out_city_name)

            adm, com, ltf = output_class_poi(dfs,
                                             '',
                                             is_output=False
                                             )

            # Merge city-level df
            adm_all = pd.concat([adm_all, adm])
            com_all = pd.concat([com_all, com])
            ltf_all = pd.concat([ltf_all, ltf])

        # Output state-level df
        adm_all.to_csv(usa_output_dir + '\\' + fstate + '\\' + 'adm.csv')
        com_all.to_csv(usa_output_dir + '\\' + fstate + '\\' + 'com.csv')
        ltf_all.to_csv(usa_output_dir + '\\' + fstate + '\\' + 'ltf.csv')


def classify_eu_poi(eu_root_dir,
                    eu_shp_dir,
                    eu_output_dir
                    ):

    ''' Path '''

    ''' Process the 1st level zipped countries '''
    eu_root_files = os.listdir(eu_root_dir)  # All (country) files in the EU root dir (including zip and folders)

    country_level_1: list = list(filter(lambda x: '.zip' in x, eu_root_files))  # Get zippped filename
    for fname in country_level_1:
        out_fname = fname.replace('-latest-free.shp.zip', '')
        # Extract the zipped file
        zipfile_extract(input_dir=eu_root_dir + '\\' + fname,
                        output_dir=eu_shp_dir + '\\' + out_fname + '\\')
        # Read shp and convert it into df
        dfs = load_all_shp(eu_shp_dir + '\\' + out_fname)
        adm, com, ltf = output_class_poi(dfs, eu_output_dir + '\\' + out_fname)

    ''' Process 1st level folders '''
    folders_level_1: list = list(filter(lambda x: '.zip' not in x, eu_root_files))  # Get country-folder name

    for fname in folders_level_1:  # fname is the country name
        all_states_fname = os.listdir(
            eu_root_dir + '\\' + fname)  # Get all zipped fname and folder name of this country
        sub_folders = list(filter(lambda x: '.zip' not in x,
                                  all_states_fname))  # A list containing sub-folders at this state (might be an empty list)
        zipped_states = list(filter(lambda x: '.zip' in x, all_states_fname))

        ''' Process zipped states '''
        for zip_state in zipped_states:  # zip_state is format as the "state-latest-free.shp.zip"
            out_state_name = zip_state.replace('-latest-free.shp.zip', '')
            zipfile_extract(input_dir=eu_root_dir + '\\' + fname + '\\' + zip_state,
                            output_dir=eu_shp_dir + '\\' + fname + '\\' + out_state_name + '\\')
            dfs = load_all_shp(eu_shp_dir + '\\' + fname + '\\' + out_state_name)
            adm, com, ltf = output_class_poi(dfs, eu_output_dir + '\\' + fname + '\\' + out_state_name)

        ''' Process sub-folders '''
        for folder_state in sub_folders:  # folder_state in the state name
            city_zip_names: list = os.listdir(eu_root_dir + '\\' + fname + '\\' + folder_state)

            # Initialize 3 df
            adm_all = pd.DataFrame()
            com_all = pd.DataFrame()
            ltf_all = pd.DataFrame()

            for city_zip in city_zip_names:  # city-zip is format as " 'cityname'-latest-free.shp.zip "
                out_city = city_zip.replace('-latest-free.shp.zip', '')
                zipfile_extract(input_dir=eu_root_dir + '\\' + fname + '\\' + folder_state + '\\' + city_zip,
                                output_dir=eu_shp_dir + '\\' + fname + '\\' + folder_state + '\\' + out_city + '\\')
                dfs = load_all_shp(eu_shp_dir + '\\' + fname + '\\' + folder_state + '\\' + out_city)
                adm, com, ltf = output_class_poi(dfs, '',
                                                 is_output=False)  # Without output

                # Merge city-level df
                adm_all = pd.concat([adm_all, adm])
                com_all = pd.concat([com_all, com])
                ltf_all = pd.concat([ltf_all, ltf])

            # Output state-level df
            adm_all.to_csv(eu_output_dir + '\\' + fname + '\\' + folder_state + '\\' + 'adm.csv')
            com_all.to_csv(eu_output_dir + '\\' + fname + '\\' + folder_state + '\\' + 'com.csv')
            ltf_all.to_csv(eu_output_dir + '\\' + fname + '\\' + folder_state + '\\' + 'ltf.csv')


