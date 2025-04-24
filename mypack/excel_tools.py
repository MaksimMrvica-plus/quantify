# -*- coding: utf-8 -*-
import concurrent.futures
import datetime
import threading
import time
import os
import pandas as pd
import pandas.core.frame
import mplfinance as mpf

import st_time as stt
import define

FILE_PATH = os.path.dirname(__file__)  # "...../quantify/mypack"
ROOT_PATH = os.path.join(FILE_PATH, '..')  # "...../quantify"
GLOBAL_DATA_PATH = os.path.join(ROOT_PATH, 'global_data')
DATA_PATH = 'stock_data'
HISTORY_DATA_PATH = 'history_data'
A_STOCK_CODE_NAME_DICT_PATH = 'A_stock_code_name.json'

excel_path = r"D:\my_projects\quantify\global_data\stockHistory\002896.xlsx"

df = pd.read_excel(excel_path)
print(df)


# 获取特定日期下stock的数据
def get_stock_date_data(stock_code, date) -> pandas.core.frame.DataFrame:
    path = os.path.join(GLOBAL_DATA_PATH, "stockHistory", f"{stock_code}.xlsx")
    _df = pd.read_excel(path)
    try:
        # 获取指定日期的数据
        date_data = _df[_df['日期'] == date]
        return date_data
    except Exception as e:
        print(f"获取股票 {stock_code} 指定日期 {date} 数据时发生错误: {e}")
        return pd.DataFrame()
