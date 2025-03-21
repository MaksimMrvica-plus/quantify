# -*- coding utf-8 -*-

"""
需要当天结束后运行
多步筛选
   - **昨停今未**：读取昨天涨停但今天未涨停的股票列表。
   - **涨停**：筛选在过去一个月内有涨停记录的股票。
   - **股价低于35元**：进一步筛选出当天收盘价低于35元的股票。
   - **市值低于300亿**：筛选出市值低于300亿的股票。
   - **涨跌幅在0-7.5%之间**：筛选出当天涨跌幅在0到7.5%之间的股票。
   - **当前价>开盘价>昨日收盘价**：筛选出当前价格大于开盘价且开盘价大于昨日收盘价的股票。
   - **量比大于1.5**：筛选出量比大于1.5的股票。

"""

import datetime
import time
import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import os
import logging

from mypack.define import *
import st_time
import mypack.stock_tools as stl

STRATEGY_NAME = os.path.basename(__file__).split('.')[0]
DATESTR = st_time.datetime_to_str_day(datetime.datetime.now())

SAVE_ROOT_PATH = f"{os.getcwd()}/../{STRATEGY_NAME}/{DATESTR}"
LOG_PATH = SAVE_ROOT_PATH + '/' + 'debug.log'

# 创建保存数据目录
stl.ensure_dir_exists(SAVE_ROOT_PATH)
# 配置日志记录器
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为 INFO << DEBUG : INFO : WARNING : ERROR : CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s',  # 设置日志格式
    filename=LOG_PATH,  # 将日志输出到文件
    filemode='w'  # 每次运行时覆盖日志文件
)
# 添加控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(console_handler)

# 示例调用
if __name__ == "__main__":
    logging.info(f"当前策略: {STRATEGY_NAME}, 日志保存路径: {LOG_PATH}")

    # # 1 昨停今不
    tdstr = st_time.datetime_to_str_day(datetime.datetime.now())
    yestr = st_time.datetime_to_str_day(datetime.datetime.now() - datetime.timedelta(days=1))
    yest_lmtup_today_no = stl.get_yest_limit_today_no(yestr, tdstr)
    print(yest_lmtup_today_no)
    yest_lmtup_today_no.to_excel(os.path.join(SAVE_ROOT_PATH, "yest_lmtup_today_no.xlsx"), index=False)
    # 2 读取已有
    yest_lmtup_today_no = pd.read_excel(os.path.join(SAVE_ROOT_PATH, "yest_lmtup_today_no.xlsx"), dtype={GPDM: str})
    logging.info(f"昨停今未:  {len(yest_lmtup_today_no)}")
    print(yest_lmtup_today_no)

    # # 3 筛选出main_board_stocks中代码，与 yest_lmtup_today_no代码共有的 内容
    main_board_stocks = stl.get_a_share_main_board()
    main_yltn_stocks = main_board_stocks[main_board_stocks[DM].isin(yest_lmtup_today_no[GPDM])]
    logging.info(f"main_yltn_stocks:  {len(main_yltn_stocks)}")
    main_yltn_stocks.to_excel(os.path.join(SAVE_ROOT_PATH, "main_yltn_stocks.xlsx"), index=False)
    # 3 股价低于35
    yltn = pd.read_excel(os.path.join(SAVE_ROOT_PATH, "main_yltn_stocks.xlsx"), dtype={"代码": str})
    price = 35
    low_price = stl.today_price_less_x(yltn, price)
    logging.info(f"当天值低于 {price}:  {len(low_price)}")
    low_price.to_excel(os.path.join(SAVE_ROOT_PATH, "low_price.xlsx"), index=False)
    # 4 市值低于300亿
    low_price = pd.read_excel(os.path.join(SAVE_ROOT_PATH, "low_price.xlsx"), dtype={"代码": str})
    low_market_value = stl.filter_market_value(low_price, max_market_value=300)
    logging.info(f"市值低于300亿:  {len(low_market_value)}")
    low_market_value.to_excel(os.path.join(SAVE_ROOT_PATH, "low_market_value.xlsx"))
    # 5 涨跌幅  0-7.5
    low_market_value = pd.read_excel(os.path.join(SAVE_ROOT_PATH, "low_market_value.xlsx"), dtype={"代码": str})
    amplow = 0
    amphigh = 7.5
    low_amplitude = stl.today_amplitude_range(low_market_value, amplow, amphigh)
    logging.info(f"当天浮动{amplow} ~ {amphigh}:  {len(low_amplitude)}")
    low_amplitude.to_excel(os.path.join(SAVE_ROOT_PATH, "low_amplitude.xlsx"), index=False)
    # 6 当前>开>收
    low_amplitude = pd.read_excel(os.path.join(SAVE_ROOT_PATH, "low_amplitude.xlsx"), dtype={"代码": str})
    now_open_yest = stl.now7open7yesterday(low_amplitude)
    logging.info(f"当前>开>收:  {len(now_open_yest)}")
    now_open_yest.to_excel(os.path.join(SAVE_ROOT_PATH, "now_open_yest.xlsx"), index=False)
    # 7 liangbi
    now_open_yest = pd.read_excel(os.path.join(SAVE_ROOT_PATH, "now_open_yest.xlsx"), dtype={"代码": str})
    lb_val = 1.5
    liangbi = stl.today_liangbi_more_than_x(now_open_yest, lb_val)
    logging.info(f"量比>{lb_val}:  {len(liangbi)}")
    liangbi.to_excel(os.path.join(SAVE_ROOT_PATH, "liangbi.xlsx"), index=False)
    # # 8 customer
    # liangbi = pd.read_excel(os.path.join(SAVE_ROOT_PATH, "liangbi.xlsx"), dtype={"代码": str})

"""
当天低位:  1095
当天值低于 35:  988
当天浮动1.5 ~ 5:  201
当前>开>收:  102
量比>1.5:  16

当天低位:  724
当天值低于 35:  656
当天浮动1.5 ~ 5:  136
当前>开>收:  71
量比>1.5:  10
"""
