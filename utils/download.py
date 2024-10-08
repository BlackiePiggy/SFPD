import datetime
import pandas as pd
from ftplib import FTP_TLS, error_perm, error_temp
import gzip
import shutil
import os
import subprocess
import time


# 函数：将日期转换为 GPS 周和周内的天数
def date_to_gps_week_day(date):
    gps_start = datetime.datetime(1980, 1, 6)
    delta = date - gps_start
    gps_week = delta.days // 7
    gps_day = delta.days % 7
    return gps_week, gps_day


# 函数：将日期转换为年份和DOY
def date_to_year_doy(date):
    year = date.year
    doy = (date - datetime.datetime(year, 1, 1)).days + 1
    return year, doy


# 函数：连接FTP服务器
def connect_to_ftp():
    print("正在初始化与FTP服务器的连接...")
    try:
        ftp = FTP_TLS('gdc.cddis.eosdis.nasa.gov')
        print("成功建立与FTP服务器的连接。")

        print("正在尝试登录...")
        ftp.login()
        print("登录成功。")

        print("正在切换到安全数据连接...")
        ftp.prot_p()  # 切换到加密的数据连接
        print("已建立安全数据连接。")

        return ftp
    except Exception as e:
        print(f"连接FTP服务器时出错: {e}")
        raise


