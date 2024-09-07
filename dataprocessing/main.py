import read_CN_from_obs as readCN
import read_el_from_sp3 as readEL
import combine_cn_el as combineCNEL
import elFilter as elft
import anomaly_insert as anomaly_insert
import convert2dataset as c2d

SS_variables = ['S2W'] # ['S1C', 'S1W', 'S2W']
satellite_code = 'G32'

station_llh = [49.187, -68.263, 27.5]  # BAIE站点的经纬高

train_start_date = '2020042'
train_end_date = '2020046'
test_start_date = '2020105'
test_end_date = '2020105'
el_mask = 30 #高度截止角

train_index = 0 #初始化索引
test_index = 0  #初始化索引
#########################################文件路径################################################

##################################train################################
train_input_obs_folder = 'data/traindata/obs'  # 替换为你的输入数据目录路径
train_input_sp3_dir = 'data/traindata/sp3'
train_output_cn_folder = "data/traindata/time_CN"  # 替换为你的输出数据目录路径
train_output_el_folder = 'data/traindata/time_EL'
train_output_cn_el_folder = 'data/traindata/time_CN_EL'
train_time_cn_el_filtered_folder = 'data/traindata/Filtered_time_CN'
train_combined_folder = 'data/traindata/combined'
######################################################################

#################################test#################################
test_input_sp3_dir = 'data/testdata/sp3'
test_input_sp3_ano_dir = 'data/testdata/sp3_ano'
test_output_el_folder = 'data/testdata/time_EL'
test_output_el_ano_folder = 'data/testdata/time_EL_ano'
test_output_cn_el_folder = 'data/testdata/time_CN_EL'
test_output_cn_el_ano_folder = 'data/testdata/time_CN_EL_ano'
test_input_obs_folder = 'data/testdata/obs'  # 替换为你的输入数据目录路径
test_input_obs_ano_folder = 'data/testdata/obs_ano'  # 替换为你的输入数据目录路径
test_output_cn_folder = "data/testdata/time_CN"  # 替换为你的输出数据目录路径
test_output_cn_ano_folder = "data/testdata/time_CN_ano"  # 替换为你的输出数据目录路径
test_time_cn_el_filtered_folder = 'data/testdata/Filtered_time_CN'
test_time_cn_el_filtered_ano_folder = 'data/testdata/Filtered_time_CN_ano'
test_anomaly_file = 'data/anomaly.txt'
test_anomaly_inserted_folder = 'data/testdata/anomaly_inserted'
dataset_folder = 'data/dataset'
######################################################################

########################################主程序##############################################

############################### train dataset ###############################

# 第一步：读取所有obs文件，提取CN值，存储到timeCN文件夹中
# readCN.read_CN_value_from_obs(SS_variables, satellite_code, train_input_obs_folder, train_output_cn_folder, train_start_date, train_end_date) #正常日期
#
# # 第二步：读取所有的sp3文件，插值合并存储到timeEL文件夹中
# readEL.read_el_from_sp3(train_input_sp3_dir, train_output_el_folder, satellite_code, station_llh, train_start_date, train_end_date) #正常日期
#
# # 第三步：合并文件得到time_CN_EL文件夹中
# combineCNEL.merge_cn_el_files(train_output_cn_folder, train_output_el_folder, train_output_cn_el_folder, train_start_date, train_end_date) #正常日期
#
# # 第四步：根据高度截至角得到Filtered_time_CN文件夹中
# elft.filter_cn_el_files(train_output_cn_el_folder, train_time_cn_el_filtered_folder, train_start_date, train_end_date, el_mask) #正常日期
#
# # 第五步：合并文件得到combined文件夹
# anomaly_insert.combine_train_data(SS_variables, satellite_code, train_time_cn_el_filtered_folder, train_combined_folder, train_start_date, train_end_date)
#
# # 第五步： 转换为test.csv和生成test_label.csv
# test_index = c2d.read_and_process_train_files(SS_variables, satellite_code, train_combined_folder, dataset_folder, train_start_date, train_end_date, train_index)
#
# print("Train Dataset Generated Successfully!")
# ############################################################################
#
# ############################### test dataset ###############################
# # 读取anomaly日期
# anomaly_intervals = anomaly_insert.read_anomaly_intervals(test_anomaly_file)

# 第一步：读取所有obs文件，提取CN值，存储到timeCN文件夹中
readCN.read_CN_value_from_obs(SS_variables, satellite_code, test_input_obs_folder, test_output_cn_folder, test_start_date, test_end_date) #正常日期
# for anomaly_interval in anomaly_intervals:
#     readCN.read_CN_value_from_obs(SS_variables, satellite_code, test_input_obs_ano_folder, test_output_cn_ano_folder, anomaly_interval[0], anomaly_interval[0]) #异常日期

# 第二步：读取所有的sp3文件，插值合并存储到timeEL文件夹中
# readEL.read_el_from_sp3(test_input_sp3_dir, test_output_el_folder, satellite_code, station_llh, test_start_date, test_end_date) #正常日期
# for anomaly_interval in anomaly_intervals:
#     readEL.read_el_from_sp3(test_input_sp3_ano_dir, test_output_el_ano_folder, satellite_code, station_llh, anomaly_interval[0], anomaly_interval[0]) #异常日期

# 第三步：合并文件得到time_CN_EL文件夹中
# combineCNEL.merge_cn_el_files(test_output_cn_folder, test_output_el_folder, test_output_cn_el_folder, test_start_date, test_end_date) #正常日期
# for anomaly_interval in anomaly_intervals:
#     combineCNEL.merge_cn_el_files(SS_variables, satellite_code, test_output_cn_ano_folder, test_output_el_ano_folder, test_output_cn_el_ano_folder, anomaly_interval[0], anomaly_interval[0]) #异常日期

# 第四步：根据高度截至角得到Filtered_time_CN文件夹中
# elft.filter_cn_el_files(test_output_cn_el_folder, test_time_cn_el_filtered_folder, test_start_date, test_end_date, el_mask) #正常日期
# for anomaly_interval in anomaly_intervals:
#     elft.filter_cn_el_files(test_output_cn_el_ano_folder, test_time_cn_el_filtered_ano_folder, anomaly_interval[0], anomaly_interval[0], el_mask) #异常日期

# # 第五步：根据Anomaly.txt获取异常日期数据，完成异常值插入
# anomaly_insert.process_and_insert_anomalies(SS_variables, satellite_code, test_time_cn_el_filtered_folder, test_anomaly_file, test_anomaly_inserted_folder, test_time_cn_el_filtered_ano_folder, test_start_date, test_end_date) #正常日期
#
# # 第六步： 转换为test.csv和生成test_label.csv
# c2d.read_and_process_test_files(SS_variables, satellite_code, test_anomaly_inserted_folder, dataset_folder, test_start_date, test_end_date, test_index)

print("Test Dataset Generated Successfully!")
######################################################################