import tushare as ts
from datetime import datetime, timedelta

import time

import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import os
import json
import logging

import mypack.ts_tools as tstl
import mypack.stock_tools as stl
import mypack.st_time as st_time
import mypack.general_tools as gtl
from mypack.define import *

pro = tstl.authorize()

STRATEGY_NAME = os.path.basename(__file__).split('.')[0]
DATESTR = st_time.datetime_to_str_day(datetime.now())
SAVE_ROOT_PATH = f"{os.getcwd()}/../{STRATEGY_NAME}/{DATESTR}"
LOG_PATH = SAVE_ROOT_PATH + '/' + 'debug.log'

# logger
gtl.init_logger(SAVE_ROOT_PATH, LOG_PATH)

if __name__ == '__main__':

    # init_used_codes()
    dc = json.loads(open(os.path.join(stl.ROOT_PATH, f"global_data/ts_codes.json"), 'r').read())
    # c = count_limit_up_times('600728.SH', '20250306', '20250307')
    # print(c)
    todaystr = st_time.datetime_to_str_day(datetime.now())
    yestr = st_time.datetime_to_str_day(datetime.now() - timedelta(days=1))
    lmtup = tstl.get_df_oneday_amplitude(yestr, 9.8, "more")
    allmtup = tstl.get_df_oneday_amplitude(todaystr, 66, "less")
    joinset = allmtup[allmtup['ts_code'].isin(lmtup['ts_code'])]
    joinset = joinset[joinset['ts_code'].isin(dc.keys())]
    logging.info("包含版")
    for low, name in zip([-5, -3, 0, 5, 9.85], ["f5", "f3", "0", "z5", "z985"]):
        nlmtup = joinset[joinset['pct_chg'] < low]
        pth = os.path.join(SAVE_ROOT_PATH, f"filter_low_{name}.xlsx")
        nlmtup.to_excel(pth, index=False)
        logging.info(f"filter_low == [{low}] up:{len(lmtup)}, res:{len(nlmtup)}\tsave to : {pth}")
    logging.info("独立版")
    for rage, name in zip([[-66, -5], [-5, -3], [-3, 0], [0, 5], [5, 66]],
                          ["[-10~-5]", "[-5~-3]", "[-3~0]", "[0~5]", "[5~10]"]):
        low,high = rage[0], rage[1]
        nlmtup = joinset[(joinset['pct_chg'] > low) & (joinset['pct_chg'] < high)]
        pth = os.path.join(SAVE_ROOT_PATH, f"filter_low_{name}.xlsx")
        nlmtup.to_excel(pth, index=False)
        logging.info(f"filter_low == [{low}] up:{len(lmtup)}, res:{len(nlmtup)}\tsave to : {pth}")
