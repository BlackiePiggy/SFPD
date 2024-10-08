clc; clear all;close all;

year = '2020';
station = 'AIRA';
signal = 'S2W';
satno = 'G05';

start_date = '9/10'; % 起始日期
end_date = '9/15';   % 结束日期
date_full1 = [year, '/', start_date]; % 起始日期完整表示
date_full2 = [year, '/', end_date];   % 结束日期完整表示

% 文件路径
full_path = ['F:\data\dataset\', year, '\', station, '\', station, '_', year, '_', signal, '_', satno, '.csv'];

% 读取CSV文件
data = readtable(full_path);

% 提取第一列（时间戳）和第二列（数值）
timestamps = data{:,1}; % 时间戳
values = data{:,2};     % 数值

% 将时间戳转换为datetime格式
timestamps = datetime(timestamps, 'InputFormat', 'yyyy/M/d HH:mm:ss');

% 获取起始日期和结束日期的datetime
start_date_dt = datetime(date_full1, 'InputFormat', 'yyyy/M/d');
end_date_dt = datetime(date_full2, 'InputFormat', 'yyyy/M/d');

% 初始化DTW距离的数组
days_count = days(end_date_dt - start_date_dt) + 1; % 计算天数
dtw_distances = zeros(1, days_count);
dates_list = start_date_dt:end_date_dt; % 日期数组

% 绘制多日数据在同一张图上
figure;
subplot(2,1,1); % 创建一个两行一列的子图
hold on;

colors = lines(days_count); % 使用不同颜色

for i = 1:days_count
    current_date = dates_list(i);
    idx_current_date = (timestamps >= current_date) & (timestamps < current_date + days(1));
    
    % 提取当前日期的数据
    time_current = timestamps(idx_current_date);
    value_current = values(idx_current_date);
    
    % 对当前日期数据中的NaN值进行线性插值
    value_current_interp = fillmissing(value_current, 'linear');
    
    % 将时间戳转换为以时分秒为单位
    time_plot = timeofday(time_current);
    
    % 绘制当前日期的数据
    plot(time_plot, value_current_interp, '.', 'Color', colors(i, :), 'DisplayName', datestr(current_date, 'yyyy/mm/dd'));
end

xlabel('Time of Day');
ylabel('Value');
title('Data for Multiple Days');
legend;
grid on;
hold off;

% 计算每一天与起始日期的数据的DTW并绘制柱状图
% 提取起始日期的数据
idx_start_date = (timestamps >= start_date_dt) & (timestamps < start_date_dt + days(1));
value_start = values(idx_start_date);
value_start_interp = fillmissing(value_start, 'linear');

for i = 1:days_count
    current_date = dates_list(i);
    idx_current_date = (timestamps >= current_date) & (timestamps < current_date + days(1));
    
    % 提取当前日期的数据
    value_current = values(idx_current_date);
    
    % 确保两天的数据长度一致，截断长的序列
    min_len = min(length(value_start_interp), length(value_current));
    value_current = value_current(1:min_len);
    value_start_interp_short = value_start_interp(1:min_len);
    
    % 对当前日期数据中的NaN值进行线性插值
    value_current_interp = fillmissing(value_current, 'linear');
    
    % 计算DTW距离
    dtw_distances(i) = dtw(value_start_interp_short, value_current_interp);
end

% 绘制每日与起始日期的DTW距离的柱状图
subplot(2,1,2); % 第二个子图
bar(dates_list, dtw_distances); % 使用柱状图绘制DTW距离
xlabel('Date');
ylabel('DTW Distance');
title('DTW Distance between Start Date and Each Day in the Range');
xtickformat('MM/dd'); % 设置横坐标日期格式
grid on;
