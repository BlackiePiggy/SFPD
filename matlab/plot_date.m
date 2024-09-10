clear all; clc; close all;

year = '2022';  % 指定年份
signal = 'S2W';
path = 'F:\data\result\ver3\DTW_results\';

% 定义站点列表
stations = {'AIRA', 'BAIE', 'BIK0', 'CAS1'};

% 动态加载 event_{year}_list.mat 文件
event_file = sprintf('event_%s_list.mat', year);

% 检查 event_file 是否存在
if isfile(event_file)
    load(event_file);  % 加载对应年份的 event_list 变量

    % 根据年份动态获取事件列表变量的名称
    event_list_var = sprintf('event_%s_list', year);

    % 使用 eval 获取对应的事件列表变量
    if exist(event_list_var, 'var')
        event_list = eval(event_list_var);  % 获取 event_{year}_list 的值
    else
        error('The event list for the specified year does not exist.');
    end

    % 动态构建事件的日期列表（假设 event_list 中是年中的日）
    event_datetime_list = datetime(str2double(year), 1, 1) + days(event_list - 1);
else
    event_datetime_list = [];  % 如果没有 event_file，事件日期列表为空
end

% 创建一个新的 figure
figure;

% 遍历站点列表
for station_idx = 1:length(stations)
    station = stations{station_idx};
    
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
        % 1. 先检测导入选项
        opts = detectImportOptions(filepath, 'ReadVariableNames', false);
        % 2. 强制将第二列的类型设置为 double
        opts = setvartype(opts, opts.VariableNames{2}, 'double');
        % 3. 按照修改后的导入选项读取表格
        data = readtable(filepath, opts);
                
        % 获取文件名中的 '*' 部分作为数组名称
        [~, filename, ~] = fileparts(filelist(k).name);
        tokens = strsplit(filename, '_');
        column_name = tokens{4};  % 第四个元素是'*'的位置
        
        % 将数据保存到以 column_name 命名的数组中
        data_struct.(column_name) = data;  % 添加到data_struct中
    end
    
    % 在对应的subplot中绘制时间序列图
    subplot(4, 1, station_idx);  % 将每个站点的图绘制在4行1列的子图中
    hold on;
    field_names = fieldnames(data_struct);
    for i = 1:length(field_names)
        % 检查 data_struct.(field_names{i}) 的维度
        if size(data_struct.(field_names{i}), 1) == 1
            disp(['Skipping: ', field_names{i}, ' due to 1x2 size']);
            continue;  % 如果维度是1x2，跳过
        end
        
        timeStrings = data_struct.(field_names{i}){:, 1};  % 提取时间字符串
        time = datetime(timeStrings, 'InputFormat', 'yyyy-MM-dd');  % 转换为 datetime 类型
        value = data_struct.(field_names{i}){:, 2};  % 提取值
        % 如果有value中有nan值，则不绘制这个点
        validIndices = ~isnan(value);
        
        validtime =  time(validIndices);
        validvalue = value(validIndices);
        % 归一化处理: 将值缩放到 [0, 1] 之间
        minVal = min(validvalue);
        maxVal = max(validvalue);
        normalizedValue = (validvalue - minVal) / (maxVal - minVal);
        plot(validtime, validvalue, 'o', 'DisplayName', field_names{i});  % 使用'o'表示点样式
        plot(validtime, normalizedValue, 'o', 'DisplayName', field_names{i});  % 使用'o'表示点样式
    end
    
    % 找到当天图的纵轴最大值
    ylim_values = ylim;
    max_value = ylim_values(2);
    
    % 如果有 event_datetime_list，则在事件日期上绘制'×'
    if ~isempty(event_datetime_list)
        for j = 1:length(event_datetime_list)
            plot(event_datetime_list(j), max_value, 'rx', 'MarkerSize', 10, 'LineWidth', 2);
        end
    end
    
    hold off;
    
    % 添加标签
    xlabel('Time');
    ylabel('Value');
    title(['Time Series for Station: ', station, ', Year: ', year, ', Signal: ', signal]);
end

% 在所有图绘制完成后，启用 datacursormode 并设置自定义提示信息
dcm = datacursormode(gcf);  % 启用数据提示模式
set(dcm, 'UpdateFcn', @myUpdateFcn);  % 设置自定义回调函数

% 自定义数据提示显示的回调函数
function txt = myUpdateFcn(~, event_obj)
    % 获取目标数据对象和当前数据点的索引
    target = get(event_obj, 'Target');  % 获取数据点的目标对象
    idx = event_obj.DataIndex;  % 获取当前数据点的索引

    % 获取该数据点的 'DisplayName'，即字段名称
    fieldname = get(target, 'DisplayName');
    
    % 通过索引获取正确的 X 和 Y 数据
    x_data = get(target, 'XData');
    y_data = get(target, 'YData');
    
    % 检查 X 数据是否为 datetime 类型
    if isdatetime(x_data)
        x_value = datestr(x_data(idx));  % 获取并格式化当前数据点的 X 值
    else
        x_value = num2str(x_data(idx));  % 对于数值类型，直接获取 X 值
    end
    
    % 获取 Y 值
    y_value = num2str(y_data(idx));
    
    % 自定义显示的提示信息，包括字段名和正确格式的 X, Y 值
    txt = {['X: ', x_value], ...
           ['Y: ', y_value], ...
           ['Field: ', fieldname]};
end
