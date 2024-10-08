import read_CN_from_obs as readCN
import read_el_from_sp3 as readEL
import combine_cn_el as combineCNEL
import elFilter as elft

#############################################参数配置#############################################
# AIRI 31.824, 130.600, 314.64
# BIK0 42.854, 74.533, 749.2
# BAIE 49.187, -68.263, 27.5
# CAS1 -66.283, 110.520, 22.6
SS_variables = ['S2W']  # ['S1C', 'S1W', 'S2W']
station_llh = [42.854, 74.533, 749.2]  # BAIE站点的经纬高
station_name = 'BIK0'
el_mask = 20  # 高度截止角
base_data_path = 'F:\\data' # 数据存储路径
################################################################################################
def generate_satellite_range(prefix, start, end):
    return [f'{prefix}{str(i).zfill(2)}' for i in range(start, end + 1)]

satellite_range = generate_satellite_range('G', 1, 32)

for year in range(2022, 2023):  # 遍历2022到2023年
    test_start_date = f'{year}001'
    test_end_date = f'{year}365'

    #########################################文件路径################################################
    test_input_obs_folder = f'{base_data_path}\\obs\\{station_name}\\{year}'  # 替换为你的输入数据目录路径
    test_input_sp3_dir = f'{base_data_path}\\sp3\\{year}'
    test_output_cn_folder = f"{base_data_path}\\1_time_CN\\{year}"  # 替换为你的输出数据目录路径
    test_output_el_folder = f'{base_data_path}\\2_time_EL\\{year}'
    test_output_cn_el_folder = f'{base_data_path}\\3_time_CN_EL\\{year}'
    test_time_cn_el_filtered_folder = f'{base_data_path}\\4_filtered_time_CN\\{year}'
    ######################################################################

    # 第一步：读取所有obs文件，提取CN值，存储到timeCN文件夹中
    #readCN.read_CN_value_from_obs_AAO(station_name, SS_variables, 'all', test_input_obs_folder, test_output_cn_folder, test_start_date, test_end_date)  # 正常日期

    readEL.read_el_from_sp3(station_name, test_input_sp3_dir, test_output_el_folder, satellite_range, station_llh, test_start_date, test_end_date)

    combineCNEL.merge_cn_el_files(station_name, SS_variables, satellite_range, test_output_cn_folder, test_output_el_folder, test_output_cn_el_folder, test_start_date, test_end_date)  # 正常日期

    elft.filter_cn_el_files(station_name, SS_variables, satellite_range, test_output_cn_el_folder, test_time_cn_el_filtered_folder, test_start_date, test_end_date, el_mask)  # 正常日期

    print(f"Test Dataset for year {year} Generated Successfully!")
    ######################################################################
