import pandas as pd
import dtw_align_series as das
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import test1

# 1.读取所有文件数据（单卫星）
# 文件路径
file_path = r'F:\data\realtime\HAL120240601_20240607\HAL1_2024_S2W_G05.csv'
# 读取CSV文件，解析第一列为日期时间格式
data = pd.read_csv(file_path, parse_dates=[0])

# 2.检查每一天的数据量
data['Date'] = data['Timestamp'].dt.date  # 将时间戳列转换为日期列
daily_counts = data.groupby('Date').size()  # 按日期分组统计数据条数

# 提取2024年6月1日和6月2日的数据
data_june1 = data[data['Date'] == pd.to_datetime('2024-06-02').date()]
data_june2 = data[data['Date'] == pd.to_datetime('2024-06-03').date()]

# 提取数据值序列，假设数据值在'CN value'列
sequence1 = data_june1['CN value'].values
sequence2 = data_june2['CN value'].values
status1 = data_june1['status'].values

# 对比sequence1和sequence2的长度，将长度调整至一致
min_length = min(len(sequence1), len(sequence2))
sequence1 = sequence1[:min_length]
sequence2 = sequence2[:min_length]
status1 = status1[:min_length]
status2 = status1.copy()

# 求差分
diff = sequence2 - sequence1

# 如果diff的数据点绝对值大于5，那这些对应的索引值应该是状态反转点
# 将status2对应索引值的点如果是1翻转为0，如果是0翻转为1
for i in range(len(diff)):
    if abs(diff[i]) > 5:
        status2[i] = 1 - status2[i] # wok，妙啊

# 画两个时序图和差分时序图在同一张图上
plt.figure(figsize=(12, 8))
plt.plot(sequence1, label='Sequence 1')
plt.plot(sequence2, label='Sequence 2')
plt.plot(diff, label='Difference')
plt.plot(status2*50, label='Status 2')
plt.legend()
plt.show()
