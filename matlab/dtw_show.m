close all; clc; clear all;
% 定义两个时间序列
ts1 = [1,7,4,8,2,9,6,5,2,0];
ts2 = [1,2,8,5,5,1,9,4,6,5];
% ts1 = [1,1,2,2,3,3,4,4,4,4,3,3,2,2,1,1];
% ts2 = [1,1,1,1,2,2,3,3,4,3,2,2,1,1,1,1];

% 绘制两个时间序列
figure;
subplot(2,1,1);
plot(ts1, '-o', 'DisplayName', 'Time Series 1');
title('Time Series 1');
xlabel('Time');
ylabel('Value');
legend;

subplot(2,1,2);
plot(ts2, '-o', 'DisplayName', 'Time Series 2');
title('Time Series 2');
xlabel('Time');
ylabel('Value');
legend;

% 计算DTW
[dist, ix, iy] = dtw(ts1, ts2);

% 计算"添加"的点。对ix和iy求前后差分，如果等于0的，记下对应的索引号
% 计算ix和iy的差分
diff_ix = diff(ix); % ix的差分
diff_iy = diff(iy); % iy的差分

% 找出ix和iy中差分为0的索引（表示重复映射点）
added_ix_indices = find(diff_ix == 0); % ix中添加的点
added_iy_indices = find(diff_iy == 0); % iy中添加的点
added_ix_indices = added_ix_indices + 1;
added_iy_indices = added_iy_indices + 1;

% 显示匹配的点并在附近显示匹配点的差异
figure;
plot(ix, iy, 'o-');
title('DTW Alignment of Time Series 1 and 2');
xlabel('Time Index of Time Series 1');
ylabel('Time Index of Time Series 2');
grid on;

% 计算并展示匹配点的差异
for i = 1:length(ix)
    diff_value = abs(ts1(ix(i)) - ts2(iy(i)));  % 计算每对匹配点的差异
    text(ix(i), iy(i), sprintf('%.2f', diff_value), 'VerticalAlignment', 'bottom', 'HorizontalAlignment', 'right');
end

% 展示匹配的两个时间序列，对added_ix_indices和added_iy_indices对应索引点用红色进行绘制
figure;
subplot(2,1,1);
plot(ts1(ix), '-o', 'DisplayName', 'Aligned Time Series 1');
hold on;
plot(added_ix_indices, ts1(ix(added_ix_indices)), 'ro', 'MarkerFaceColor', 'r', 'DisplayName', 'Added Points'); % 红色标记添加的点，并设置图例说明
title('Aligned Time Series 1');
xlabel('Warped Time');
ylabel('Value');
legend;

subplot(2,1,2);
plot(ts2(iy), '-o', 'DisplayName', 'Aligned Time Series 2');
hold on;
plot(added_iy_indices, ts2(iy(added_iy_indices)), 'ro', 'MarkerFaceColor', 'r', 'DisplayName', 'Added Points'); % 红色标记添加的点，并设置图例说明
title('Aligned Time Series 2');
xlabel('Warped Time');
ylabel('Value');
legend;

% 计算DTW距离矩阵
m = length(ts1);
n = length(ts2);
D = zeros(m, n);

% 初始化第一行和第一列
D(1, 1) = abs(ts1(1) - ts2(1));
for i = 2:m
    D(i, 1) = D(i-1, 1) + abs(ts1(i) - ts2(1));
end
for j = 2:n
    D(1, j) = D(1, j-1) + abs(ts1(1) - ts2(j));
end

% 填充DTW矩阵
for i = 2:m
    for j = 2:n
        cost = abs(ts1(i) - ts2(j));
        D(i, j) = cost + min([D(i-1, j), D(i, j-1), D(i-1, j-1)]);
    end
end

% 创建新图形
figure('Position', [100, 100, 800, 600]);
imagesc(D);
colormap(flipud(winter(256))); % 使用冬季色调的反转版本，从深蓝到浅绿
hold on; % 开启图层叠加模式

% 标注最优路径（绘制在数字下方）
plot(iy, ix, 'r-', 'LineWidth', 1.5); % 使用红色来显示最优路径，稍微减小线宽
scatter(iy, ix, 30, 'r', 'filled'); % 使用红色填充的圆点标记路径上的点，稍微减小点的大小

% 标注每个格点的DTW距离值
textColor = [0.9 0.9 0.9]; % 使用浅灰色作为文本颜色
for i = 1:m
    for j = 1:n
        % 为文本添加黑色边缘以增加可见度
        text(j, i, sprintf('%d', D(i, j)), 'HorizontalAlignment', 'center', ...
            'Color', textColor, 'FontSize', 13, 'FontWeight', 'bold');
    end
end

% 调整图形外观
colorbar;
title('DTW Distance Matrix with Optimal Path', 'FontSize', 14, 'FontWeight', 'bold');
xlabel('Time Series 2');
ylabel('Time Series 1');
axis tight;
set(gca, 'YDir', 'normal');
set(gca, 'FontSize', 10); % 增加轴标签的字体大小

% 设置x轴和y轴的刻度和标签
xticks(1:length(ts2));
yticks(1:length(ts1));
xticklabels(ts2);
yticklabels(ts1);

% 旋转x轴标签以防止重叠
xtickangle(45);

% 调整颜色条的位置和标签
c = colorbar;
c.Label.String = 'DTW Distance';
c.Label.FontSize = 12;

% 添加图例
legend('Optimal Path', 'Location', 'southeast');

hold off; % 关闭图层叠加模式