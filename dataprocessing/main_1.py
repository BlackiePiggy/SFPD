import read_CN_from_obs as readCN
import read_el_from_sp3 as readEL
import combine_cn_el as combineCNEL
import elFilter as elft
import anomaly_insert as anomaly_insert
import convert2dataset as c2d

# AIRI 31.824, 130.600, 314.64
# BIK0 42.854, 74.533, 749.2
# BAIE 49.187, -68.263, 27.5
# CAS1 -66.283, 110.520, 22.6
SS_variables = ['S2W']  # ['S1C', 'S1W', 'S2W']
station_llh = [42.854, 74.533, 749.2]  # BAIE站点的经纬高
station_name = 'BIK0'
el_mask = 20  # 高度截止角

for year in range(2022, 2023):  # 遍历2020到2024年
    test_start_date = f'{year}001'
    test_end_date = f'{year}365'

    #########################################文件路径################################################
    #################################test#################################
    test_input_obs_folder = f'F:\\data\\obs\\{station_name}\\{year}'  # 替换为你的输入数据目录路径
    test_input_sp3_dir = f'F:\\data\\sp3\\{year}'
    test_output_cn_folder = f"F:\\data\\1_time_CN\\{year}"  # 替换为你的输出数据目录路径
    test_output_el_folder = f'F:\\data\\2_time_EL\\{year}'
    test_output_cn_el_folder = f'F:\\data\\3_time_CN_EL\\{year}'
    test_time_cn_el_filtered_folder = f'F:\\data\\4_filtered_time_CN\\{year}'
    ######################################################################

    satellite_code = 'all'
    # 第一步：读取所有obs文件，提取CN值，存储到timeCN文件夹中
    readCN.read_CN_value_from_obs_AAO(station_name, SS_variables, satellite_code, test_input_obs_folder, test_output_cn_folder, test_start_date, test_end_date)  # 正常日期

    # 遍历所有卫星代码，1-33是全部卫星
    for i in range(1, 33):
        satellite_code = f'G{i:02d}'  # 格式化卫星代码为"G01"到"G32"

        print(f"Processing for satellite: {satellite_code} in year {year}")

        ############################### test dataset ###############################
        readEL.read_el_from_sp3(station_name, test_input_sp3_dir, test_output_el_folder, satellite_code, station_llh, test_start_date, test_end_date)

        combineCNEL.merge_cn_el_files(station_name, SS_variables, satellite_code, test_output_cn_folder, test_output_el_folder, test_output_cn_el_folder, test_start_date, test_end_date)  # 正常日期

        elft.filter_cn_el_files(station_name, SS_variables, satellite_code, test_output_cn_el_folder, test_time_cn_el_filtered_folder, test_start_date, test_end_date, el_mask)  # 正常日期

        print(f"Test Dataset for {satellite_code} in year {year} Generated Successfully!")
        ######################################################################
