clc; clear all;

year = '2020';
station = 'AIRA';
signal = 'S2W';
satno = 'G06';

date1 = '7/12';
date2 = '';
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

% 将两天的数据时间轴转换为以时分秒为单位
time1_plot = timeofday(time1); % 时分秒
time2_plot = timeofday(time2); % 时分秒

% 绘制图形，使用点绘制数据
figure;
hold on;
plot(time1_plot, value1, '.r', 'DisplayName', date_full1); % date1的点图，用红色圆点表示
plot(time2_plot, value2, '.b', 'DisplayName', date_full2); % date2的点图，用蓝色圆点表示
xlabel('Time (HH:MM:SS)');
ylabel('Value');
title(['Data for ', date_full1, ' and ', date_full2]);
legend;
grid on;
hold off;
