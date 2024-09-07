import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import os
from tqdm import tqdm  # 导入 tqdm
import time

# 定义年份、站点和信号类型数组
years = ['2020', '2021', '2022', '2023', '2024']
stations = ['AIRA', 'BAIE', 'BIK0', 'CAS1']
signals = ['S2W']

# 可修改变量命名区
svn_range = range(1, 33)  # G04到G32的范围
timestamp_format = '%Y-%m-%d %H:%M:%S'
residual_threshold = 5
save_plots = True  # 控制是否保存每日图像的布尔变量

# 绘图比例控制变量（只用于汇总图）
figsize = (15, 5)  # 图形的大小 (宽, 高)
plot_dpi = 100  # 图形的分辨率

# 遍历每个year, station, signal的组合
for year in years:
    for station in stations:
        for signal in signals:
            # 计时开始
            start_time = time.time()

            # 遍历每个G代码
            for svn in svn_range:
                name = f'{station}_{year}_{signal}_G{svn:02d}'
                input_csv_path = f'F:/data/dataset/{year}/{station}/{name}.csv'
                output_image_dir = f'images/{name}'
                output_DTW_dir = f'DTW_result'
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

                # 1. 读取CSV文件
                data = pd.read_csv(input_csv_path)
                timestamps = pd.to_datetime(data.iloc[:, 0], format=timestamp_format)
                CNvalues = data.iloc[:, 1]
                # 插值处理NaN值
                nan_mask = CNvalues.isna()
                nan_indices = CNvalues[nan_mask].index
                print("NaN values found at indices:", nan_indices)
                CNvalues_interpolated = CNvalues.interpolate(method='linear')
                CNvalues_interpolated = CNvalues_interpolated.bfill() #加入前向填充以避免csv开头就是nan值的情况线性插值无法处理
                remaining_nan = CNvalues_interpolated.isna().sum()
                print(f"Number of remaining NaN values after interpolation: {remaining_nan}")
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

                # 使用 tqdm 添加进度条
                for i in tqdm(range(1, len(unique_dates)), desc=f'Processing Dates for {name}'):
                    s_today = adjusted_data.loc[dates_origin_day == unique_dates[i]].iloc[:, 1].values

                    if i >= 3 and anomaly_all[-1] != 0:
                        lastanomaly_date = unique_dates[i - 1]

                    prev_days_idx = np.where((unique_dates < unique_dates[i]) & (unique_dates >= lastanomaly_date))[0][-5:]
                    s_prev = np.array(
                        [adjusted_data.loc[dates_origin_day == unique_dates[idx]].iloc[:, 1].values[:len(s_today)] for idx in
                         prev_days_idx])

                    s_seasonal = s_prev.mean(axis=0)
                    s_residual = s_today - s_seasonal[:len(s_today)]

                    dist, _ = fastdtw(s_today.reshape(-1, 1), s_seasonal[:len(s_today)].reshape(-1, 1), dist=euclidean)

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

                    if save_plots:
                        fig, ax = plt.subplots()  # 使用默认尺寸
                        ax.plot(s_seasonal, label='Seasonal Mean')
                        ax.plot(s_today, label='Today')
                        ax.plot(s_residual, label='Residual')
                        ax.legend()
                        ax.set_title(f'Date: {unique_dates[i].strftime("%Y-%m-%d")}')
                        ax.set_xlabel('Time Points')
                        ax.set_ylabel('Values')
                        plt.savefig(f'{output_image_dir}/Date_{unique_dates[i].strftime("%Y-%m-%d")}.png')
                        plt.close(fig)

                # 6.5 将 dist_all 与时间戳一起保存到 CSV 文件
                dist_all_df = pd.DataFrame({
                    'Date': unique_dates[1:],  # 对应的日期（去掉第一天，因为从第二天开始计算DTW距离）
                    'DTW Distance': dist_all
                })
                dist_all_df.to_csv(os.path.join(output_DTW_dir, output_DTW_name), index=False)

            # 计时结束并显示结果
            elapsed_time = time.time() - start_time
            print(f'组合 {year}, {station}, {signal} 运行时间：{elapsed_time:.2f}秒')
