# sfpd.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import os
from tqdm import tqdm

def calculate_sfpd(years, stations, signals, svn_range, timestamp_format, residual_threshold, save_plots, figsize,
                   plot_dpi, input_data_path, output_image_dir_base, output_DTW_dir_base):
    # 遍历每个year, station, signal的组合
    for year in years:
        for station in stations:
            for signal in signals:
                for svn in svn_range:
                    name = f'{station}_{year}_{signal}_G{svn:02d}'
                    input_csv_path = f'{input_data_path}/{year}/{station}/{name}.csv'
                    output_image_dir = f'{output_image_dir_base}/{name}'  # 自定义图像输出路径
                    output_DTW_dir = f'{output_DTW_dir_base}'  # 自定义DTW输出路径
                    output_DTW_name = f'{name}_DTW.csv'

                    # 创建输出目录（如果不存在）
                    if not os.path.exists(output_image_dir):
                        os.makedirs(output_image_dir)

                    if not os.path.exists(output_DTW_dir):
                        os.makedirs(output_DTW_dir)

                    # 检查文件是否存在
                    if not os.path.exists(input_csv_path):
                        print(f"File {input_csv_path} does not exist. Skipping this iteration.")
                        continue

                    # **新增：检查是否已经有输出文件**
                    # 如果 DTW 结果文件存在，跳过处理
                    if os.path.exists(os.path.join(output_DTW_dir, output_DTW_name)):
                        print(f"DTW result for {name} already exists. Skipping.")
                        continue

                    # 1. 读取CSV文件
                    data = pd.read_csv(input_csv_path)
                    # 使用混合模式解析时间格式
                    timestamps = pd.to_datetime(data.iloc[:, 0], format='mixed')
                    CNvalues = data.iloc[:, 1]
                    # 插值处理NaN值
                    CNvalues_interpolated = CNvalues.interpolate(method='linear').bfill()
                    data.iloc[:, 1] = CNvalues_interpolated

                    # 2. 获取日期和每日数据数量，保持原始顺序
                    dates_origin_day = timestamps.dt.floor('d')
                    unique_dates = dates_origin_day.unique()
                    daily_counts = dates_origin_day.value_counts().sort_index()
                    single_day_num_standard = daily_counts.min()

                    # 3. 调整每日数据量
                    adjusted_data = pd.DataFrame()
                    for date in unique_dates:
                        day_data = data[dates_origin_day == date]
                        if len(day_data) > single_day_num_standard:
                            day_data = day_data.iloc[:single_day_num_standard, :]
                        adjusted_data = pd.concat([adjusted_data, day_data])

                    # 4. 处理每日数据
                    s_residual_all = []
                    anomaly_all = []
                    dist_all = []
                    lastanomaly_date = unique_dates[0]
                    last_valid_seasonal = None  # 用于记录最后一次有效的seasonal mean

                    # 使用 tqdm 添加进度条
                    for i in tqdm(range(1, len(unique_dates)), desc=f'Processing Dates for {name}'):
                        s_today = adjusted_data.loc[dates_origin_day == unique_dates[i]].iloc[:, 1].values

                        # **新增：检查是否已经处理过该日期的图像**
                        # 如果图像文件存在，跳过该日期
                        output_image_path = f'{output_image_dir}/Date_{unique_dates[i].strftime("%Y-%m-%d")}.png'
                        if os.path.exists(output_image_path):
                            print(f"Image for {unique_dates[i].strftime('%Y-%m-%d')} already exists. Skipping.")
                            continue

                        # 检查当天日期是否和上一天的日期相邻
                        if (unique_dates[i] - unique_dates[i - 1]).days != 1:
                            print(f'Date {unique_dates[i].strftime("%Y-%m-%d")} has no adjacent previous date. Skipping calculations.')
                            dist_all.append('nofront')
                            continue

                        # 检查当日数据量是否充足
                        prev_days_idx = np.where((unique_dates < unique_dates[i]) & (unique_dates >= lastanomaly_date))[
                                            0][-5:]
                        s_prev = np.array(
                            [adjusted_data.loc[dates_origin_day == unique_dates[idx]].iloc[:, 1].values[:len(s_today)]
                             for idx in prev_days_idx])
                        s_seasonal = s_prev.mean(axis=0) if len(s_prev) > 0 else last_valid_seasonal

                        # 如果当前没有有效的s_seasonal，跳过后续计算
                        if s_seasonal is None:
                            print(f"No valid seasonal data for {unique_dates[i].strftime('%Y-%m-%d')}. Skipping.")
                            continue

                        # 检查数据量是否少于参考数据量的一半
                        if len(s_today) < 0.5 * len(s_seasonal):
                            print(f'Date {unique_dates[i].strftime("%Y-%m-%d")} has insufficient data. Skipping calculations.')
                            dist_all.append('nodata')
                            continue

                        # 检查数据量是否在50%-80%之间
                        if 0.5 * len(s_seasonal) <= len(s_today) < 0.8 * len(s_seasonal):
                            print(f'Date {unique_dates[i].strftime("%Y-%m-%d")} has reduced data. Performing DTW with adjusted seasonal data.')
                            # 使用滑动窗口在 seasonal 中提取与 s_today 相同长度的部分
                            min_dist = float('inf')
                            step_size = int(0.1 * len(s_seasonal))  # 以10%为步长
                            for j in range(0, len(s_seasonal) - len(s_today) + 1, step_size):
                                s_seasonal_window = s_seasonal[j:j + len(s_today)]
                                dist, _ = fastdtw(s_today.reshape(-1, 1), s_seasonal_window.reshape(-1, 1),
                                                  dist=euclidean)
                                if dist < min_dist:
                                    min_dist = dist
                            dist = min_dist  # 使用最小的DTW距离
                        else:
                            # 正常计算DTW
                            dist, _ = fastdtw(s_today.reshape(-1, 1), s_seasonal[:len(s_today)].reshape(-1, 1),
                                              dist=euclidean)

                        # 计算残差和异常
                        s_residual = s_today - s_seasonal[:len(s_today)]
                        anomaly_flag = 0
                        has_greater_than_5 = np.any(s_residual > residual_threshold)
                        has_less_than_5 = np.any(s_residual < -residual_threshold)

                        if has_greater_than_5 and has_less_than_5:
                            anomaly_flag = 3
                        elif has_greater_than_5:
                            anomaly_flag = 1
                        elif has_less_than_5:
                            anomaly_flag = 2

                        s_residual_all.extend(s_residual)
                        anomaly_all.append(anomaly_flag)
                        dist_all.append(dist)

                        # 更新 last_valid_seasonal，当天数据有效时才更新
                        if len(s_today) >= 0.5 * len(s_seasonal):
                            last_valid_seasonal = s_seasonal

                        if save_plots:
                            fig, ax = plt.subplots()  # 使用默认尺寸
                            ax.plot(s_seasonal, label='Seasonal Mean')
                            ax.plot(s_today, label='Today')
                            ax.plot(s_residual, label='Residual')
                            ax.legend()

                            # 更新图像标题，增加测站名称、卫星编号以及之前的日期信息
                            ax.set_title(f'Station: {station}, Satellite: G{svn:02d}, Date: {unique_dates[i].strftime("%Y-%m-%d")}')
                            ax.set_xlabel('Time Points')
                            ax.set_ylabel('Values')
                            plt.savefig(output_image_path)  # 保存图像
                            plt.close(fig)

                    # 6.5 将 dist_all 与时间戳一起保存到 CSV 文件
                    dist_all_df = pd.DataFrame({
                        'Date': unique_dates[1:],  # 对应的日期（去掉第一天，因为从第二天开始计算DTW距离）
                        'DTW Distance': dist_all
                    })
                    dist_all_df.to_csv(os.path.join(output_DTW_dir, output_DTW_name), index=False)
