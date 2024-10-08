close all; clc; clear all;

% 定义两个时间序列
ts1 = [1,7,4,8,2,9,6,5,2,0];
ts2 = [1,2,8,5,5,1,9,4,6,5];

% 获取时间序列的长度
m = length(ts1);
n = length(ts2);

% 初始化距离矩阵
D = zeros(m, n);

% 计算欧氏距离矩阵
for i = 1:m
    for j = 1:n
        D(i,j) = (ts1(i) - ts2(j))^2;
    end
end

% 累积距离矩阵的初始化
C = zeros(m, n);
C(1, 1) = D(1, 1);

% 计算累积距离矩阵
for i = 2:m
    C(i, 1) = D(i, 1) + C(i-1, 1);
end

for j = 2:n
    C(1, j) = D(1, j) + C(1, j-1);
end

for i = 2:m
    for j = 2:n
        C(i, j) = D(i, j) + min([C(i-1, j), C(i, j-1), C(i-1, j-1)]);
    end
end

% 回溯最优路径
ix = m;
iy = n;
path_ix = [m];
path_iy = [n];

while ix > 1 || iy > 1
    if ix == 1
        iy = iy - 1;
    elseif iy == 1
        ix = ix - 1;
    else
        [~, idx] = min([C(ix-1, iy), C(ix, iy-1), C(ix-1, iy-1)]);
        if idx == 1
            ix = ix - 1;
        elseif idx == 2
            iy = iy - 1;
        else
            ix = ix - 1;
            iy = iy - 1;
        end
    end
    path_ix = [ix, path_ix];
    path_iy = [iy, path_iy];
end

% 绘制m×n的矩阵，并标注每个格点的DTW累积距离
figure;
imagesc(C); % 绘制累积DTW距离矩阵
colorbar;   % 添加颜色条，显示距离的范围
title('DTW Cumulative Distance Matrix with Optimal Path');
xlabel('Time Index of Time Series 2');
ylabel('Time Index of Time Series 1');
axis equal;
hold on;

% 在每个格点标注DTW距离值
for i = 1:m
    for j = 1:n
        text(j, i, sprintf('%d', C(i,j)), 'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle');
    end
end

% 绘制最优路径，并将路径上的点用深色标注
plot(path_iy, path_ix, 'ko-', 'LineWidth', 2, 'MarkerFaceColor', 'k');  % 'k'表示黑色

% 设置格点线条
set(gca, 'XTick', 1:n, 'YTick', 1:m);
grid on;
