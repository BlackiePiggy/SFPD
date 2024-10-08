import os
import pandas as pd


def filter_cn_el_files(station_name, SS_variables, satellite_range, output_cn_el_folder, time_cn_el_filtered_folder, start_date_str, end_date_str, el_mask):
    # 确保输出目录存在
    os.makedirs(time_cn_el_filtered_folder, exist_ok=True)

    # 解析 start_date 和 end_date
    start_date = pd.to_datetime(start_date_str, format='%Y%j')
    end_date = pd.to_datetime(end_date_str, format='%Y%j')

    #遍历日期
    for date in pd.date_range(start=start_date, end=end_date):

        for satellite_code in satellite_range:
            # 找到每一天对应的CN_EL文件，如果找不到，跳过并输出提示信息
            # 文件名称格式示例：AIRA_2021001_CN_G09_S2W_el.csv
            cn_el_name = f"{station_name}_{date.strftime('%Y%j')}_CN_{satellite_code}_{SS_variables[0]}_el.csv"
            full_cn_el_path = os.path.join(output_cn_el_folder, cn_el_name)
            if not os.path.exists(full_cn_el_path):
                print(f"CN_EL file {cn_el_name} not found. Skipping...")
                continue

            # 检查输出文件是否已经存在
            output_file = os.path.join(time_cn_el_filtered_folder, f"{os.path.splitext(cn_el_name)[0]}_{el_mask}_filtered.csv")
            if os.path.exists(output_file):
                print(f"File {output_file} already exists. Skipping...")
                continue

            # 读取文件
            df = pd.read_csv(full_cn_el_path)
            # 过滤掉elevation小于el_mask的行
            filtered_df = df[df.iloc[:, 2] >= el_mask]

            # 输出过滤后的文件
            filtered_df.to_csv(output_file, index=False)
            print(f"Saved filtered file: {output_file}")

            # 删除变量
            del df
            del filtered_df
    print("All files filtered successfully!")
