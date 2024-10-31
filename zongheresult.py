import pandas as pd
import os

# 定义测站名称、年份和信号
base_names = ['HAL1','HLFX','KAT1','SAVO','STFU']
year = '2024'
signal = 'S2W'
input_dir = 'F:/data/result/ver3/combine/'
output_dir = 'F:/data/result/ver3/result/'

# 设定是否选择所有测站的标志
all_base = 1  # 1 表示选择所有测站，0 表示按照 base_names 进行选择

# 初始化一个空的 DataFrame 用于合并结果
merged_df = pd.DataFrame()

# 如果 all_base 为 1，选择所有测站文件；如果为 0，选择指定的测站
if all_base == 1:
    # 遍历 input_dir 中的所有 CSV 文件
    for file_name in os.listdir(input_dir):
        if file_name.endswith('_combine.csv'):
            file_path = os.path.join(input_dir, file_name)
            df = pd.read_csv(file_path)

            # 确保列存在
            if 'Date' in df.columns and 'DOY' in df.columns and 'Is_Abnormal' in df.columns:
                # 确保日期格式一致
                df['Date'] = pd.to_datetime(df['Date'])
                df['Year'] = df['Date'].dt.year

                # 仅保留对应年份的数据
                df = df[df['Year'] == int(year)]

                # 合并数据，保留 DOY 列
                merged_df = pd.concat([merged_df, df[['Date', 'DOY', 'Is_Abnormal']]], ignore_index=True)

else:
    # 遍历指定的测站名称
    for base_name in base_names:
        file_path = os.path.join(input_dir, f'{base_name}_combine.csv')

        # 读取 CSV 文件
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)

            # 确保列存在
            if 'Date' in df.columns and 'DOY' in df.columns and 'Is_Abnormal' in df.columns:
                # 确保日期格式一致
                df['Date'] = pd.to_datetime(df['Date'])
                df['Year'] = df['Date'].dt.year

                # 仅保留对应年份的数据
                df = df[df['Year'] == int(year)]

                # 合并数据，保留 DOY 列
                merged_df = pd.concat([merged_df, df[['Date', 'DOY', 'Is_Abnormal']]], ignore_index=True)

# 检查是否成功合并数据
if not merged_df.empty:
    # 处理合并后的数据，取并集
    final_df = merged_df.groupby(['Date', 'DOY']).agg({'Is_Abnormal': lambda x: 'Abnormal' if 'Abnormal' in x.values else 'normal'}).reset_index()

    # 生成输出文件名
    output_file_path = os.path.join(output_dir, f'{year}_{signal}_result.csv')

    # 确保输出目录存在，如果不存在则创建
    os.makedirs(output_dir, exist_ok=True)

    # 保存结果到新的 CSV 文件
    final_df.to_csv(output_file_path, index=False)

    print(f"结果已保存到 {output_file_path}")
else:
    print("未找到合适的数据，合并结果为空。")