# 函数：从FTP服务器下载文件并解压
def download_and_extract_files(start_date, end_date, save_path_obs, save_path_sp3, station_name, download_obs=False,
                               download_sp3=True):
    if not os.path.exists(save_path_obs):
        os.makedirs(save_path_obs)
        print(f"创建目录: {save_path_obs}")
    if not os.path.exists(save_path_sp3):
        os.makedirs(save_path_sp3)
        print(f"创建目录: {save_path_sp3}")

    # 连接FTP服务器
    print("正在连接FTP服务器...")
    ftp = connect_to_ftp()
    print("FTP连接成功建立。")

    day_count = 0
    start_time = time.time()

    current_year = start_date.year

    # 遍历日期范围
    for single_date in pd.date_range(start=start_date, end=end_date):
        print(f"\n正在处理日期: {single_date.strftime('%Y-%m-%d')}")

        if single_date.year != current_year:
            current_year = single_date.year
            save_path_obs = f"F:/data/obs/{station_name}/{current_year}"
            save_path_sp3 = f'F:/data/sp3/{current_year}'
            if not os.path.exists(save_path_obs):
                os.makedirs(save_path_obs)
                print(f"为obs数据创建新目录: {save_path_obs}")
            if not os.path.exists(save_path_sp3):
                os.makedirs(save_path_sp3)
                print(f"为sp3数据创建新目录: {save_path_sp3}")

        gps_week, gps_day = date_to_gps_week_day(single_date)
        year, doy = date_to_year_doy(single_date)
        year_short = single_date.strftime('%y')
        doy_padded = f'{doy:03d}'

        # 下载obs文件
        if download_obs:
            obs_filename = f'{station_name}00USA_S_{year}{doy_padded}0000_01D_30S_MO.crx.gz'
            obs_directory = f'/pub/gps/data/daily/{year}/{doy_padded}/{year_short}d/'
            local_obs_gz_filename = os.path.join(save_path_obs, obs_filename)
            local_obs_filename = os.path.join(save_path_obs, obs_filename[:-3])

            # 检查文件是否已经存在
            if os.path.exists(local_obs_filename.replace(".crx", ".cro")):
                print(f'{local_obs_filename.replace(".crx", ".cro")} 已存在，跳过下载。')
            else:
                max_retries = 3
                retry_delay = 5
                for attempt in range(max_retries):
                    try:
                        print(f"正在下载 {obs_filename}...")
                        with open(local_obs_gz_filename, 'wb') as file:
                            ftp.retrbinary(f'RETR {obs_directory}{obs_filename}', file.write)
                        print(f'成功下载 {local_obs_gz_filename}')

                        print(f"正在解压 {local_obs_gz_filename}...")
                        with gzip.open(local_obs_gz_filename, 'rb') as f_in:
                            with open(local_obs_filename, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        print(f'成功解压到 {local_obs_filename}')

                        # 修改文件后缀为.crd
                        new_crx_filename = local_obs_filename.replace(".crx", ".crd")
                        os.rename(local_obs_filename, new_crx_filename)
                        print(f"重命名文件为 {new_crx_filename}")

                        # 执行cmd命令行进行转换
                        print("正在执行crx2rnx转换...")
                        cmd = f'D:\\OneDrive\\GNSS_DATA\\crx2rnx.exe {new_crx_filename}'
                        subprocess.run(cmd, shell=True)
                        print("crx2rnx转换完成")

                        # 删除不需要的文件
                        if os.path.exists(new_crx_filename):
                            os.remove(new_crx_filename)
                            print(f"删除中间文件 {new_crx_filename}")
                        if os.path.exists(local_obs_gz_filename):
                            os.remove(local_obs_gz_filename)
                            print(f"删除压缩文件 {local_obs_gz_filename}")
                        break
                    except error_perm as e:
                        if str(e).startswith('550'):  # File not found
                            print(f"服务器上未找到文件 {obs_filename}，跳过。")
                            break
                        else:
                            raise
                    except error_temp as e:
                        if attempt < max_retries - 1:
                            print(f"临时错误: {e}。{retry_delay} 秒后重试...")
                            time.sleep(retry_delay)
                        else:
                            print(f"尝试 {max_retries} 次后仍无法下载 {obs_filename}。")
                            break
                    except Exception as e:
                        if 'EOF occurred in violation of protocol (_ssl.c:2427)' in str(e):
                            print('发生EOF错误，正在重新连接FTP服务器...')
                            ftp = connect_to_ftp()
                        else:
                            print(f'处理 {local_obs_gz_filename} 时出错: {e}')
                            break

        # 下载sp3文件
        if download_sp3:
            sp3_filename = f'COD0MGXFIN_{year}{doy_padded}0000_01D_05M_ORB.SP3.gz'
            sp3_directory = f'/pub/gps/products/{gps_week}/'
            local_sp3_gz_filename = os.path.join(save_path_sp3, sp3_filename)
            local_sp3_filename = os.path.join(save_path_sp3, f'COD0MGXFIN_{year}{doy_padded}0000_01D_05M_ORB.SP3')

            # 检查文件是否已经存在
            if os.path.exists(local_sp3_filename):
                print(f'{local_sp3_filename} 已存在，跳过下载。')
            else:
                max_retries = 3
                retry_delay = 5
                for attempt in range(max_retries):
                    try:
                        print(f"正在下载 {sp3_filename}...")
                        with open(local_sp3_gz_filename, 'wb') as file:
                            ftp.retrbinary(f'RETR {sp3_directory}{sp3_filename}', file.write)
                        print(f'成功下载 {local_sp3_gz_filename}')

                        print(f"正在解压 {local_sp3_gz_filename}...")
                        with gzip.open(local_sp3_gz_filename, 'rb') as f_in:
                            with open(local_sp3_filename, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        print(f'成功解压到 {local_sp3_filename}')

                        # 删除压缩文件
                        os.remove(local_sp3_gz_filename)
                        print(f"删除压缩文件 {local_sp3_gz_filename}")
                        break
                    except error_perm as e:
                        if str(e).startswith('550'):  # File not found
                            print(f"服务器上未找到文件 {sp3_filename}，跳过。")
                            break
                        else:
                            raise
                    except error_temp as e:
                        if attempt < max_retries - 1:
                            print(f"临时错误: {e}。{retry_delay} 秒后重试...")
                            time.sleep(retry_delay)
                        else:
                            print(f"尝试 {max_retries} 次后仍无法下载 {sp3_filename}。")
                            break
                    except Exception as e:
                        if 'EOF occurred in violation of protocol (_ssl.c:2427)' in str(e):
                            print('发生EOF错误，正在重新连接FTP服务器...')
                            ftp = connect_to_ftp()
                        else:
                            print(f'处理 {local_sp3_gz_filename} 时出错: {e}')
                            break

        day_count += 1

        # 每下载10天的文件输出一次计时信息
        if day_count % 10 == 0:
            elapsed_time = time.time() - start_time
            print(f'已下载 {day_count} 天的文件，耗时: {elapsed_time:.2f} 秒')

    # 断开FTP连接
    print("正在关闭FTP连接...")
    ftp.quit()
    print("FTP连接已成功关闭。")


# 示例使用
if __name__ == "__main__":
    start_date = datetime.datetime(2020, 1, 1)
    end_date = datetime.datetime(2021, 12, 31)
    station_name = 'STFU'

    save_path_obs = f"F:/data/obs/{station_name}/{start_date.year}"
    save_path_sp3 = f'F:/data/sp3/{start_date.year}'

    print("开始下载和提取文件...")
    download_and_extract_files(start_date, end_date, save_path_obs, save_path_sp3, station_name, download_obs=True,
                               download_sp3=False)
    print("下载和提取过程完成。")