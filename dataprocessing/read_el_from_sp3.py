import os
import numpy as np
import pandas as pd
import datetime
from pyproj import Transformer
import utils

def read_el_from_sp3(station_name, inputdir, output_folder, satellite_range, station_llh, start_date_str, end_date_str):
    utils.create_directory_if_not_exists(output_folder) # 如果没有文件夹，创建文件夹

    # 解析 start_date 和 end_date
    start_date = pd.to_datetime(start_date_str, format='%Y%j')  # 处理数据开始日期
    end_date = pd.to_datetime(end_date_str, format='%Y%j')  # 处理数据结束日期

    # 加入对inputdir文件排序

    # 遍历data文件夹下的所有SP3文件，并进行插值
    for file in os.listdir(inputdir):
        if file.endswith('.SP3'):
            try:
                # 提取文件名中的日期并转换为 datetime 对象
                file_date_str = file[11:18]  # 假设文件名中日期格式为 'YYYYDOY'
                file_date = pd.to_datetime(file_date_str, format='%Y%j')
            except ValueError:
                print(f"Skipping file {file} due to invalid date format")
                continue

            # 检查文件日期是否在指定范围内
            if not (start_date <= file_date <= end_date):
                print(f"File {file} is not in the date range. Skipping...")
                continue

            filename = os.path.join(inputdir, file)

            result = calculate_satellite_elevations(filename, station_llh, output_folder, satellite_range, station_name)


def calculate_satellite_elevations(filename, station_llh, output_folder,satellite_range, station_name):
    """
    计算卫星仰角并将结果保存到CSV文件。

    参数:
    filename (str): SP3文件的路径
    station_llh (list): 测站的经纬度和高度 [纬度, 经度, 高度]

    返回:
    int: 0表示执行成功，1表示执行失败
    """
    try:
        # 第一步：解析sp3文件，获取时间戳-卫星位置对应的15min间隔数据
        [epochs, sat_data] = parse_sp3_file(filename)

        # 遍历satellite_range中的每一个卫星，执行下面的内容
        for satellite_code in satellite_range:
            # 只保留指定的卫星
            if satellite_code not in sat_data:
                raise ValueError(f"Satellite {satellite_code} not found in the SP3 file.")

            sat_single_data = {satellite_code: sat_data[satellite_code]}

            # 第二步，对epochs和sat_data进行插值
            new_epochs = create_new_epochs(epochs)

            # 对sat_data每个卫星的值进行插值
            for sat_id in sat_single_data:
                for coord in ['x', 'y', 'z']:
                    df = pd.DataFrame({'epoch': epochs, 'values': sat_single_data[sat_id][coord]})
                    df.set_index('epoch', inplace=True)
                    new_df = df.resample('30s').interpolate(method='linear')
                    new_values = new_df.reindex(new_epochs).values.flatten()
                    sat_single_data[sat_id][coord] = new_values

            # 第三步：对每个时间戳，计算卫星的仰角
            # 计算station的ecef坐标
            sta_x, sta_y, sta_z = llh_to_ecef(station_llh[0], station_llh[1], station_llh[2])

            # 遍历每颗卫星
            for sat_id in sat_single_data:
                elevation_data = []

                # 遍历每个时间戳，求解那一时刻的仰角
                for i, epoch in enumerate(new_epochs):
                    sat_x, sat_y, sat_z = sat_single_data[sat_id]['x'][i], sat_single_data[sat_id]['y'][i], sat_single_data[sat_id]['z'][i]
                    sat_ecef = [sat_x, sat_y, sat_z]

                    # 计算仰角
                    elevation = calc_el_angle(sat_ecef, [sta_x, sta_y, sta_z], station_llh[0], station_llh[1])

                    # 将当前的epoch和仰角对应存储到变量中
                    elevation_data.append({'Timestamp': epoch, 'elevation': elevation})

                # 将当前卫星的仰角结果保存到一个CSV文件中
                df = pd.DataFrame(elevation_data)

                filename_nopath = os.path.basename(filename)
                outfilename = f'elevation_{station_name}_{filename_nopath[11:18]}_{satellite_code}.csv'
                full_path = os.path.join(output_folder, outfilename)

                # 检测输出文件是否已经存在
                if os.path.exists(full_path):
                    print(f"File {full_path} already exists. Skipping...")
                    continue
                else:
                    df.to_csv(full_path, index=False)
                    print(f"Execution result for {full_path}:", "Success")

                del elevation_data

        return 0  # 执行成功
    except Exception as e:
        print(f"An error occurred: {e}")
        return 1  # 执行失败


