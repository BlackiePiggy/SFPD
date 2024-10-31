import pandas as pd
import numpy as np
import os

# 定义测站和年份列表
stations = ['HAL1','HLFX','KAT1','SAVO','STFU']  # 替换为实际的测站名称列表
years = ['2022', '2023','2024']  # 替换为实际的年份列表
signal = 'S2W'  # 替换为实际的信号名称

# 定义输入和输出的文件夹路径
input_folder = 'F:/data/result/ver3/consolidated_results'
output_folder = 'F:/data/result/ver3/combine'

# 确保输出目录存在，如果不存在则创建
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 定义处理函数
def process_station_year(station, year):
    # 定义文件名
    input_name = f'{station}_{year}_{signal}'
    input_file_name = f'{input_name}_ConsolidatedResults.csv'
    output_file_name = f'{input_name}_combine.csv'

    input_file_path = os.path.join(input_folder, input_file_name)
    output_file_path = os.path.join(output_folder, output_file_name)

    # 检查输入文件是否存在
    if not os.path.exists(input_file_path):
        print(f"文件未找到：{input_file_path}")
        return

    # 读取CSV文件
    df = pd.read_csv(input_file_path)

    # 检查并处理空值
    df.fillna(0, inplace=True)

    # 计算每一天的32颗卫星时间序列数据的和
    df['Sum'] = df.iloc[:, 2:34].sum(axis=1)

    # 判断每一天是否为异常日
    df['Is_Abnormal'] = df['Sum'].apply(lambda x: 'Abnormal' if x >= 5 else 'normal')

    # 删除中间计算的Sum列
    df.drop(columns=['Sum'], inplace=True)

    # 只保留前两列和Is_Abnormal列
    result_df = df[['Date', 'DOY', 'Is_Abnormal']]

    # 保存结果到新的CSV文件
    result_df.to_csv(output_file_path, index=False)

    print(f"结果已保存到 {output_file_path}")

# 对所有测站和年份的组合进行处理
for station in stations:
    for year in years:
        process_station_year(station, year)

print("所有测站和年份的处理已完成。")
