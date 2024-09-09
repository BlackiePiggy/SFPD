# SFPD - Seasonal Flex Power Detector

## 0 工程结构说明
```
SFPDpy
├── dataprocessing                  # 用于根据原始数据生成用于SFPD检测的数据集
│   ├── lib                         # 调用的库
│   ├── main.py                     # 数据处理主函数
│   ├── elFilter.py                 # 高度截止角滤波
│   ├── combine_cn_el.py            # 合并载噪比和高度角
│   ├── generate_SFPD_dataset.py    # 生成SFPD数据集
│   ├── read_CN_from_obs.py         # 从原始观测数据中提取载噪比
│   ├── read_CN_from_sp3.py         # 从导航电文中提取高度角
│   └── utils.py                    # 工具函数
├── matlab                          # 用于绘制图像，可视化展示结果
│   ├── plot_date.m                 # 
│   ├── plot_year.m                 # 
│   ├── check_two_day_data.m        # 比较两天的数据特征
│   ├── event_2020_list.mat         # 2020年的先验事件
│   └── event_2021_list.mat         # 2021年的先验事件
├── main.py                         # SFPD主函数
├── sfpd.py                         # SFPD算法函数
├── README.md                       # 说明文档
└── requirements.txt                # 依赖库
```


## 1 dataprocessing
dataprocessing中放置有数据处理函数，可以从obs原始观测和导航电文中获取需要的载噪比数据。

### 1.1 使用流程
1. 主函数为main.py， 打开主函数。
2. 参数配置区域修改对应的信息，包括：
    
    - SS_variables， 载噪比信号名称，如：['S2W']；
    - station_llh，测站的经纬高坐标，如AIRI站的话就应该填写：[42.854, 74.533, 749.2]；
    - station_name，测站名称，如'BIK0'；
    - el_mask，高度截止角，整数数字，低于这个截止角度的载噪比信号不会被提取，如20；
    - base_data_path，数据存放路径，数据文件夹具体格式在后面进行展示，如'F:\\data'；

3. 运行主函数，`python main.py`。结果被保存到base_data_path的各个文件夹中，每个文件夹有数字标号，最终得到的数据被存储到了4_filtered_time_CN文件夹中；
4. 使用generate_SFPD_dataset.py对数据集进行生成，这个程序需要同样对一些信息进行配置；
5. 得到以年为单位，每颗卫星、不同信号的载噪比数据（高度截止角以上的），存储在base_data_path\dataset路径中；

### 1.2 可能存在的问题
这里使用了gnsspy库，其github页面为：（待补充）。其中对于如接收机型号更改，或者其他特别信息的处理不完善，我对此进行了修改；

另外，在使用gnsspy库时，可能会存在包含lib到运行环境中，这个问题的解决方法是：（待补充）

## 2 - SFPD检测算法
对处理好的dataset进行SFPD算法检测，检测结果主要以每日一个值的DTW_result.csv表格和每天一张的image为输出；

./main.py为主函数, sfpd.py为算法函数。

### 2.1 使用流程
1. 配置main.py中的参数；
2. 运行main.py，`python main.py`；
3. 得到每日的DTW_result.csv和image文件，存储在自定义路径中。

### 2.2 配置项
- years = ['2020','2021','2022']
- stations = ['AIRA', 'BAIE', 'BIK0', 'CAS1']
- signals = ['S2W']
- residual_threshold = 5 
- save_plots = True  # 控制是否保存每日图像的布尔变量
- input_data_path = 'F:/data/dataset'  # 输入CSV文件所在目录
- output_image_dir_base = 'F:/data/result/ver2/images'  # 图像输出基础路径 
- output_DTW_dir_base = 'F:/data/result/ver2/DTW_results'  # DTW输出路径

### 2.3 其他

## 3 Matlab可视化展示
1. plot_date.m 用于绘制每日的图像；
2. check_two_day_data.m 用于比较两天的数据特征；
## 4 其他说明
### 4.1 数据存储格式
原始数据的存储文件夹结构应该如下所示：

假设base_data_path为数据存放根目录，那么base_data_path下的文件结构应该如下所示：
```
base_data_path
├── obs
│   ├── 测站名1
│   │   ├── 年份1
│   │   │   ├── AIRA00JPN_R_20200010000_01D_30S_MO.cro
│   │   │   ├── ...
│   │   ├── ...
│   └── ...
└── sp3
    ├── 年份1
    │   ├── COD0MGXFIN_20180010000_01D_05M_ORB.SP3
    │   ├── ...
    ├── ...
```

### 4.2 速度测试