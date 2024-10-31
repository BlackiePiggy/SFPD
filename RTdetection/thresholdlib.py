import numpy as np
import pandas as pd
from enum import Enum


from enum import Enum
import numpy as np
import pandas as pd

class ThresholdMethod(Enum):
    STATIC = "static"
    ROLLING = "rolling"
    STATISTICAL = "statistical"
    ADAPTIVE = "adaptive"
    EWMA = "ewma"  # 新增的EWMA方法


class ThresholdCalculator:
    def __init__(self, method=ThresholdMethod.STATIC, params=None):
        """
        初始化阈值计算器

        参数:
        method: ThresholdMethod 枚举值，指定使用的阈值方法
        params: 字典，包含特定方法所需的参数
        """
        self.method = method
        self.params = params or {}

    def calculate_threshold(self, sequence_prev, sequence_curr, diff=None):
        """
        根据选定的方法计算阈值

        参数:
        sequence_prev: 前一天的序列数据
        sequence_curr: 当前天的序列数据
        diff: 可选，已计算的差分序列

        返回:
        float or numpy.ndarray: 计算得到的阈值
        """
        if diff is None:
            diff = sequence_curr - sequence_prev

        if self.method == ThresholdMethod.STATIC:
            return self._static_threshold()
        elif self.method == ThresholdMethod.ROLLING:
            return self._rolling_threshold(diff)
        elif self.method == ThresholdMethod.STATISTICAL:
            return self._statistical_threshold(diff)
        elif self.method == ThresholdMethod.ADAPTIVE:
            return self._adaptive_threshold(diff, sequence_curr)
        elif self.method == ThresholdMethod.EWMA:
            return self._ewma_threshold(diff)  # 新增的EWMA方法调用

    def _static_threshold(self):
        """静态阈值方法"""
        return self.params.get('threshold', 4.5)

    def _rolling_threshold(self, diff):
        """
        基于滑动窗口的动态阈值
        使用局部数据的标准差来调整阈值
        """
        window_size = self.params.get('window_size', 20)
        base_threshold = self.params.get('base_threshold', 3.0)

        rolling_std = pd.Series(diff).rolling(
            window=window_size,
            min_periods=1
        ).std().fillna(0)

        multiplier = self.params.get('std_multiplier', 2.0)
        return base_threshold + (rolling_std * multiplier)

    def _statistical_threshold(self, diff):
        """
        基于统计分布的阈值
        使用中位数绝对偏差(MAD)方法
        """
        median = np.median(diff)
        mad = np.median(np.abs(diff - median))

        k = self.params.get('mad_multiplier', 1.4826)
        threshold_multiplier = self.params.get('threshold_multiplier', 3.0)

        return threshold_multiplier * k * mad

    def _adaptive_threshold(self, diff, sequence_curr):
        """
        自适应阈值
        根据信号强度动态调整阈值
        """
        base_threshold = self.params.get('base_threshold', 3.0)
        signal_weight = self.params.get('signal_weight', 0.3)

        signal_strength = np.abs(sequence_curr).mean()
        return base_threshold * (1 + signal_weight * (signal_strength / 100))

    def _ewma_threshold(self, diff):
        """
        指数加权移动平均（EWMA）阈值
        使用指数加权平滑来计算每个时间点的动态阈值序列
        """
        alpha = self.params.get('alpha', 0.3)  # 平滑系数
        base_threshold = self.params.get('base_threshold', 3.0)
        threshold_multiplier = self.params.get('ewma_multiplier', 1.5)

        # 计算每个时间点的EWMA值序列
        ewma_series = pd.Series(diff).ewm(alpha=alpha, adjust=False).mean()

        # 计算每个时间点的动态阈值
        dynamic_thresholds = base_threshold + ewma_series * threshold_multiplier

        # 返回包含每个时间点阈值的数组
        return dynamic_thresholds.values



def check_threshold_violation(diff, threshold):
    """
    检查是否超过阈值

    参数:
    diff: float or numpy.ndarray, 差值
    threshold: float or numpy.ndarray, 阈值

    返回:
    bool: 是否超过阈值
    """
    return abs(diff) > threshold