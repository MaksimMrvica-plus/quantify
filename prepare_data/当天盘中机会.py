# -*- coding: utf-8 -*-
import datetime
import time

import pandas as pd

import mypack.stock_tools as stl
import mypack.st_time as stt
from mypack.ts_tools import pro
import mypack.ts_tools as tstl
import akshare as ak
import tushare as ts
import os
import json

# 序号,代码,名称,最新价,涨跌幅,涨跌额,成交量,成交额,振幅,最高,最低,今开,昨收,量比,换手率,
# 市盈率-动态,市净率,总市值,流通市值,涨速,5分钟涨跌,60日涨跌幅,年初至今涨跌幅
now_df = ak.stock_zh_a_spot_em()
now_df.to_csv("now_df_em.csv", index=False)
now_df = ak.stock_zh_a_spot()  # 代码,名称,最新价,涨跌额,涨跌幅,成交量,成交额,     最高,最低,今开,昨收,卖出,买入,,时间戳
now_df.to_csv("now_df.csv", index=False)


# 1. 量能位于昨天的50-80%




