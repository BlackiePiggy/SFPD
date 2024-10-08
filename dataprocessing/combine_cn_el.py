import os
import pandas as pd


def merge_cn_el_files(station_name, SS_variables, satellite_range, output_cn_folder, output_el_folder, output_cn_el_folder, start_date_str, end_date_str):
    # 确保输出目录存在
    os.makedirs(output_cn_el_folder, exist_ok=True)

    # 解析 start_date 和 end_date
    start_date = pd.to_datetime(start_date_str, format='%Y%j')
    end_date = pd.to_datetime(end_date_str, format='%Y%j')

    # Step1:遍历天数，找到每一天对应的CN文件和EL文件，如果找不到，跳过并输出提示信息
    # CN文件格式：AIRA_2021001_CN_G01_S2W.csv
    # EL文件格式：elevation_BIK0_2022324_G23.csv
    for date in pd.date_range(start=start_date, end=end_date):
        date_str = date.strftime('%Y%j')
        # 遍历每颗卫星
        for satellite_code in satellite_range:
            # 查找对应名称的 CN 文件
            CN_filename = f"{station_name}_{date_str}_CN_{satellite_code}_{SS_variables[0]}.csv"
            full_CN_path = os.path.join(output_cn_folder, CN_filename)
            if not os.path.exists(full_CN_path):
                print(f"CN file {CN_filename} not found. Skipping...")
                continue

            # 查找对应名称的 EL 文件
            EL_filename = f"elevation_{station_name}_{date_str}_{satellite_code}.csv"
            full_EL_path = os.path.join(output_el_folder, EL_filename)
            if not os.path.exists(full_EL_path):
                print(f"EL file {EL_filename} not found. Skipping...")
                continue

            # 检查输出文件是否已经存在，如果已经存在，后续内容不再执行
            output_file = os.path.join(output_cn_el_folder, f"{os.path.splitext(CN_filename)[0]}_el.csv")
            if os.path.exists(output_file):
                print(f"File {output_file} already exists. Skipping...")
                continue

            # 读取文件1 (CN file) 和 文件2 (EL file)
            cn_df = pd.read_csv(full_CN_path)
            el_df = pd.read_csv(full_EL_path)

            # 合并两个文件的数据
            # 合并两个文件的数据，使用列索引号进行操作
            merged_df = pd.merge(cn_df, el_df, left_on=cn_df.columns[0], right_on=el_df.columns[0],
                                 suffixes=('_cn', '_el'))
            merged_df = merged_df[[cn_df.columns[0], cn_df.columns[1], el_df.columns[1]]]
            merged_df.columns = ['Timestamp', 'CN value', 'el value']

            # 输出新的包含 timestamp-cn value-el value 的 csv 表格
            merged_df.to_csv(output_file, index=False)
            print(f"Saved merged file: {output_file}")
