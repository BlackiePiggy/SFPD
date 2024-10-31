import matplotlib.pyplot as plt
from fastdtw import fastdtw
import numpy as np


def align_time_series_with_dtw(sequence1, sequence2, plot=True):
    """
    对两段时间序列数据进行DTW对齐，并返回对齐后的序列及DTW距离

    参数:
    sequence1 (array-like): 第一段时间序列数据
    sequence2 (array-like): 第二段时间序列数据
    plot (bool): 是否绘制对齐前后的数据图像，默认开启

    返回:
    aligned_seq1 (ndarray): 对齐后的第一段时间序列
    aligned_seq2 (ndarray): 对齐后的第二段时间序列
    dtw_distance (float): DTW计算出的距离值
    """

    # 确保两段序列长度一致，截取较长的一段
    len1, len2 = len(sequence1), len(sequence2)
    min_length = min(len1, len2)

    if len1 > min_length:
        print(f"Sequence 1 was truncated by {len1 - min_length} data points.")
        sequence1 = sequence1[:min_length]
    elif len2 > min_length:
        print(f"Sequence 2 was truncated by {len2 - min_length} data points.")
        sequence2 = sequence2[:min_length]

    # 定义距离函数
    def scalar_euclidean(u, v):
        return abs(u - v)

    # 使用fastdtw计算DTW距离和路径
    dtw_distance, path = fastdtw(sequence1, sequence2, dist=scalar_euclidean)

    # 根据路径对序列进行对齐
    aligned_seq1 = []
    aligned_seq2 = []

    for index1, index2 in path:
        aligned_seq1.append(sequence1[index1])
        aligned_seq2.append(sequence2[index2])

    aligned_seq1 = np.array(aligned_seq1)
    aligned_seq2 = np.array(aligned_seq2)

    # 计算原始序列和对齐序列的差异
    diff_original = sequence1 - sequence2
    diff_aligned = aligned_seq1 - aligned_seq2

    # 如果开启绘图
    if plot:
        plt.figure(figsize=(12, 8))

        # 绘制原始数据
        plt.subplot(3, 1, 1)
        plt.plot(sequence1, label='Original Sequence 1')
        plt.plot(sequence2, label='Original Sequence 2')
        plt.legend()
        plt.title('Original Data')

        # 绘制对齐后的数据
        plt.subplot(3, 1, 2)
        plt.plot(aligned_seq1, label='Aligned Sequence 1')
        plt.plot(aligned_seq2, label='Aligned Sequence 2')
        plt.legend()
        plt.title('Aligned Data')

        # 绘制对齐前后数据的差异
        plt.subplot(3, 1, 3)
        plt.plot(diff_original, label='Original Difference')
        plt.plot(diff_aligned, label='DTW Difference')
        plt.legend()
        plt.title('Difference Comparison')

        plt.tight_layout()
        plt.show()

    return aligned_seq1, aligned_seq2, dtw_distance
