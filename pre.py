import numpy as np
import pandas as pd
from datetime import timedelta
import seaborn as sns
import matplotlib.pylab as plt
# %matplotlib inline

from functools import reduce

# 支持中文
# plt.rcParams['font.sans-serif'] = ['Arial Unicode MS'] # 用来正常显示中文标签
# plt.rcParams['axes.unicode_minus'] = False # 用来正常显示负号
plt.rcParams['font.sans-serif'] = ['SimHei'] #设置画图的中文字体显示
plt.rcParams['axes.unicode_minus'] = False   #显示负号
plt.rcParams['font.size'] = 12

#隐藏红色警示框
import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')

seed = 123


## 去精度
def degree(df, freq):
    df.loc[:, '时间'] = df.loc[:, '时间'].dt.round(freq)

#磨机浓度：
def concentration(df):
    Dry_weight = (df['给料皮带G1_矿量反馈'] + df['返料皮带F3_矿量']) * (1-0.009) + (df['给料皮带G1_矿量反馈'] * 0.001 * 0.61)
    Total_weight = df['给料皮带G1_矿量反馈'] + df['返料皮带F3_矿量'] + df['半自磨_给矿水流量反馈'] + (df['给料皮带G1_矿量反馈'] * 0.001 * 0.61)
    con = ((Dry_weight / Total_weight)) * 100
    df['半自磨浓度%'] = pd.DataFrame(con)

#cdf
minpoint_lst = []
maxpoint_lst = []

def cdf(df):
    # minpoint_lst = []
    # maxpoint_lst = []
    denominator = len(df)

    for cols in df.columns:
        Data = pd.Series(df[cols])
        Fre = Data.value_counts()
        Fre_sort = Fre.sort_index(axis=0, ascending=True)
        Fre_df = Fre_sort.reset_index()
        Fre_df.columns = ['nums', 'fre']
        Fre_df['fre'] = Fre_df['fre'] / denominator
        Fre_df['cumsum'] = np.cumsum(Fre_df['fre'])

        # 创建画布
        plot = plt.figure()
        # 只有一张图，也可以多张
        ax1 = plot.add_subplot(1, 1, 1)
        # 按照Rds列为横坐标，累计概率分布为纵坐标作图
        ax1.plot(Fre_df['nums'], Fre_df['cumsum'])
        # 图的标题
        ax1.set_title('CDF-{}'.format(cols))
        # 横轴名
        ax1.set_xlabel('{}'.format(cols))
        # 纵轴名
        ax1.set_ylabel('Cumulative percentage')
        # 横轴的界限
        # ax1.set_xlim(0.1,0.5)
        # 图片显示
        plt.show()

        max_df = Fre_df.loc[Fre_df['cumsum'] < 0.995]
        maxpoint = max_df['nums'].max()
        maxpoint = round(maxpoint, 2)

        min_df = Fre_df.loc[Fre_df['cumsum'] > 0.005]
        minpoint = min_df['nums'].min()
        minpoint = round(minpoint, 2)

        print('{}累计分布0.5%下界为{}，99.5%上界为{}'.format(cols, minpoint, maxpoint))
        print("\n" * 2)
        minpoint_lst.append(minpoint)
        maxpoint_lst.append(maxpoint)
        # return minpoint_lst, maxpoint_lst


# 前后范围

def outilers(df, lower, higher) :
    lower = lower[:18]
    higher = higher[:18]
    features = ['给料皮带G1_矿量反馈', '返料皮带F3_电流', '返料皮带F3_矿量', '半自磨_功率1', '半自磨_功率2',
       '半自磨_进料端总高压', '半自磨_出料端总高压', '半自磨_给矿水流量反馈', '半自磨_给矿水阀位', '半自磨_排矿水流量',
       '直线筛_冲筛水流量', '一段泵池_液位', '一段泵池_补加水流量反馈', '一段渣浆泵1_电流', '一段渣浆泵1_矿浆流量反馈',
       '一段旋流器1_压力', '球磨机_功率1', '球磨机_功率2']
    for i in range(len(df.iloc[:,1:19].columns)) :
        df = df[(df[features[i]] > lower[i]) & (df[features[i]] < higher[i])]
        i += 1
    return df



# def combine(df, huayan, new, shift, freq):
#     df0 = df[['时间','给料皮带G1_矿量反馈']]
#     df1 = df[['时间','返料皮带F3_电流', '返料皮带F3_矿量']]
#     df2 = df[['时间','半自磨_功率1', '半自磨_功率2','半自磨_进料端总高压', '半自磨_出料端总高压', '半自磨_给矿水流量反馈',
#                            '半自磨_给矿水阀位','半自磨_排矿水流量', '直线筛_冲筛水流量']]
#     df3 = df[['时间','一段泵池_液位', '一段泵池_补加水流量反馈']]
#     df4 = df[['时间','一段渣浆泵1_电流', '一段渣浆泵1_矿浆流量反馈']]
#
#     df5 = df[['时间','一段旋流器1_压力']]
#     df6 = df[['时间','球磨机_功率1','球磨机_功率2', '球磨机_进料端总高压', '球磨机_出料端总高压', '球磨机_排矿水流量', '球磨机_排矿水阀位']]
#
#     df_set = [df0, df1, df2, df3, df4, df5, df6]
#     # shift = [10, 20, 10, 5, 5, 5, 1]
#     # freq = ['5min', '5min', '5min', '5min', '5min', '5min', '1min']
#     for i in range(7):
#         lll = len(df_set[i].columns)
#         df_set[i].loc[:, '时间'] = df_set[i].loc[:, '时间'] - timedelta(minutes=shift[i])
#         df_set[i].loc[:, '时间'] = df_set[i].loc[:, '时间'].dt.round(freq[i])
#         df_set[i] = df_set[i].groupby("时间").mean().reset_index()
#         df_set[i] = df_set[i].merge(huayan, how="left", on="时间").dropna(axis=0, how='any')
#
#         df_set[i] = df_set[i].iloc[:, :lll]
#         df_set[i].reset_index(inplace=True, drop=True)
#
#         df_list = [df_set[0], df_set[1], df_set[2], df_set[3], df_set[4], df_set[5], df_set[6], huayan]
#         aaa = reduce(lambda left, right: pd.merge(left, right, on=['时间']), df_list)

def Normal(df):
    '''
    （1）Skewness = 0 ，分布形态与正态分布偏度相同。
    （2）Skewness > 0 ，正偏差数值较大，为正偏或右偏。长尾巴拖在右边，数据右端有较多的极端值。
    （3）Skewness < 0 ，负偏差数值较大，为负偏或左偏。长尾巴拖在左边，数据左端有较多的极端值。


    （1）Kurtosis=0 与正态分布的陡缓程度相同。
    （2）Kurtosis>0 比正态分布的高峰更加陡峭——尖顶峰
    （3）Kurtosis<0 比正态分布的高峰来得平台——平顶峰
    '''
    for i in df.columns:
        skew = df[i].skew().round(3)
        kurt = df[i].kurt().round(3)
        print('{}---偏度为{};峰度为{}'.format(i,skew,kurt))






