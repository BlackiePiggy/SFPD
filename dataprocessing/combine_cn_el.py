import os
import pandas as pd


def merge_cn_el_files(station_name, SS_variables, satellite_code, output_cn_folder, output_el_folder, output_cn_el_folder, start_date_str, end_date_str):
    # 确保输出目录存在
    os.makedirs(output_cn_el_folder, exist_ok=True)

    # 解析 start_date 和 end_date
    start_date = pd.to_datetime(start_date_str, format='%Y%j')
    end_date = pd.to_datetime(end_date_str, format='%Y%j')

    # 遍历 output_cn_folder 的文件
    for cn_file in os.listdir(output_cn_folder):
        cn_file_path = os.path.join(output_cn_folder, cn_file)

        # 检查文件是否为指定的SS_variables和satellite_code，文件实例名称为BAIE_2024179_CN_G03_S1W.csv
        try:
            file_SS_str = cn_file[20:23]
            file_satellite_str = cn_file[16:19]
        except ValueError:
            print(f"Skipping file {cn_file} due to invalid signal strength or satellite format")
            continue

        # 检查文件名中的日期是否在指定范围内
        try:
            file_date_str = cn_file[5:12]  # 假设文件名中日期格式为 'YYYYDOY'
            file_date = pd.to_datetime(file_date_str, format='%Y%j')
        except ValueError:
            print(f"Skipping file {cn_file} due to invalid date format")
            continue

        # 检查文件名中的日期是否在指定范围内
        try:
            file_station_str = cn_file[0:4]
        except ValueError:
            print(f"Skipping file {cn_file} due to invalid station name format")
            continue

        # 如果文件日期在指定范围内，且文件的SS和卫星号与指定的一致，且站点名称与指定的一致，才执行合并操作
        if (start_date <= file_date <= end_date) and (file_SS_str==SS_variables[0]) and (file_satellite_str==satellite_code) and (file_station_str==station_name):
            # 找到对应日期的 el 文件
            el_file = None
            for f in os.listdir(output_el_folder):
                # 如果日期和卫星号和测站名匹配，则找到对应的 EL 文件
                if file_date_str in f and satellite_code in f and station_name in f:
                    el_file = f
                    break

            if el_file is not None:
                # 检查输出文件是否已经存在
                output_file = os.path.join(output_cn_el_folder, f"{os.path.splitext(cn_file)[0]}_el.csv")
                if os.path.exists(output_file):
                    print(f"File {output_file} already exists. Skipping...")
                    continue

                el_file_path = os.path.join(output_el_folder, el_file)

                # 读取文件1 (CN file) 和 文件2 (EL file)
                cn_df = pd.read_csv(cn_file_path)
                el_df = pd.read_csv(el_file_path)

                # 合并两个文件的数据
                # 合并两个文件的数据，使用列索引号进行操作
                merged_df = pd.merge(cn_df, el_df, left_on=cn_df.columns[0], right_on=el_df.columns[0],
                                     suffixes=('_cn', '_el'))
                merged_df = merged_df[[cn_df.columns[0], cn_df.columns[1], el_df.columns[1]]]
                merged_df.columns = ['Timestamp', 'CN value', 'el value']

                # 输出新的包含 timestamp-cn value-el value 的 csv 表格
                merged_df.to_csv(output_file, index=False)
                print(f"Saved merged file: {output_file}")
            else:
                print(f"No corresponding EL file found for {cn_file}")
        else:
            print(f"File {cn_file} is not in the date range.")