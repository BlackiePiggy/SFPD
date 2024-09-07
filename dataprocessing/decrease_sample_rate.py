import os
import pandas as pd

def resample_file(file_path, sampling_rate=5):
    # 读取CSV文件
    df = pd.read_csv(file_path)

    # 降低采样率，取每sampling_rate行中的第一行
    df_resampled = df.iloc[::sampling_rate, :]

    return df_resampled

def resample_files(input_folder, output_folder, sampling_rate=5):
    # 检查输出文件夹是否存在，如果不存在则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 定义文件名
    train_file = 'train.csv'
    test_file = 'test.csv'
    test_label_file = 'test_label.csv'

    # 处理train.csv
    train_path = os.path.join(input_folder, train_file)
    train_resampled = resample_file(train_path, sampling_rate)
    train_resampled.reset_index(drop=True, inplace=True)
    train_resampled.drop(columns=[train_resampled.columns[0]], inplace=True)  # 删除第一列
    train_resampled.insert(0, 'Timestamp', range(0, len(train_resampled)))  # 插入新的索引列
    train_output_path = os.path.join(output_folder, train_file)
    train_resampled.to_csv(train_output_path, index=False)
    print(f"文件 '{train_file}' 已降采样并保存到 '{train_output_path}'")

    # 获取train.csv最后一行的索引值
    last_index_train = train_resampled.iloc[-1, 0]

    # 处理test.csv
    test_path = os.path.join(input_folder, test_file)
    test_resampled = resample_file(test_path, sampling_rate)
    test_resampled.reset_index(drop=True, inplace=True)
    test_resampled.drop(columns=[test_resampled.columns[0]], inplace=True)  # 删除第一列
    test_resampled.insert(0, 'Timestamp', range(last_index_train + 1, last_index_train + 1 + len(test_resampled)))  # 插入新的索引列
    test_output_path = os.path.join(output_folder, test_file)
    test_resampled.to_csv(test_output_path, index=False)
    print(f"文件 '{test_file}' 已降采样并保存到 '{test_output_path}'")


    # 处理test_label.csv
    test_label_path = os.path.join(input_folder, test_label_file)
    test_label_resampled = resample_file(test_label_path, sampling_rate)
    test_label_resampled.reset_index(drop=True, inplace=True)
    test_label_resampled.drop(columns=[test_label_resampled.columns[0]], inplace=True)  # 删除第一列
    test_label_resampled.insert(0, 'Index', range(last_index_train + 1, last_index_train + 1 + len(test_label_resampled)))  # 插入新的索引列
    test_label_output_path = os.path.join(output_folder, test_label_file)
    test_label_resampled.to_csv(test_label_output_path, index=False)
    print(f"文件 '{test_label_file}' 已降采样并保存到 '{test_label_output_path}'")

# 指定输入和输出文件夹路径
input_folder = 'D:\projects\Anomaly-Transformer\dataset\PSM'
output_folder = 'D:\projects\Anomaly-Transformer\dataset\FP_BAIE_S1W_2019_2020_5per'

# 调用函数进行批量降采样
resample_files(input_folder, output_folder)
