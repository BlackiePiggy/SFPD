import os
import pandas as pd

# 定义年份变量
year = '2022'
station = 'BIK0'
date_start = f'{year}001'
date_end = f'{year}365'
signal = 'S2W'

# 定义输入输出路径
test_data_path = rf'F:\data\4_filtered_time_CN\{year}'
output_base_path = rf'F:\data\dataset\{year}\{station}'

# 定义卫星号的范围
satellites = [f'G{str(i).zfill(2)}' for i in range(1, 33)]  # 生成G06到G32的卫星号

for satellite in satellites:
    # 动态设置输出路径
    output_path = os.path.join(output_base_path, f'{station}_{year}_{signal}_{satellite}.csv')

    # 创建一个空的列表来存储数据框
    data_frames = []

    # 遍历所有文件
    for path in [test_data_path]:
        for filename in os.listdir(path):
            if filename.startswith(station) and filename.endswith('_filtered.csv'):
                parts = filename.split('_')
                date_str = parts[1]
                satellite_str = parts[3]
                signal_str = parts[4]

                if date_start <= date_str <= date_end and satellite_str == satellite and signal_str == signal:
                    file_path = os.path.join(path, filename)
                    df = pd.read_csv(file_path)
                    data_frames.append(df)

    # 如果有符合条件的数据框则进行处理
    if data_frames:
        # 合并所有数据框
        merged_df = pd.concat(data_frames, ignore_index=True)

        # 删除第三列
        merged_df.drop(merged_df.columns[2], axis=1, inplace=True)

        # 确认Timestamp列存在并进行格式转换
        if 'Timestamp' in merged_df.columns:
            merged_df['Timestamp'] = pd.to_datetime(merged_df['Timestamp'])

        # 按日期排序
        merged_df.sort_values(by='Timestamp', inplace=True)

        # 输出合并后的数据框到指定文件
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        merged_df.to_csv(output_path, index=False)

        print(f"合并后的文件已保存到: {output_path}")
    else:
        print(f"没有找到符合条件的文件：卫星 {satellite}")