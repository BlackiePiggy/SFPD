import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta
import os
import re
from thresholdlib import ThresholdMethod, ThresholdCalculator, check_threshold_violation


def process_signal_data(folder_path, stationname, year, signal, satellite_range, initial_date, threshold_method,
                        threshold_params):
    """
    处理信号数据的主函数
    """
    # 初始化阈值计算器
    threshold_calculator = ThresholdCalculator(
        method=threshold_method,
        params=threshold_params
    )

    # 转换卫星范围为正则匹配的字符串
    satellite_pattern = '|'.join([f"G{str(i).zfill(2)}" for i in satellite_range])

    # 正则表达式模式
    pattern = re.compile(f"{stationname}_{year}_{signal}_({satellite_pattern}).csv")

    # 遍历文件夹中的所有CSV文件
    for file_name in os.listdir(folder_path):
        if pattern.match(file_name):
            process_single_file(
                folder_path,
                file_name,
                initial_date,
                threshold_calculator
            )


def process_single_file(folder_path, file_name, initial_date, threshold_calculator):
    """处理单个文件的函数"""
    file_path = os.path.join(folder_path, file_name)

    # 获取输出文件名并检查是否已存在
    base_name = os.path.splitext(file_name)[0]
    output_file = os.path.join(folder_path, f"{base_name}_result.csv")
    if os.path.exists(output_file):
        print(f"Output file '{output_file}' already exists. Skipping '{file_name}'.")
        return

    # 读取CSV文件并解析日期
    data = pd.read_csv(file_path, parse_dates=[0])
    data['Date'] = data['Timestamp'].dt.date

    # 处理初始状态
    initial_data = data[data['Date'] == pd.to_datetime(initial_date).date()]
    sequence_prev = initial_data['CN value'].values
    status_prev = initial_data['status'].values
    data.loc[data['Date'] == pd.to_datetime(initial_date).date(), 'status'] = status_prev

    # 设置处理的日期范围
    start_date = pd.to_datetime(initial_date).date() + timedelta(days=1)
    end_date = data['Date'].max()

    # 处理每一天的数据
    current_date = start_date
    while current_date <= end_date:
        process_daily_data(
            data,
            current_date,
            threshold_calculator
        )
        current_date += timedelta(days=1)

    # 保存结果
    data = data.drop(columns=['Date'])
    data.to_csv(output_file, index=False)
    print(f"All status results for '{file_name}' have been saved to '{output_file}' without the 'Date' column.")


def process_daily_data(data, current_date, threshold_calculator):
    """处理每日数据的函数"""
    # 获取前一天和当前天的数据
    previous_day_data = data[data['Date'] == current_date - timedelta(days=1)]
    current_day_data = data[data['Date'] == current_date]
    sequence_prev = previous_day_data['CN value'].values
    sequence_curr = current_day_data['CN value'].values

    # 确保序列长度一致
    min_length = min(len(sequence_prev), len(sequence_curr))
    sequence_prev = sequence_prev[:min_length]
    sequence_curr = sequence_curr[:min_length]
    status_prev = data.loc[data['Date'] == current_date - timedelta(days=1), 'status'].values[:min_length]

    # 计算差分和阈值
    diff = sequence_curr - sequence_prev
    threshold = threshold_calculator.calculate_threshold(sequence_prev, sequence_curr)

    # 更新状态
    status_curr = update_status(diff, status_prev, threshold)

    # 更新数据框中的状态
    target_len = len(data.loc[data['Date'] == current_date, 'status'])
    if len(status_curr) < target_len:
        status_curr = np.pad(status_curr, (0, target_len - len(status_curr)), mode='edge')
    data.loc[data['Date'] == current_date, 'status'] = status_curr

    # 可视化
    visualize_daily_data(
        sequence_prev,
        sequence_curr,
        diff,
        status_curr,
        threshold,
        current_date
    )


def update_status(diff, status_prev, threshold):
    """更新状态的函数"""
    status_curr = status_prev.copy()
    for i in range(len(diff)):
        # 如果阈值是一个序列，那么每个数据点都有自己的阈值;如果阈值是一个常值，那么所有数据点共享一个阈值
        if isinstance(threshold, np.ndarray):
            if check_threshold_violation(diff[i], threshold[i]):
                status_curr[i] = 1 - status_curr[i]
        else:
            if check_threshold_violation(diff[i], threshold):
                status_curr[i] = 1 - status_curr[i]
    return status_curr


def visualize_daily_data(sequence_prev, sequence_curr, diff, status_curr, threshold, current_date):
    """可视化每日数据的函数，并标注均值和标准差"""
    plt.figure(figsize=(12, 8))

    # 绘制前一天和当前天的序列
    plt.plot(sequence_prev, label=f'Sequence on {current_date - timedelta(days=1)}')
    plt.plot(sequence_curr, label=f'Sequence on {current_date}')
    plt.plot(diff, label='Difference')
    plt.plot(status_curr * 50, label='Updated Status')

    # 计算并标注均值和标准差
    mean_prev, std_prev = np.mean(sequence_prev), np.std(sequence_prev)
    mean_curr, std_curr = np.mean(sequence_curr), np.std(sequence_curr)
    plt.axhline(mean_prev, color='blue', linestyle='--', label=f'Mean (prev)={mean_prev:.2f}')
    plt.axhline(mean_curr, color='green', linestyle='--', label=f'Mean (curr)={mean_curr:.2f}')
    plt.fill_between(range(len(sequence_prev)), mean_prev - std_prev, mean_prev + std_prev, color='blue', alpha=0.1, label=f'STD (prev)={std_prev:.2f}')
    plt.fill_between(range(len(sequence_curr)), mean_curr - std_curr, mean_curr + std_curr, color='green', alpha=0.1, label=f'STD (curr)={std_curr:.2f}')

    # 画阈值线
    if isinstance(threshold, np.ndarray):
        plt.plot(threshold, color='red', linestyle='--', label='Threshold')
        plt.plot(-threshold, color='red', linestyle='--')
    else:
        plt.axhline(threshold, color='red', linestyle='--', label='Threshold')
        plt.axhline(-threshold, color='red', linestyle='--')

    # 添加图例和标题
    plt.legend()
    plt.title(f'Data comparison for {current_date - timedelta(days=1)} and {current_date}')
    plt.show()



if __name__ == "__main__":
    # 配置参数
    folder_path = r'D:\OneDrive\data\HAL120240601_20240607'
    stationname = 'HAL1'
    year = '2024'
    signal = 'S2W'
    satellite_range = range(32, 33)
    initial_date = '2024-06-01'

    # 配置阈值方法和参数
    threshold_method = ThresholdMethod.STATIC  # 设置使用EWMA方法
    threshold_params = {
        'threshold': 5.8
    }

    # 运行主程序
    process_signal_data(
        folder_path,
        stationname,
        year,
        signal,
        satellite_range,
        initial_date,
        threshold_method,
        threshold_params
    )