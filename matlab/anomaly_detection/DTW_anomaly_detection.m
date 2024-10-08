%% Step 0 Read data
clear all; clc; close all;
% 手动赋值
station = 'AIRA'; % 替换为实际的站点名称
year = '2020'; % 替换为实际的年份
signal = 'S2W'; % 替换为实际的信号名称
sat = 'G01'; % 替换为实际的卫星编号

% 构造文件路径
filePath = ['F:\data\result\ver3\DTW_results\' station '_' year '_' signal '_' sat '_DTW.csv'];

% 读取数据，处理非数值元素为 NaN
data = readtable(filePath);
dates = data{:, 1};  % 第一列为日期
values = data{:, 2}; % 第二列为数值

% 检查数值列中的非数值元素，将其标记为 NaN
values(~isnumeric(values)) = NaN;

%% 方法1 IQR 四分位距法
% 手动设置检测阈值的倍数因子
multiplier = 9;  % 1.5为默认值，可以手动调整

% 使用IQR方法进行异常值检测
Q1 = prctile(values, 25); % 第一四分位数
Q3 = prctile(values, 75); % 第三四分位数
IQR = Q3 - Q1;            % 四分位距

% 根据倍数因子调整上边界
upperBound = Q3 + multiplier * IQR; % 上边界

% 标记异常值
isOutlier = values > upperBound;

% 记录异常值和对应日期
outlierDates = dates(isOutlier);
outlierValues = values(isOutlier);

% 绘制图形
figure;
hold on;

% 绘制非异常值
scatter(dates(~isOutlier), values(~isOutlier), 'b', 'filled'); % 蓝色散点表示非异常数据

% 绘制异常值
scatter(dates(isOutlier), values(isOutlier), 'r', 'filled');   % 红色散点表示异常数据

% 添加上边界的红色虚线并标注具体数值
yline(upperBound, '--r', ['Upper Threshold: ' num2str(upperBound)], 'LabelHorizontalAlignment', 'left', 'LabelVerticalAlignment', 'bottom');

% 设置图形属性
xlabel('Date');
ylabel('Value');
title(['Time Series Data with Outliers - ' station ' ' year]);

% 显示图例
legend('Non-Outlier Data', 'Outliers');

hold off;

%% 输出结果为CSV文件
outputFolder = 'F:\data\result\ver3\DTW_detection_result\'; % 输出文件夹路径
mkdir(outputFolder); % 创建文件夹（如果不存在）

outputTable = table(dates, double(isOutlier), 'VariableNames', {'Date', 'IsOutlier'}); % 创建输出表格
outputPath = [outputFolder station '_' year '_' signal '_' sat '_OutlierDetectionResults.csv']; % 输出路径
writetable(outputTable, outputPath); % 写入CSV文件
