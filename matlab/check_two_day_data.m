clc; clear all;

year = '2020';
station = 'BAIE';
signal = 'S2W';
satno = 'G15';

date1 = '6/8';
date2 = '6/7';
date_full1 = [year,'/',date1];
date_full2 = [year,'/',date2];

full_path = ['F:\data\dataset\', year, '\', station, '\',station,'_',year,'_',signal,'_',satno,'.csv'];

% 读取full_path对应的csv文件
data = readtable(full_path);

% 提取第一列（时间戳）和第二列（数值）
timestamps = data{:,1}; % 时间戳
values = data{:,2};     % 数值

% 将时间戳转换为datetime格式
timestamps = datetime(timestamps, 'InputFormat', 'yyyy/M/d HH:mm:ss');

% 分别找出属于date_full1和date_full2的数据
date_full1_dt = datetime(date_full1, 'InputFormat', 'yyyy/M/d');
date_full2_dt = datetime(date_full2, 'InputFormat', 'yyyy/M/d');

idx_date1 = (timestamps >= date_full1_dt) & (timestamps < date_full1_dt + days(1));
idx_date2 = (timestamps >= date_full2_dt) & (timestamps < date_full2_dt + days(1));

% 分别提取属于这两天的数据
time1 = timestamps(idx_date1);
value1 = values(idx_date1);

time2 = timestamps(idx_date2);
value2 = values(idx_date2);

% 将时间戳转换为以时分秒为单位
time1_plot = timeofday(time1); % 时分秒
time2_plot = timeofday(time2); % 时分秒

% 绘制图形，使用点绘制数据
figure;
hold on;
plot(time1_plot, value1, '.r', 'DisplayName', date_full1); % date1的点图，用红色圆点表示
plot(time2_plot, value2, '.b', 'DisplayName', date_full2); % date2的点图，用蓝色圆点表示

% 检测value1中的NaN值，并标记
nan_idx1 = isnan(value1);
plot(time1_plot(nan_idx1), zeros(sum(nan_idx1), 1), 'xr', 'MarkerSize', 10, 'LineWidth', 2);

% 检测value2中的NaN值，并标记
nan_idx2 = isnan(value2);
plot(time2_plot(nan_idx2), zeros(sum(nan_idx2), 1), 'xb', 'MarkerSize', 10, 'LineWidth', 2);

% 找出 time1 相比 time2 独有的点
[unique_time1, idx_unique_time1] = setdiff(time1_plot, time2_plot);
plot(unique_time1, zeros(size(unique_time1)), 'v', 'MarkerEdgeColor', 'b', 'MarkerFaceColor', 'b', 'MarkerSize', 5); % 蓝色三角标记

% 找出 time2 相比 time1 独有的点
[unique_time2, idx_unique_time2] = setdiff(time2_plot, time1_plot);
plot(unique_time2, zeros(size(unique_time2)), '^', 'MarkerEdgeColor', 'r', 'MarkerFaceColor', 'r', 'MarkerSize', 5); % 红色三角标记

% 打印两天的NaN值数量
fprintf('Date %s has %d NaN values.\n', date_full1, sum(nan_idx1));
fprintf('Date %s has %d NaN values.\n', date_full2, sum(nan_idx2));

xlabel('Time (HH:MM:SS)');
ylabel('Value');
title(['Data for ', date_full1, ' and ', date_full2]);
legend;
grid on;
hold off;