def parse_sp3_file(filename):
    # Initialize variables
    epochs = []
    sat_data = {}

    # Open and read the file
    with open(filename, 'r') as file:
        for line in file:
            # Check if it's an epoch line
            if line[0] == '*':
                # Parse epoch
                year = int(line[3:7])
                month = int(line[8:10])
                day = int(line[11:13])
                hour = int(line[14:16])
                minute = int(line[17:19])
                second = float(line[20:31])
                current_epoch = datetime.datetime(year, month, day, hour, minute, int(second), int((second % 1) * 1e6))
                epochs.append(current_epoch)

            # Check if it's a satellite position line
            elif line[0] == 'P':
                # Parse satellite data
                sat_id = line[1:4]
                x = float(line[4:18])
                y = float(line[18:32])
                z = float(line[32:46])
                clock_bias = float(line[46:60])

                # Store the data
                if sat_id not in sat_data:
                    sat_data[sat_id] = {'x': [], 'y': [], 'z': [], 'clock_bias': []}
                sat_data[sat_id]['x'].append(x)
                sat_data[sat_id]['y'].append(y)
                sat_data[sat_id]['z'].append(z)
                sat_data[sat_id]['clock_bias'].append(clock_bias)

    return epochs, sat_data

def llh_to_ecef(lat, lon, h):
    # 创建一个从 WGS84 (EPSG:4326) 到 ECEF (EPSG:4978) 的转换器
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:4978", always_xy=True)

    # 使用转换器将经纬度和高程转换为 ECEF 坐标
    x, y, z = transformer.transform(lon, lat, h)
    return x, y, z

def create_new_epochs(epochs):
    # Convert epochs to pandas datetime if it's not already
    if not isinstance(epochs, pd.DatetimeIndex):
        epochs = pd.to_datetime(epochs)

    # Create new epochs
    start_time = epochs[0]
    end_time = epochs[-1] - pd.Timedelta(minutes=0, seconds=30)
    new_epochs = pd.date_range(start=start_time, end=end_time, freq='30s')

    return new_epochs

def calc_el_angle(sat_ecef, sta_ecef, lat0, lon0):
    # Calculate LOS vector in ECEF coordinates
    sat_ecef_np = np.array(sat_ecef)*1000
    sta_ecef_np = np.array(sta_ecef)

    # Extract station ECEF coordinates
    xr, yr, zr = sta_ecef_np

    # Convert satellite ECEF coordinates to ENU
    xs, ys, zs = sat_ecef_np

    dx = xs - xr; dy = ys - yr; dz = zs - zr
    e,n,u = ecef2enu(dx, dy, dz, lat0, lon0)

    # Calculate elevation angle
    elevation_rad = np.arctan2(u, np.sqrt(e ** 2 + n ** 2))
    elevation = np.degrees(elevation_rad)

    return elevation


# 定义转换函数
def ecef2enu(u, v, w, lat0, lon0):
    """
    Rotate Cartesian 3-vector from ECEF to ENU

    Parameters:
    u, v, w -- Cartesian coordinates in ECEF
    lat0, lon0 -- Origin latitude and longitude
    sinfun, cosfun -- Function handles to sine and cosine functions (either np.sin/np.cos or np.sin/np.cos for degrees)

    Returns:
    uEast, vNorth, wUp -- Converted coordinates in ENU
    """
    cosPhi = np.cos(np.radians(lat0))
    sinPhi = np.sin(np.radians(lat0))
    cosLambda = np.cos(np.radians(lon0))
    sinLambda = np.sin(np.radians(lon0))

    t = cosLambda * u + sinLambda * v
    uEast = -sinLambda * u + cosLambda * v

    wUp = cosPhi * t + sinPhi * w
    vNorth = -sinPhi * t + cosPhi * w

    return uEast, vNorth, wUp
