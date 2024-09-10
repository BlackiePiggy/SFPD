clc; clear all;

year = '2020';
station = 'AIRA';
signal = 'S2W';
satno = 'G01';

full_path = ['F:\data\result\ver3\DTW_results\',  station, '_',year,  '_',signal,'_',satno,'_DTW.csv'];

% 读取full_path对应的csv文件
data = readtable(full_path);

% 提取第一列（时间戳）和第二列（数值）
timestamps = data{:,1}; % 时间戳
values = data{:,2};     % 数值

% 将时间戳转换为datetime格式
timestamps = datetime(timestamps, 'InputFormat', 'yyyy/M/d HH:mm:ss');

figure;
plot(timestamps, values, '.r'); % date1的点图，用红色圆点表示
