import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from tqdm import tqdm


class SatelliteStatusViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-time Detection Result")

        # 定义卫星分类
        self.satellite_groups = {
            'IIR-M': ['G05', 'G07', 'G12', 'G15', 'G17', 'G29', 'G31'],
            'IIF': ['G01', 'G03', 'G06', 'G08', 'G09', 'G10', 'G24',
                    'G25', 'G26', 'G27', 'G30', 'G32']
        }

        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 创建卫星选择框
        self.satellite_frame = ttk.LabelFrame(self.main_frame, text="Choose Sats", padding="5")
        self.satellite_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        # 设置列宽权重，使右侧有空间
        self.main_frame.columnconfigure(1, weight=1)

        # 卫星选择变量
        self.satellite_vars = {}
        # 组选择变量
        self.group_vars = {}

        # 创建刷新按钮
        self.refresh_button = ttk.Button(self.main_frame, text="Refresh Plot", command=self.update_plot)
        self.refresh_button.grid(row=1, column=0, pady=10)

        # 创建进度条
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.main_frame, variable=self.progress_var, maximum=100)
        self.progress.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)

        # 创建图表区域
        self.fig, self.ax = plt.subplots(figsize=(18, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 加载数据
        self.load_data()

        # 创建卫星选择复选框
        self.create_satellite_checkboxes()

        # 初始化图例标记
        self.legend_added = False

    def load_data(self):
        # 读取CSV文件
        self.data = pd.read_csv('final_satellite_data.csv', parse_dates=[0])
        # 获取所有卫星列
        self.satellite_columns = [col for col in self.data.columns if col.startswith('G')]

    def toggle_group(self, group_name):
        """切换组内所有卫星的选择状态"""
        state = self.group_vars[group_name].get()
        satellites = self.get_group_satellites(group_name)
        for sat in satellites:
            if sat in self.satellite_vars:
                self.satellite_vars[sat].set(state)

    def get_group_satellites(self, group_name):
        """获取组内的卫星列表"""
        if group_name == 'Others':
            # 获取不属于其他组的卫星
            all_grouped_sats = []
            for sats in self.satellite_groups.values():
                all_grouped_sats.extend(sats)
            return [sat for sat in self.satellite_columns if sat not in all_grouped_sats]
        return self.satellite_groups.get(group_name, [])

    def create_satellite_checkboxes(self):
        # 创建全局全选按钮
        global_var = tk.BooleanVar(value=True)
        self.group_vars['All'] = global_var
        ttk.Checkbutton(self.satellite_frame, text="Select All Satellites",
                        variable=global_var,
                        command=lambda: self.toggle_all_satellites(global_var.get())
                        ).grid(row=0, column=0, columnspan=3, pady=5)

        # 为每个组创建区域，横向排列
        for col, group_name in enumerate(['IIR-M', 'IIF', 'Others']):
            # 创建组标签和全选按钮
            group_frame = ttk.LabelFrame(self.satellite_frame, text=group_name)
            group_frame.grid(row=1, column=col, sticky='nsew', padx=5, pady=5)

            # 组全选按钮
            group_var = tk.BooleanVar(value=True)
            self.group_vars[group_name] = group_var
            ttk.Checkbutton(group_frame, text=f"Select All {group_name}",
                            variable=group_var,
                            command=lambda g=group_name: self.toggle_group(g)
                            ).grid(row=0, column=0, columnspan=2)

            # 获取该组的卫星
            satellites = self.get_group_satellites(group_name)

            # 创建卫星复选框，改为按2行排列
            max_rows = 1  # 固定2行
            sats_per_row = len(satellites) // max_rows
            if len(satellites) % max_rows != 0:
                sats_per_row += 1  # 如果有余数，每行多放一个

            for i, sat in enumerate(satellites):
                var = tk.BooleanVar(value=True)
                self.satellite_vars[sat] = var
                row = i % max_rows  # 确保只有2行
                col = i // max_rows  # 列数根据卫星数量自动计算
                ttk.Checkbutton(group_frame, text=sat, variable=var).grid(
                    row=row + 1, column=col, padx=5, pady=2)  # row+1 是因为第0行是全选按钮

    def toggle_all_satellites(self, state):
        """切换所有卫星的选择状态"""
        for group_var in self.group_vars.values():
            group_var.set(state)
        for sat_var in self.satellite_vars.values():
            sat_var.set(state)

    def update_plot(self):
        # 清除当前图表
        self.ax.clear()

        # 获取选中的卫星并按序号排序
        selected_satellites = [sat for sat, var in self.satellite_vars.items() if var.get()]
        selected_satellites.sort(key=lambda x: int(x[1:]))  # 按卫星编号排序

        if not selected_satellites:
            return

        # 设置进度条最大值
        total_steps = len(selected_satellites)

        # 创建颜色映射
        colors = {0: 'green', 1: 'red', np.nan: 'purple'}
        labels = {0: 'FP OFF', 1: 'FP ON', np.nan: 'NO DATA'}

        # 重置图例标记
        self.legend_handles = {status: None for status in colors.keys()}

        # 绘制每个卫星的状态
        for i, sat in enumerate(tqdm(selected_satellites, desc="Plot Satellite Status")):
            # 更新进度条
            self.progress_var.set((i + 1) / total_steps * 100)
            self.root.update_idletasks()

            # 获取卫星数据
            sat_data = self.data[sat]

            # 为不同状态绘制散点
            for status in [0, 1, np.nan]:
                mask = sat_data == status if pd.notna(status) else pd.isna(sat_data)
                if mask.any():
                    scatter = self.ax.scatter(self.data['Timestamp'][mask],
                                              [selected_satellites.index(sat)] * mask.sum(),
                                              c=colors[status],
                                              label=labels[status] if self.legend_handles[status] is None else "",
                                              marker='s', s=50)

                    # 保存第一次出现的每种状态的句柄用于图例
                    if self.legend_handles[status] is None:
                        self.legend_handles[status] = scatter

        # 设置图表属性
        self.ax.set_yticks(range(len(selected_satellites)))
        self.ax.set_yticklabels(selected_satellites)
        self.ax.set_xlabel('Date')
        self.ax.set_ylabel('Satellite Number')

        # 添加图例
        legend_elements = [handle for handle in self.legend_handles.values() if handle is not None]
        legend_labels = [handle.get_label() for handle in legend_elements]
        self.ax.legend(legend_elements, legend_labels,
                       bbox_to_anchor=(1.05, 1), loc='upper left')

        # 调整布局
        plt.tight_layout()

        # 刷新画布
        self.canvas.draw()


def main():
    root = tk.Tk()
    app = SatelliteStatusViewer(root)
    root.mainloop()


if __name__ == "__main__":
    main()