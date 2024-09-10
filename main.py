# main.py
from sfpd import calculate_sfpd

# 可修改变量命名区
years = ['2020','2021','2022']
stations = ['AIRA', 'BAIE', 'BIK0', 'CAS1']
signals = ['S2W']
svn_range = range(1, 33)  # G01到G32的范围
timestamp_format = '%Y-%m-%d %H:%M:%S'
residual_threshold = 5
save_plots = True  # 控制是否保存每日图像的布尔变量
figsize = (15, 5)  # 图形的大小 (宽, 高)
plot_dpi = 100  # 图形的分辨率
input_data_path = 'F:/data/dataset'  # 输入CSV文件所在目录

# 自定义输出路径
output_image_dir_base = 'F:/data/result/ver3/images'  # 图像输出基础路径
output_DTW_dir_base = 'F:/data/result/ver3/DTW_results'  # DTW输出路径

# 调用SFPD计算函数
calculate_sfpd(years, stations, signals, svn_range, timestamp_format, residual_threshold, save_plots, figsize, plot_dpi,
               input_data_path, output_image_dir_base, output_DTW_dir_base)
