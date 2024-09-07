import gnsspy as gp
import os
import pandas as pd
import utils

def read_CN_value_from_obs(station_name, SS_variables, satellite_code, input_folder, output_folder, start_date_str, end_date_str):
    def list_files_in_directory(directory_path):
        if not os.path.exists(directory_path):
            raise ValueError(f"Directory {directory_path} does not exist.")
        return [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

    # 解析 start_date 和 end_date
    start_date = pd.to_datetime(start_date_str, format='%Y%j')
    end_date = pd.to_datetime(end_date_str, format='%Y%j')

    # 获取输入文件夹中的所有文件
    files_array = sorted(list_files_in_directory(input_folder))

    # 创建输出目录
    utils.create_directory_if_not_exists(output_folder)

    # 处理每个文件并保存对应的CSV文件
    for file in files_array:
        try:
            # 提取文件名中的日期并转换为 datetime 对象
            file_date_str = file[12:19]  # 假设文件名中日期格式为 'YYYYDOY'
            file_date = pd.to_datetime(file_date_str, format='%Y%j')
        except ValueError:
            print(f"Skipping file {file} due to invalid date format")
            continue

        # 检查文件日期是否在指定范围内
        if not (start_date <= file_date <= end_date):
            print(f"File {file} is not in the date range. Skipping...")
            continue

        filename_base = os.path.splitext(file)[0]
        if filename_base[0:4] != station_name:
            print(f"File {file} does not match station name. Skipping...")
            continue

        output_filename = f'{filename_base[0:4]}_{filename_base[12:19]}_CN_{satellite_code}_{SS_variables[0]}.csv'
        output_path = os.path.join(output_folder, output_filename)

        # 检查输出文件是否已经存在
        if os.path.exists(output_path):
            print(f"File {output_path} already exists. Skipping...")
            continue

        file_path = os.path.join(input_folder, file)
        BAIE_obs = gp.read_obsFile(file_path)

        # 对每个 SS_variable 提取数据
        for SS_variable in SS_variables:
            if SS_variable in BAIE_obs.observation:
                data = []
                for entry in BAIE_obs.observation[SS_variable].items():
                    timestamp, code = entry[0]
                    value = entry[1]
                    if code == satellite_code:
                        data.append((timestamp, value))

                # 如果有数据则保存为CSV文件
                if data:
                    df = pd.DataFrame(data, columns=['Timestamp', SS_variable])
                    full_path = os.path.join(output_folder, output_filename)
                    df.to_csv(full_path, index=False)
                    print(f"Saved: {full_path}")
                else:
                    print(f"No data for {satellite_code} and {SS_variable} in file {file}")
            else:
                print(f"Warning: {SS_variable} not found in file {file}")

# Read CN value from obs all at once
def read_CN_value_from_obs_AAO(station_name, SS_variables, satellite_code, input_folder, output_folder, start_date_str,
                               end_date_str):
    def list_files_in_directory(directory_path):
        if not os.path.exists(directory_path):
            raise ValueError(f"Directory {directory_path} does not exist.")
        return [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

    # 解析 start_date 和 end_date
    start_date = pd.to_datetime(start_date_str, format='%Y%j')
    end_date = pd.to_datetime(end_date_str, format='%Y%j')

    # 获取输入文件夹中的所有文件
    files_array = sorted(list_files_in_directory(input_folder))

    # 创建输出目录
    utils.create_directory_if_not_exists(output_folder)

    # 处理每个文件并保存对应的CSV文件
    for file in files_array:
        try:
            # 提取文件名中的日期并转换为 datetime 对象
            file_date_str = file[12:19]  # 假设文件名中日期格式为 'YYYYDOY'
            file_date = pd.to_datetime(file_date_str, format='%Y%j')
        except ValueError:
            print(f"Skipping file {file} due to invalid date format")
            continue

        # 检查文件日期是否在指定范围内
        if not (start_date <= file_date <= end_date):
            print(f"File {file} is not in the date range. Skipping...")
            continue

        filename_base = os.path.splitext(file)[0]
        if filename_base[0:4] != station_name:
            print(f"File {file} does not match station name. Skipping...")
            continue

        file_path = os.path.join(input_folder, file)
        BAIE_obs = gp.read_obsFile(file_path)

        # 对每个 SS_variable 提取数据并按 code 保存
        for SS_variable in SS_variables:
            if SS_variable in BAIE_obs.observation:
                # 创建一个字典来保存不同 code 的数据
                satellite_data = {}

                for entry in BAIE_obs.observation[SS_variable].items():
                    timestamp, code = entry[0]
                    value = entry[1]

                    # 如果 code 以 "G" 开头，保存到对应的列表中
                    if code.startswith('G'):
                        if code not in satellite_data:
                            satellite_data[code] = []
                        satellite_data[code].append((timestamp, value))

                # 将不同 code 的数据分别保存到不同的 CSV 文件中
                for code, data in satellite_data.items():
                    if data:
                        output_filename = f'{filename_base[0:4]}_{filename_base[12:19]}_CN_{code}_{SS_variables[0]}.csv'
                        output_path = os.path.join(output_folder, output_filename)

                        if not os.path.exists(output_path):  # 检查输出文件是否已存在
                            df = pd.DataFrame(data, columns=['Timestamp', SS_variable])
                            df.to_csv(output_path, index=False)
                            print(f"Saved: {output_path}")
                        else:
                            print(f"File {output_path} already exists. Skipping...")
            else:
                print(f"Warning: {SS_variable} not found in file {file}")