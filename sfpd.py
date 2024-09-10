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
                    inte_data = data.copy()
                    inte_data.iloc[:, 1] = CNvalues_interpolated  # 把插值后的结果写回原始数据

                    # 2. 获取日期和每日数据数量，保持原始顺序
                    dates_origin_day = timestamps.dt.floor('d')
                    unique_dates = dates_origin_day.unique()
                    daily_counts = dates_origin_day.value_counts().sort_index()

                    # 计算data中每天的nan值数量，生成一个第一列是时间，第二列是每天nan值数量的dataframe
                    nan_count = data.iloc[:, 1].isna()
                    nan_count = nan_count.groupby(dates_origin_day).sum().reset_index()
                    nan_count.columns = ['Date', 'NaN Count']

                    # daily_counts要减去每天的nan值，才是真实的有效值
                    # 合并 daily_counts 和 nan_count，确保它们按日期对齐
                    daily_counts_df = daily_counts.reset_index()
                    daily_counts_df.columns = ['Date', 'Total Count']  # 给daily_counts加上适当的列名
                    # 合并 daily_counts 和 nan_count 两个DataFrame
                    merged_counts = pd.merge(daily_counts_df, nan_count, on='Date', how='left')
                    # 计算有效值数量（总数量减去NaN数量）
                    merged_counts['Valid Count'] = merged_counts['Total Count'] - merged_counts['NaN Count']
                    # 将有效值数量赋回 daily_counts
                    daily_counts = merged_counts.set_index('Date')['Valid Count']

                    data = inte_data.copy()  # 使用插值后的数据

                    single_day_num_standard = daily_counts.min()
                    single_day_num_max = daily_counts.max() # 单日最大数据量
                    percent_every_day = daily_counts / single_day_num_max # 每日数据量占比
                    below_half_day = percent_every_day[percent_every_day < 0.5].index # 将percent_every_day中小于0.5的日期赋给below_half_day
                    between_half_and_nine = percent_every_day[(percent_every_day >= 0.5) & (percent_every_day < 0.9)].index # 将percent_every_day中在0.5-0.9之间的日期赋给between_half_and_nine
                    above_nine = percent_every_day[percent_every_day >= 0.9].index # 将percent_every_day中大于0.9的日期赋给above_nine

                    # 4. 处理每日数据
                    s_residual_all = []
                    anomaly_all = []
                    dist_all = []
                    seasonal_date = []
                    lastanomaly_date = unique_dates[0]
                    last_valid_seasonal = None  # 用于记录最后一次有效的seasonal mean

                    # 使用 tqdm 添加进度条
                    for i in tqdm(range(0, len(unique_dates)), desc=f'Processing Dates for {name}'):
                        # 获取当天日期
                        today_date = unique_dates[i]
                        # 获取当天数据
                        s_today = data.loc[dates_origin_day == today_date].iloc[:, 1].values

                        # debugger, 如果日期是2020-01-01，打印当天日期
                        if today_date == pd.Timestamp('2020-09-13'):
                            print(today_date)

                        # 如果图像文件存在，跳过该日期
                        output_image_path = f'{output_image_dir}/Date_{today_date.strftime("%Y-%m-%d")}.png'
                        if os.path.exists(output_image_path):
                            print(f"Image for {today_date.strftime('%Y-%m-%d')} already exists. Skipping.")
                            continue

                        # 判断是否为第 1 天，直接输出"firstday"为结果
                        if i == 0:
                            dist_all.append('firstday')
                            # 如果当天日期属于above_nine，则把当天数据赋给s_seasonal
                            if today_date in above_nine:
                                s_seasonal = s_today
                                # 把当天的日期加入到seasonal_date中
                                seasonal_date.append(today_date)
                                print(f"Use {today_date.strftime('%Y-%m-%d')} as the first detection day.")
                            continue

                        # 判断seasonal_date是否为空
                        if len(seasonal_date) == 0:
                            dist_all.append('noresult') # 如果为空，检查当天日期属于above_nine，则把当天数据赋给s_seasonal
                            if today_date in above_nine:
                                s_seasonal = s_today
                                # 把当天的日期加入到seasonal_date中
                                seasonal_date.append(today_date)
                                # 输出："把{today_date}作为第一个检测日"
                                print(f"Use {today_date.strftime('%Y-%m-%d')} as the first detection day.")
                            continue

                        # 检查当天日期是否和seasonal的最后一天日期相邻
                        if (today_date - seasonal_date[-1]).days != 1: # 如果不相邻
                            print(f'Date {today_date.strftime("%Y-%m-%d")} has no adjacent previous date. Skipping calculations.')
                            dist_all.append('incontinuity')
                            # 清空seasonal_date数组
                            seasonal_date = []
                            # 判断当天的日期是否属于above_nine，如果属于，将当天数据赋给s_seasonal，否则
                            if today_date in above_nine:
                                s_seasonal = s_today
                                # 把当天的日期加入到seasonal_date中
                                seasonal_date.append(today_date)
                            continue

                        # 现在我拿到了有效的s_seasonal和s_today，可以开始计算DTW距离
                        # 先检查当日数据量是否充足，判断当日日期是否属于above_nine，如果属于，则直接计算DTW距离
                        # 使用switch case语句，判断当日日期是否属于below_half_day，between_half_and_nine，above_nine
                        # 如果当日日期属于below_half_day，则调用proc_below_half_day函数
                        # 如果当日日期属于between_half_and_nine，调用proc_between_half_and_nine函数
                        # 如果当日日期属于above_nine，调用proc_above_nine函数
                        if today_date in below_half_day:
                            dist_all.append('firstday')
                            seasonal_date = []
                            continue
                        elif today_date in between_half_and_nine:
                            # 滑窗计算DTW距离，窗口大小为percent，滑动距离为0.1，取s_seasonal的前len(s_today)个数据开始计算
                            min_DTW_dist, min_DTW_bias, s_today_dtw, s_seasonal_dtw = movingWindowDTW(s_today, s_seasonal, 0.1)
                            dist_all.append(min_DTW_dist)   # 输出结果
                            # 计算DTW残差
                            # 如果s_today_dtw和s_seasonal_dtw的长度不一样，就截取更多的那个序列
                            if len(s_today_dtw) != len(s_seasonal_dtw):
                                if len(s_today_dtw) > len(s_seasonal_dtw):
                                    s_today_dtw = s_today_dtw[:len(s_seasonal_dtw)]
                                else:
                                    s_seasonal_dtw = s_seasonal_dtw[:len(s_today_dtw)]
                            s_residual = s_today_dtw - s_seasonal_dtw

                            # 绘图
                            if save_plots:
                                fig, ax = plt.subplots()  # 使用默认尺寸
                                ax.plot(s_seasonal, label='Seasonal Mean')
                                ax.plot(s_today, label='Today')
                                ax.plot(s_residual, label='Residual(DTW)')
                                ax.legend()

                                # 更新图像标题，增加测站名称、卫星编号以及之前的日期信息
                                ax.set_title(
                                    f'Station: {station}, Satellite: G{svn:02d}, Date: {today_date.strftime("%Y-%m-%d")}')
                                ax.set_xlabel('Time Points')
                                ax.set_ylabel('Values')
                                plt.savefig(output_image_path)  # 保存图像
                                plt.close(fig)
                            # 判断残差是否有超过阈值的，如果有超过阈值的，则清空seasonal_date数组，然后把当天数据赋给s_seasonal，最后把当天的日期加入到seasonal_date中
                            if np.any(np.abs(s_residual) > residual_threshold):
                                # 如果有超过阈值的，则清空seasonal_date数组
                                seasonal_date = []
                            # 如果没有超过阈值的，则只把min_bias开始的部分数据加入到s_seasonal的平均计算中，并把当天的日期加入到seasonal_date中
                            else:
                                # seasonal_date数组中加入当天的日期，但是s_seasonal暂时不变
                                seasonal_date.append(today_date)
                            continue

                        elif today_date in above_nine:
                            # 计算s_today和s_seasonal的DTW距离，并且输出在这个DTW距离下变换后的两个对应的序列
                            dist, path = fastdtw(s_today.reshape(-1, 1), s_seasonal.reshape(-1, 1), dist=euclidean)
                            # 输出结果
                            dist_all.append(dist)
                            # 提取DTW变换后的序列
                            s_today_dtw = np.array([s_today[i] for i, j in path])
                            s_seasonal_dtw = np.array([s_seasonal[j] for i, j in path])
                            # 计算DTW残差
                            # 如果s_today_dtw和s_seasonal_dtw的长度不一样，就截取更多的那个序列
                            if len(s_today_dtw) != len(s_seasonal_dtw):
                                if len(s_today_dtw) > len(s_seasonal_dtw):
                                    s_today_dtw = s_today_dtw[:len(s_seasonal_dtw)]
                                else:
                                    s_seasonal_dtw = s_seasonal_dtw[:len(s_today_dtw)]
                            s_residual = s_today_dtw - s_seasonal_dtw
                            # 绘图
                            if save_plots:
                                fig, ax = plt.subplots()  # 使用默认尺寸
                                ax.plot(s_seasonal, label='Seasonal Mean')
                                ax.plot(s_today, label='Today')
                                ax.plot(s_residual, label='Residual(DTW)')
                                ax.legend()

                                # 更新图像标题，增加测站名称、卫星编号以及之前的日期信息
                                ax.set_title(
                                    f'Station: {station}, Satellite: G{svn:02d}, Date: {today_date.strftime("%Y-%m-%d")}')
                                ax.set_xlabel('Time Points')
                                ax.set_ylabel('Values')

                                # 在图中右上角标注当天的DTW_value
                                ax.text(0.9, 0.1, f'DTW Distance: {dist:.2f}', horizontalalignment='center',
                                        verticalalignment='bottom', transform=ax.transAxes)
                                plt.savefig(output_image_path)  # 保存图像
                                plt.close(fig)
                            # 判断残差是否有超过阈值的，如果有超过阈值的，则清空seasonal_date数组，然后把当天数据赋给s_seasonal，最后把当天的日期加入到seasonal_date中
                            if np.any(np.abs(s_residual) > residual_threshold):
                                # 如果有超过阈值的，则清空seasonal_date数组
                                seasonal_date = []
                                # 把今天的数据赋给s_seasonal
                                s_seasonal = s_today
                                # 最后把当天的日期加入到seasonal_date中
                                seasonal_date.append(today_date)
                                continue
                            else:
                                # 如果没有超过阈值的，则把当日的数据加入到s_seasonal的平均计算中，并把当天的日期加入到seasonal_date中
                                n_s_day = len(seasonal_date)
                                # 使用DTW的策略求平均值
                                s_seasonal_dtw_mean = (s_seasonal_dtw * n_s_day + s_today_dtw) / (n_s_day + 1)

                                # 将平均后的序列映射回原始s_seasonal的长度
                                from scipy.interpolate import interp1d
                                interp_func = interp1d(np.linspace(0, 1, len(s_seasonal_dtw_mean)), s_seasonal_dtw_mean,
                                                       kind='linear')
                                s_seasonal = interp_func(np.linspace(0, 1, len(s_seasonal)))  # 映射到原始长度
                                seasonal_date.append(today_date) # 把当天的日期加入到seasonal_date中
                                continue


                    # 6.5 将 dist_all 与时间戳一起保存到 CSV 文件
                    dist_all_df = pd.DataFrame({
                        'Date': unique_dates,  # 对应的日期（去掉第一天，因为从第二天开始计算DTW距离）
                        'DTW Distance': dist_all
                    })
                    dist_all_df.to_csv(os.path.join(output_DTW_dir, output_DTW_name), index=False)


def movingWindowDTW(s_today, s_seasonal, step_size):
    # 返回最小的DTW距离，最小DTW距离对应的偏移量，DTW最小时的DTW变化后的序列
    min_dist = float('inf')
    min_bias = 0
    min_s_today_dtw = s_today
    min_s_seasonal_dtw = s_seasonal
    # 以percent为窗口大小，step_size为滑动距离，从s_seasonal中提取和s_today相同长度的数据，计算DTW距离
    for j in range(0, len(s_seasonal) - len(s_today) + 1, int(step_size * len(s_seasonal))):
        s_seasonal_window = s_seasonal[j:j + len(s_today)]
        dist, path = fastdtw(s_today.reshape(-1, 1), s_seasonal_window.reshape(-1, 1), dist=euclidean)
        if dist < min_dist:
            min_dist = dist
            min_bias = j
            min_s_today_dtw = np.array([s_today[i] for i, j in path])
            min_s_seasonal_dtw = np.array([s_seasonal_window[j] for i, j in path])
    return min_dist, min_bias, min_s_today_dtw, min_s_seasonal_dtw
