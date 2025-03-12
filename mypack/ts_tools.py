# -*- coding: utf-8 -*-
import concurrent.futures
import datetime
import threading
import time
import os
import json

import pandas as pd
import tushare as ts

import pandas.core.frame
import mplfinance as mpf

from st_time import *
from define import *

FILE_PATH = os.path.dirname(__file__)  # "...../quantify/mypack"
ROOT_PATH = os.path.join(FILE_PATH, '..')  # "...../quantify"
DATA_PATH = 'stock_data'
HISTORY_DATA_PATH = 'history_data'
A_STOCK_CODE_NAME_DICT_PATH = 'A_stock_code_name.json'


def authorize():
    return ts.pro_api('c481515077951633f62f40f93473cee19825a2dc91cf7343b4b37a29')


pro = authorize()  # global


def init_used_codes():
    datestr = datetime_to_str_day(now_datetime())
    df = pro.query("daily", trade_date=datestr)
    codes = df['ts_code'].tolist()
    dc = {}
    for code in codes:
        number = code[:6]
        loc = code[-2:]
        if number.startswith('60') or number.startswith('00'):
            dc[code] = [number, loc]
    string = json.dumps(dc, ensure_ascii=False)
    n = len(dc)
    print(f"main number: [{n}]")
    open(os.path.join(ROOT_PATH, f"global_data/ts_codes.json"), 'w').write(string)


# 包含边界 [begin, end]
def count_limit_up_times(_code, _begin='20250101', _end='20250201'):
    df = pro.query("daily", ts_code=_code, start_date=_begin, end_date=_end)
    cnt = len(df[df['pct_chg'] > 9.8])
    return cnt


def count_limit_up_times_pre30(_code) -> int:
    now_date = now_datetime()
    _end = datetime_to_str_day(now_date)
    pre_date = now_date - timedelta(days=30)
    _begin = datetime_to_str_day(pre_date)
    df = pro.query("daily", ts_code=_code, start_date=_begin, end_date=_end)
    cnt = len(df[df['pct_chg'] > 9.8])
    return cnt


def get_df_oneday_amplitude(_date="20250312", _ampl: float = 5.0, _type="more") -> pd.DataFrame:
    df = pro.query("daily", trade_date=_date)
    if _type == "more":
        df = df[df['pct_chg'] >= _ampl]
    elif _type == "less":
        df = df[df['pct_chg'] <= -_ampl]
    return df


if __name__ == '__main__':
    # init_used_codes()
    dc = json.loads(open(os.path.join(ROOT_PATH, f"global_data/ts_codes.json"), 'r').read())
    # c = count_limit_up_times('600728.SH', '20250306', '20250307')
    # print(c)
    lmtup = get_df_oneday_amplitude("20250311", 9.8, "more")
    nlmtup = get_df_oneday_amplitude("20250312", 0, "less")
    print(f"up:{len(lmtup)}, down:{len(nlmtup)}")
    res = nlmtup[nlmtup['ts_code'].isin(lmtup['ts_code'])]
    res = res[res['ts_code'].isin(dc.keys())]
    print(f"res:{len(res)}")
    res.to_excel('tmp.xlsx', index=False)

    nlmtup = get_df_oneday_amplitude("20250312", 5, "less")
    print(f"up:{len(lmtup)}, down:{len(nlmtup)}")
    res = nlmtup[nlmtup['ts_code'].isin(lmtup['ts_code'])]
    res = res[res['ts_code'].isin(dc.keys())]
    print(f"res:{len(res)}")
    res.to_excel('tmp2.xlsx', index=False)


    pass
