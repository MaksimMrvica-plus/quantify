# -*- coding: utf-8 -*-
import time

import mypack.stock_tools as stl
import mypack.st_time as stt
import akshare as ak
import os
import json

DATA_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "global_data", "day_data"))
print(DATA_ROOT)

main_codes = json.loads(open("main_codes.json", 'r').read())
all_codes = json.loads(open("all_codes.json", 'r').read())

for code, item in main_codes.items():
    # "000001": ["平安银行", "19910403", "sz"]
    name = item[0]
    start_date = item[1]
    location = item[2]
    if os.path.exists(os.path.join(DATA_ROOT, f"{code}.xlsx")):
        print(f"{code} {name} 已存在")
        continue
    end_date = stt.datetime_to_str_day(stt.now_datetime())
    symbol = item[2]+code
    print(f"NOW: {symbol}, {name}, {start_date} - {end_date}", end="")
    df = ak.stock_zh_a_daily(symbol=symbol, start_date=start_date, end_date=end_date,  adjust="qfq")
    df.to_excel(os.path.join(DATA_ROOT,  f"{code}.xlsx"), index=False)
    print(f"  加载完成, 共 {len(df)} 条数据")
    # time.sleep(1)
# df.to_excel("test.xlsx")
# print(df)
