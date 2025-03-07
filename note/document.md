# 交易策略

de: 某一天同时涨停的股票可能在之前的某一天也同时涨停

检查当天时刻已经涨停的股票

查看此股票历史数据，找出该股票过去涨停的日期

再检索此日期涨停的其他股票，

查看这些股票今日表现


# 历史数据存储方式

约5000只股票， 一年范围，365天，一天一个excel
5000*365 = 1,825,000








# DataFrame 数据使用

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
pd.options.display.max_rows=n:    # 最多显示n列
df.memory_usage():                # 占用内存(字节B)
