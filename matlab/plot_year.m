clear all; clc;

year = '2020';
station = 'AIRA';
signal = 'S2W';
path = 'D:\projects\SFPDpy\DTW_result\';

filename_pattern = [station, '_', year, '_', signal, '_', '*', '_DTW.csv'];
filenamepath_pattern = [path, filename_pattern];

% 获取所有符合条件的文件列表
filelist = dir(filenamepath_pattern);

% 初始化一个结构体来存储所有的数据
data_struct = struct();

% 遍历所有文件，读取数据并将其存储在数组中
for k = 1:length(filelist)
    % 读取当前文件的数据
    filepath = fullfile(filelist(k).folder, filelist(k).name);
    data = readtable(filepath, 'ReadVariableNames', false);
    
    % 获取文件名中的 '*' 部分作为数组名称
    [~, filename, ~] = fileparts(filelist(k).name);
    tokens = strsplit(filename, '_');
    column_name = tokens{4};  % 第四个元素是'*'的位置

    % 将数据保存到以 column_name 命名的数组中
    data_struct.(column_name) = data.Var1;  % 假设数据在第一列

end

% 绘制时间序列图
figure;
hold on;
field_names = fieldnames(data_struct);
for i = 1:length(field_names)
    plot(data_struct.(field_names{i}), 'DisplayName', field_names{i});
end
hold off;

% 添加图例和标签
legend show;
xlabel('Time');
ylabel('Value');
title(['Time Series Data for Station: ' station ', Year: ' year ', Signal: ' signal]);

