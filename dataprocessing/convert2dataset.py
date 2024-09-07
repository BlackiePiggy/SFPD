import os
import pandas as pd


def read_and_process_test_files(SS_variables, satellite_code, anomaly_inserted_folder, dataset_folder, start_date_str, end_date_str, test_index):
    start_date = pd.to_datetime(start_date_str, format='%Y%j')
    end_date = pd.to_datetime(end_date_str, format='%Y%j')
    os.makedirs(dataset_folder, exist_ok=True)

    file_name = f'anomaly_inserted_{satellite_code}_{SS_variables[0]}_{start_date_str}_{end_date_str}.csv'
    file_path = os.path.join(anomaly_inserted_folder, file_name)

    testlabel_file = os.path.join(anomaly_inserted_folder, f'test_label_time_{satellite_code}_{SS_variables[0]}.csv')

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)

        # 删除第三列
        df.drop(df.columns[2], axis=1, inplace=True)

        # 将第一列的值替换为从 test_index 开始的索引
        df.iloc[:, 0] = range(test_index, test_index + len(df))

        # 保存处理后的文件
        output_file = os.path.join(dataset_folder, f'test_{satellite_code}_{SS_variables[0]}.csv')
        df.to_csv(output_file, index=False)
        print(f"Saved processed data to {output_file}")
    else:
        print(f"No file found for the specified date range: {file_name}")

    if os.path.exists(testlabel_file):
        df = pd.read_csv(testlabel_file)

        # 将第一列的值替换为从 test_index 开始的索引
        df.iloc[:, 0] = range(test_index, test_index + len(df))

        # 保存处理后的文件
        output_file = os.path.join(dataset_folder, f'test_label_{satellite_code}_{SS_variables[0]}.csv')
        df.to_csv(output_file, index=False)
        print(f"Saved processed data to {output_file}")
    else:
        print(f"No file found for the specified date range: {file_name}")


def read_and_process_train_files(SS_variables, satellite_code, train_time_cn_el_filtered_folder, dataset_folder, start_date_str, end_date_str, train_index):
    start_date = pd.to_datetime(start_date_str, format='%Y%j')
    end_date = pd.to_datetime(end_date_str, format='%Y%j')
    os.makedirs(dataset_folder, exist_ok=True)

    file_name = f'combined_{satellite_code}_{SS_variables[0]}_{start_date_str}_{end_date_str}.csv'
    file_path = os.path.join(train_time_cn_el_filtered_folder, file_name)

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)

        # 删除第三列
        df.drop(df.columns[2], axis=1, inplace=True)

        # 将第一列的值替换为从 test_index 开始的索引
        df.iloc[:, 0] = range(train_index, train_index + len(df))

        test_index = train_index + len(df)

        # 保存处理后的文件
        output_file = os.path.join(dataset_folder, f'train_{satellite_code}_{SS_variables[0]}.csv')
        df.to_csv(output_file, index=False)
        print(f"Saved processed data to {output_file}")

        return test_index
    else:
        print(f"No file found for the specified date range: {file_name}")
        return None  # 如果文件不存在，返回 None