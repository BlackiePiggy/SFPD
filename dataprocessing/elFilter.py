import os
import pandas as pd


def filter_cn_el_files(station_name, SS_variables, satellite_code, output_cn_el_folder, time_cn_el_filtered_folder, start_date_str, end_date_str, el_mask):
    # 确保输出目录存在
    os.makedirs(time_cn_el_filtered_folder, exist_ok=True)

    # 解析 start_date 和 end_date
    start_date = pd.to_datetime(start_date_str, format='%Y%j')
    end_date = pd.to_datetime(end_date_str, format='%Y%j')

    # 遍历 output_cn_el_folder 的文件
    for file in os.listdir(output_cn_el_folder):
        file_path = os.path.join(output_cn_el_folder, file)

        # 检查文件名中的日期是否在指定范围内
        try:
            file_date_str = file[5:12]  # 假设文件名中日期格式为 'YYYYDOY'
            file_date = pd.to_datetime(file_date_str, format='%Y%j')
        except ValueError:
            print(f"Skipping file {file} due to invalid date format")
            continue

        # 检查文件名中的站点名称是否与指定的一致
        try:
            file_station_str = file[0:4]
        except ValueError:
            print(f"Skipping file {file} due to invalid station name format")
            continue

        # 检查SS和卫星号是否与指定的一致，文件示例：BAIE_2021358_CN_G01_S1W_el.csv
        try:
            file_SS_str = file[20:23]
            file_satellite_str = file[16:19]
        except ValueError:
            print(f"Skipping file {file} due to invalid signal strength or satellite format")
            continue

        if (start_date <= file_date <= end_date) and (file_station_str == station_name) and (file_SS_str == SS_variables[0]) and (file_satellite_str == satellite_code):
            # 检查输出文件是否已经存在
            output_file = os.path.join(time_cn_el_filtered_folder, f"{os.path.splitext(file)[0]}_{el_mask}_filtered.csv")
            if os.path.exists(output_file):
                print(f"File {output_file} already exists. Skipping...")
                continue

            # 读取文件
            df = pd.read_csv(file_path)

            # 过滤掉elevation小于el_mask的行
            filtered_df = df[df.iloc[:, 2] >= el_mask]

            # 输出过滤后的文件
            filtered_df.to_csv(output_file, index=False)
            print(f"Saved filtered file: {output_file}")
        else:
            print(f"File {file} is not in the date range.")