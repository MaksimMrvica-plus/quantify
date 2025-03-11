import tushare as ts
import datetime
import time

import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import os
import logging

import st_time
from define import *


if __name__ == '__main__':
    pro = ts.pro_api('c481515077951633f62f40f93473cee19825a2dc91cf7343b4b37a29')
    # pd = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    # pd = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,market,exchange,list_status')
    df = pro.query("daily", ts_code='000001.SZ', start_date='20250211', end_date='20250311')
    print(df)
    df.to_excel("tmp.xlsx", index=False)
    df = pro.query("daily", trade_date='20250311')
    df.to_excel("tmp2.xlsx", index=False)