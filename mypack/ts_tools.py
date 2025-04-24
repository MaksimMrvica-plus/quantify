# -*- coding: utf-8 -*-
import concurrent.futures
import datetime
import logging
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

ts.set_token('c481515077951633f62f40f93473cee19825a2dc91cf7343b4b37a29')

FILE_PATH = os.path.dirname(__file__)  # "...../quantify/mypack"
ROOT_PATH = os.path.join(FILE_PATH, '..')  # "...../quantify"
DATA_PATH = 'stock_data'
HISTORY_DATA_PATH = 'history_data'
A_STOCK_CODE_NAME_DICT_PATH = 'A_stock_code_name.json'


def authorize():
    return ts.pro_api('c481515077951633f62f40f93473cee19825a2dc91cf7343b4b37a29')


pro = authorize()  # global


# 转换成ts格式code
def format_code(_code: str):
    if len(_code) == 9:
        return _code
    if len(_code) == 6:
        if _code.startswith('6'):
            return f"{_code}.SH"
        elif _code.startswith('0'):
            return f"{_code}.SZ"
    print("格式错误，转换失败")
    return _code


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
        df = df[df['pct_chg'] <= _ampl]
    return df


def get_stocks_limit_up_oneday(_date="20250312") -> pd.DataFrame:
    df = pro.query("daily", trade_date=_date)
    df = df[df['pct_chg'] > 9.8]
    return df


def pre_n_days_trade_date(n: int = 5) -> list:
    """
    # 返回截至今天，前n个交易日的日期（包括今天），结果从前往后的日期，是从近到远的顺序, 如果今天是交易日，则第一个会是今天。
    :param n:
    :return:
    """
    now_date = now_datetime()
    _end = datetime_to_str_day(now_date)
    pre_date = now_date - timedelta(days=max(n * 2, 15))  # 防止假期，结果数量不足
    _begin = datetime_to_str_day(pre_date)
    _code = "600000.sh"
    df = pro.query("daily", ts_code=_code, start_date=_begin, end_date=_end)
    # print(df)
    _res = df['trade_date'].tolist()
    return _res[:n]


def get_oneday_stock_infos(_code: list, _date):
    """
    _code 是一个列表，eg: ['603173.sh', '605208.sh', '603665.sh'] 或 ['603173', '605208', '603665']
    _date 是当天日期, eg: "20250101"
    """
    _code = [format_code(_code_str) for _code_str in _code]
    _code_str = ','.join(_code)
    logging.info(f"当前查询日期：f{_date}, 共查询{len(_code)}个: {_code_str}")
    _df = pro.query("daily", ts_code=_code_str, trade_date=_date)
    return _df
