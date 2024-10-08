%% Step 0: Initialize
clear all; clc; close all;

% 手动赋值
station = 'BAIE'; % 替换为实际的站点名称
year = '2021';    % 替换为实际的年份
signal = 'S2W';   % 替换为实际的信号名称

% 设置输入和输出文件夹
inputFolder = 'F:\data\result\ver3\DTW_results\';
outputFolder = 'F:\data\result\ver3\DTW_detection_result\';
consolidatedOutputFolder = 'F:\data\result\ver3\consolidated_results\';
imageOutputFolder = 'F:\data\result\ver3\outlier_detection_plots\';

% 创建输出文件夹（如果不存在）
for folder = {outputFolder, consolidatedOutputFolder, imageOutputFolder}
    if ~exist(folder{1}, 'dir')
        mkdir(folder{1});
    end
end

% 初始化变量来存储所有日期和数据
allDates = datetime.empty;
allData = cell(1, 32); % 用于存储32颗卫星的数据

% 定义日期转DOY的函数
dateToDOY = @(date) day(date, 'dayofyear');

%% Step 1: Process each satellite
for satNum = 1:32
    % Format satellite number with leading zero
    sat = sprintf('G%02d', satNum); % Generate satellite ID (G01, G02, ..., G32)
    
    % Construct file path
    filePath = fullfile(inputFolder, [station '_' year '_' signal '_' sat '_DTW.csv']);
    
    % Check if the file exists before attempting to read it
    if isfile(filePath)
        % Read data, handling non-numeric elements as NaN
        data = readtable(filePath);
        dates = datetime(data{:, 1}); % 第一列为日期，确保转换为datetime类型
        cellValues = data{:, 2}; % 第二列为cell数组
        
        % Check if cellValues is a cell array
        if iscell(cellValues)
            % Convert cell array to numeric array
            values = cell2mat(cellfun(@str2double, cellValues, 'UniformOutput', false));
        else
            % Directly assign values if it's already a numeric array
            values = double(cellValues); % Ensure it's double type, if necessary
        end
        
        % 检查数值列中的非数值元素，将其标记为 NaN
        values(~isnumeric(values)) = NaN;
        
        %% 方法1 IQR 四分位距法
        % 手动设置检测阈值的倍数因子
        multiplier = 9; % 1.5为默认值，可以手动调整
        
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
        
        % 绘制图形并保存
        fig = figure('Visible', 'off'); % 创建图形但不显示
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
        title(['Time Series Data with Outliers - ' station ' ' year ' - ' sat]);
        
        % 显示图例
        legend('Non-Outlier Data', 'Outliers');
        
        hold off;
        
        % 保存图片
        imagePath = fullfile(imageOutputFolder, [station '_' year '_' signal '_' sat '_OutlierDetection.png']);
        saveas(fig, imagePath);
        close(fig); % 关闭图形
        
        % 计算DOY
        doy = arrayfun(dateToDOY, dates);
        
        % 输出结果为CSV文件
        outputTable = table(dates, doy, double(isOutlier), 'VariableNames', {'Date', 'DOY', 'IsOutlier'}); % 创建输出表格
        outputPath = fullfile(outputFolder, [station '_' year '_' signal '_' sat '_OutlierDetectionResults.csv']); % 输出路径
        writetable(outputTable, outputPath); % 写入CSV文件
        
        % 将日期添加到allDates中
        allDates = unique([allDates; dates]);
        
        % 存储卫星数据
        dateStrings = datestr(dates, 'yyyy-mm-dd HH:MM:SS');
        allData{satNum} = containers.Map(cellstr(dateStrings), num2cell(double(isOutlier)));
    else
        fprintf('File not found: %s\n', filePath); % 如果文件不存在，输出提示信息
    end
end

%% Step 2: Consolidate data
% 对日期进行排序
allDates = sort(allDates);

% 计算所有日期的DOY
allDOY = arrayfun(dateToDOY, allDates);

% 创建输出数据矩阵
outputData = NaN(length(allDates), 34); % 34列：1列日期 + 1列DOY + 32列卫星数据
outputData(:,1) = datenum(allDates); % 将日期转换为数值
outputData(:,2) = allDOY; % 添加DOY列

% 填充数据
for satNum = 1:32
    if ~isempty(allData{satNum})
        dateStrings = datestr(allDates, 'yyyy-mm-dd HH:MM:SS');
        for i = 1:length(allDates)
            if isKey(allData{satNum}, dateStrings(i,:))
                outputData(i, satNum+2) = allData{satNum}(dateStrings(i,:));
            end
        end
    end
end

% 创建表格
varNames = ['Date', 'DOY', arrayfun(@(x) sprintf('G%02d', x), 1:32, 'UniformOutput', false)];
outputTable = array2table(outputData, 'VariableNames', varNames);

% 将日期列转换回日期格式
outputTable.Date = datetime(outputTable.Date, 'ConvertFrom', 'datenum');

% 写入CSV文件
consolidatedOutputPath = fullfile(consolidatedOutputFolder, [station '_' year '_' signal '_ConsolidatedResults.csv']);
writetable(outputTable, consolidatedOutputPath);

fprintf('处理完成。\n');
fprintf('异常值检测结果已保存至: %s\n', outputFolder);
fprintf('异常值检测图片已保存至: %s\n', imageOutputFolder);
fprintf('合并后的文件已保存至: %s\n', consolidatedOutputPath);