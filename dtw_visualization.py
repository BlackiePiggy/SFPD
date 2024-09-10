import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import matplotlib.pyplot as plt

# 示例时间序列
s_today = np.array([1, 2, 3, 4, 5, 6, 7])
s_seasonal = np.array([1, 1, 2, 3, 4, 4, 6])

# 确保时间序列为1D
s_today = s_today.reshape(-1, 1)
s_seasonal = s_seasonal.reshape(-1, 1)

# 计算DTW距离及配对路径
distance, path = fastdtw(s_today, s_seasonal, dist=euclidean)

# 提取DTW变换后的序列
s_today_dtw = np.array([s_today[i] for i, j in path])
s_seasonal_dtw = np.array([s_seasonal[j] for i, j in path])

# 可视化原始时间序列
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.plot(s_today, label='s_today', marker='o')
plt.plot(s_seasonal, label='s_seasonal', marker='o')
plt.title('Original Time Series Comparison')
plt.legend()

# 可视化经过DTW变换后的时间序列
plt.subplot(1, 2, 2)
plt.plot(s_today_dtw, label='s_today_dtw', marker='o')
plt.plot(s_seasonal_dtw, label='s_seasonal_dtw', marker='o')
for (i, j) in path:
    plt.plot([i, j], [s_today[i], s_seasonal[j]], 'k-', alpha=0.5)  # 连接配对点
plt.title('DTW Transformed Time Series')
plt.legend()

plt.tight_layout()
plt.show()
