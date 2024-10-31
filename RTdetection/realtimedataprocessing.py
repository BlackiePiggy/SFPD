import os
import pandas as pd
import numpy as np


def process_satellite_data(folder_path, start_date="2024-06-01", end_date="2024-06-07 23:59:30"):
    """
    处理卫星数据并生成最终结果，保留缺失值

    Parameters:
    folder_path: 数据文件所在文件夹路径
    start_date: 开始日期
    end_date: 结束日期

    Returns:
    DataFrame: 包含所有卫星数据的最终结果表
    """
    # 创建时间索引
    timestamp_range = pd.date_range(start=start_date, end=end_date, freq="30S")
    final_result = pd.DataFrame(timestamp_range, columns=["Timestamp"])

    # 处理G01到G32的所有卫星
    for sat_num in range(1, 33):
        sat = f'G{str(sat_num).zfill(2)}'
        print(f"Processing satellite {sat}...")

        # 获取该卫星的所有文件
        file_list = []
        for file in os.listdir(folder_path):
            if file.endswith(f'{sat}_result.csv'):
                file_list.append(file)

        if not file_list:
            print(f"No files found for satellite {sat}")
            final_result[sat] = pd.NA  # 如果没有找到文件，整列设置为NA
            continue

        # 为每个卫星创建时间表
        time_table = pd.DataFrame(timestamp_range, columns=["Timestamp"])

        # 处理每个测站的数据
        for file in file_list:
            stationname = file.split('_')[0]

            # 读取数据
            try:
                data = pd.read_csv(os.path.join(folder_path, file), parse_dates=[0])
                data['Timestamp'] = pd.to_datetime(data['Timestamp'])

                # 修正时间戳
                for i in range(len(data)):
                    if i == 0 and data.loc[i, 'Timestamp'].second != 30:
                        data.loc[i, 'Timestamp'] = data.loc[i, 'Timestamp'].replace(second=30)
                    elif i > 0 and data.loc[i, 'Timestamp'] == data.loc[i - 1, 'Timestamp']:
                        data.loc[i, 'Timestamp'] += pd.Timedelta(seconds=30)

                # 将数据添加到time_table中
                time_table[stationname] = pd.NA  # 初始化为NA
                for i in range(len(data)):
                    mask = time_table['Timestamp'] == data.loc[i, 'Timestamp']
                    if mask.any():
                        time_table.loc[mask, stationname] = data.loc[i, 'status']

            except Exception as e:
                print(f"Error processing file {file}: {str(e)}")
                continue

        # 计算每个时间戳的平均值并取整，保留NA值
        numeric_columns = time_table.columns[1:]  # 排除Timestamp列
        if len(numeric_columns) > 0:
            # 将所有列转换为float以正确处理NA值
            for col in numeric_columns:
                time_table[col] = pd.to_numeric(time_table[col], errors='coerce')

            # 计算平均值
            means = time_table[numeric_columns].mean(axis=1)

            # 只对非NA值进行取整
            rounded_means = pd.Series(pd.NA, index=means.index, dtype='Int64')
            mask = means.notna()
            rounded_means[mask] = means[mask].round().astype('Int64')

            final_result[sat] = rounded_means
        else:
            final_result[sat] = pd.NA

    return final_result


# 使用示例
if __name__ == "__main__":
    folder_path = r'D:\OneDrive\data\HAL120240601_20240607'

    try:
        # 处理数据
        result = process_satellite_data(folder_path)

        # 保存结果
        result.to_csv('final_satellite_data.csv', index=False)
        print("Processing completed. Results saved to 'final_satellite_data.csv'")

    except Exception as e:
        print(f"An error occurred: {str(e)}")