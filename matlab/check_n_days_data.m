clc; clear all;close all;

year = '2020';
station = 'AIRA';
signal = 'S2W';
satno = 'G05';

% 定义开始和结束日期
start_date = '2/14'; % 开始日期
end_date = '2/24';  % 结束日期

% 生成每一天的日期列表
dates = datetime([year,'/',start_date], 'InputFormat', 'yyyy/M/d'):days(1):datetime([year,'/',end_date], 'InputFormat', 'yyyy/M/d');

full_path = ['F:\data\dataset\', year, '\', station, '\',station,'_',year,'_',signal,'_',satno,'.csv'];

% 读取full_path对应的csv文件
data = readtable(full_path);

% 提取第一列（时间戳）和第二列（数值）
timestamps = data{:,1}; % 时间戳
values = data{:,2};     % 数值

% 将时间戳转换为datetime格式
timestamps = datetime(timestamps, 'InputFormat', 'yyyy/M/d HH:mm:ss');

% 创建图形窗口
figure;
hold on;

% 设置不同颜色列表
colors = ['r', 'b', 'g', 'm', 'c', 'y', 'k'];
num_colors = length(colors);

% 循环处理每一天的数据
for i = 1:length(dates)
    current_date = dates(i);  % 当前日期
    next_date = current_date + days(1);  % 下一天，用于筛选数据
    
    % 找出属于当前日期的数据
    idx_date = (timestamps >= current_date) & (timestamps < next_date);
    
    % 提取当前日期的数据
    time_current = timestamps(idx_date);
    value_current = values(idx_date);
    
    % 将时间戳转换为以时分秒为单位
    time_current_plot = timeofday(time_current);
    
    % 绘制当前日期的数据
    plot(time_current_plot, value_current, '-', 'Color', colors(mod(i-1, num_colors) + 1), 'DisplayName', datestr(current_date, 'yyyy/mm/dd'));
    
    % 检测NaN值，并标记
    nan_idx = isnan(value_current);
    plot(time_current_plot(nan_idx), zeros(sum(nan_idx), 1), 'x', 'MarkerSize', 10, 'LineWidth', 2, 'Color', colors(mod(i-1, num_colors) + 1));
end

xlabel('Time (HH:MM:SS)');
ylabel('Value');
title(['Data from ', start_date, ' to ', end_date]);
legend;
grid on;
hold off;
