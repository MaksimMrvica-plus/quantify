# -*- coding: utf-8 -*-


import akshare as ak
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pandas.core.frame
from pandas import DataFrame
import mypack.stock_tools as stl


# DataFrame 数据使用
'''
df.info():          # 打印摘要
df.describe():      # 描述性统计信息
df.values:          # 数据 <ndarray>
df.to_numpy()       # 数据 <ndarray> (推荐)
df.shape:           # 形状 (行数, 列数)
df.columns:         # 列标签 <Index>
df.columns.values:  # 列标签 <ndarray>
df.index:           # 行标签 <Index>
df.index.values:    # 行标签 <ndarray>
df.head(n):         # 前n行
df.tail(n):         # 尾n行
pd.options.display.max_columns=n: # 最多显示n列
pd.options.display.max_rows=n:    # 最多显示n行
df.memory_usage():                # 占用内存(字节B)
'''
# # 个股信息
# stock_individual_info_em_df = ak.stock_individual_info_em(symbol="000001")
# print(stock_individual_info_em_df)
#
#
# # 实时报价
# stock_bid_ask_em_df = ak.stock_bid_ask_em(symbol="000001")
# print(stock_bid_ask_em_df)
#
# # 实时行情数据
# #
# # 沪深京 A 股
# stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
# print(stock_zh_a_spot_em_df)
#
# # 沪A
# stock_sh_a_spot_em_df = ak.stock_sh_a_spot_em()
# print(stock_sh_a_spot_em_df)
#
#
# # 深A
# stock_sz_a_spot_em_df = ak.stock_sz_a_spot_em()
# print(stock_sz_a_spot_em_df)
#
#
# # 京A
# stock_bj_a_spot_em_df = ak.stock_bj_a_spot_em()
# print(stock_bj_a_spot_em_df)
#
# # 新股
# stock_new_a_spot_em_df = ak.stock_new_a_spot_em()
# print(stock_new_a_spot_em_df)


# 描述: 雪球-行情中心-个股
# 限量: 单次获取指定 symbol 的最新行情数据

# # SH600000  SZ000001
# stock_individual_spot_xq_df = ak.stock_individual_spot_xq(symbol="SZ000001")
# print(stock_individual_spot_xq_df)
#
#
# 描述: 东方财富-沪深京 A 股日频率数据; 历史数据按日频率更新, 当日收盘价请在收盘后获取
# 限量: 单次返回指定沪深京 A 股上市公司、指定周期和指定日期间的历史行情日频率数据
stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="603050", period="daily",
                                        start_date="20240601", end_date='20240817', adjust="qfq")
print(stock_zh_a_hist_df)
print(type(stock_zh_a_hist_df))
stl.dataframe2excel('a.xlsx', stock_zh_a_hist_df)
res = stl.dataframe2list(stock_zh_a_hist_df)
for x in res:
    print(x[0], x[9])
# # 分时
# #描述: 东方财富网-行情首页-沪深京 A 股-每日分时行情; 该接口只能获取近期的分时数据，注意时间周期的设置
# # 限量: 单次返回指定股票、频率、复权调整和时间区间的分时数据, 其中 1 分钟数据只返回近 5 个交易日数据且不复权
#
#
# """
# symbol	str	symbol='000300'; 股票代码
# start_date	str	start_date="1979-09-01 09:32:00"; 日期时间; 默认返回所有数据
# end_date	str	end_date="2222-01-01 09:32:00"; 日期时间; 默认返回所有数据
# period	str	period='5'; choice of {'1', '5', '15', '30', '60'}; 其中 1 分钟数据返回近 5 个交易日数据且不复权
# adjust	str	adjust=''; choice of {'', 'qfq', 'hfq'}; '': 不复权, 'qfq': 前复权, 'hfq': 后复权, 其中 1 分钟数据返回近 5 个交易日数据且不复权
# """
# # 注意：该接口返回的数据只有最近一个交易日的有开盘价，其他日期开盘价为 0
# stock_zh_a_hist_min_em_df = ak.stock_zh_a_hist_min_em(symbol="000002", start_date="2024-08-16 09:30:00",
#                                                       end_date="2024-08-16 15:00:00", period="1", adjust="qfq")
# print(stock_zh_a_hist_min_em_df)
#
#
# # 盘前数据
# # 描述: 东方财富-股票行情-盘前数据
# # 限量: 单次返回指定 symbol 的最近一个交易日的股票分钟数据, 包含盘前分钟数据
# stock_zh_a_hist_pre_min_em_df = ak.stock_zh_a_hist_pre_min_em(symbol="000001", start_time="09:15:00", end_time="09:26:00")
# print(stock_zh_a_hist_pre_min_em_df)
#
#
#
# # 风险警示
# stock_zh_a_st_em_df = ak.stock_zh_a_st_em()
# print(stock_zh_a_st_em_df)
# # 绘图
# stock_zh_a_st_em_df['最新价'].plot(title='平安银行')
# plt.show()
# print(matplotlib.matplotlib_fname())
