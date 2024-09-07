import os
import pandas as pd
import random
from datetime import datetime, timedelta


def generate_test_label_csv(result_df, anomaly_intervals, output_file):
    # 创建一个新的DataFrame，只包含时间戳列
    label_df = pd.DataFrame({'Timestamp': result_df['Timestamp']})

    # 初始化标签列为0
    label_df['Label'] = 0

    # 将时间戳列转换为datetime类型
    label_df['Timestamp'] = pd.to_datetime(label_df['Timestamp'])

    # 遍历异常时间段，将对应的标签设置为1
    for start_time, end_time in anomaly_intervals:
        mask = (label_df['Timestamp'] >= start_time) & (label_df['Timestamp'] <= end_time)
        label_df.loc[mask, 'Label'] = 1

    # 保存为CSV文件
    label_df.to_csv(output_file, index=False)
    print(f"Generated test label file: {output_file}")

def read_anomaly_intervals(anomaly_file):
    anomaly_intervals = []
    with open(anomaly_file, 'r') as file:
        for line in file:
            mode, interval = line.split(': ')
            start_str, end_str = interval.strip().split(', ')
            start_time = pd.to_datetime(start_str)
            end_time = pd.to_datetime(end_str)
            anomaly_intervals.append((start_time, end_time))
    return anomaly_intervals

def concatenate_files_in_range(folder, start_date_str, end_date_str):
    start_date = pd.to_datetime(start_date_str, format='%Y%j')
    end_date = pd.to_datetime(end_date_str, format='%Y%j')
    all_dfs = []

    for file in sorted(os.listdir(folder)):
        try:
            file_date_str = file[5:12]  # 假设文件名中日期格式为 'YYYYDOY'
            file_date = pd.to_datetime(file_date_str, format='%Y%j')
        except ValueError:
            continue

        if start_date <= file_date <= end_date:
            file_path = os.path.join(folder, file)
            df = pd.read_csv(file_path)
            all_dfs.append(df)

    if all_dfs:
        return pd.concat(all_dfs).reset_index(drop=True)
    else:
        return pd.DataFrame()

def read_anomaly_data(folder, anomaly_intervals):
    anomaly_dfs = []
    for start_time, end_time in anomaly_intervals:
        for single_date in pd.date_range(start=start_time, end=end_time):
            file_date_str = single_date.strftime('%Y%j')  # 格式化为 'YYYYDOY'
            for file in os.listdir(folder):
                if file_date_str in file:
                    file_path = os.path.join(folder, file)
                    df = pd.read_csv(file_path)
                    anomaly_dfs.append(df)
    return anomaly_dfs


def insert_anomalies(data_df, anomaly_dfs):
    data_df['Date'] = pd.to_datetime(data_df['Timestamp']).dt.date
    unique_dates = data_df['Date'].unique()

    for anomaly_df in anomaly_dfs:
        if not anomaly_df.empty:
            insertion_date = random.choice(unique_dates)
            insertion_index = data_df[data_df['Date'] == insertion_date].index[-1]
            data_df = pd.concat(
                [data_df.iloc[:insertion_index + 1], anomaly_df, data_df.iloc[insertion_index + 1:]]
            ).reset_index(drop=True)
            print(f"Inserted anomaly data at the end of {insertion_date}")

    data_df = data_df.drop('Date', axis=1)
    return data_df

def process_and_insert_anomalies(SS_variables, satellite_code, time_cn_el_filtered_folder, anomaly_file, anomaly_inserted_folder, time_cn_el_filtered_ano_folder, start_date_str, end_date_str):
    os.makedirs(anomaly_inserted_folder, exist_ok=True)

    # 拼接指定日期范围内的文件
    concatenated_df = concatenate_files_in_range(time_cn_el_filtered_folder, start_date_str, end_date_str)
    if concatenated_df.empty:
        print("No data found in the specified date range.")
        return

    # 读取异常时间段
    anomaly_intervals = read_anomaly_intervals(anomaly_file)

    # 读取异常数据
    anomaly_dfs = read_anomaly_data(time_cn_el_filtered_ano_folder, anomaly_intervals)

    # 插入异常时间段数据
    result_df = insert_anomalies(concatenated_df, anomaly_dfs)

    # 保存结果
    output_file = os.path.join(anomaly_inserted_folder, f"anomaly_inserted_{satellite_code}_{SS_variables[0]}_{start_date_str}_{end_date_str}.csv")
    result_df.to_csv(output_file, index=False)
    print(f"Saved result to {output_file}")

    # 生成test_label.csv
    test_label_file = os.path.join(anomaly_inserted_folder, f"test_label_time_{satellite_code}_{SS_variables[0]}.csv")
    generate_test_label_csv(result_df, anomaly_intervals, test_label_file)

def combine_train_data(SS_variables, satellite_code, time_cn_el_filtered_folder, train_combined_folder, start_date_str, end_date_str):
    os.makedirs(train_combined_folder, exist_ok=True)

    # 拼接指定日期范围内的文件
    concatenated_df = concatenate_files_in_range(time_cn_el_filtered_folder, start_date_str, end_date_str)
    if concatenated_df.empty:
        print("No data found in the specified date range.")
        return

    # 保存结果
    output_file = os.path.join(train_combined_folder, f"combined_{satellite_code}_{SS_variables[0]}_{start_date_str}_{end_date_str}.csv")
    concatenated_df.to_csv(output_file, index=False)
    print(f"Saved result to {output_file}")
