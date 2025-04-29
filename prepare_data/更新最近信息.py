# -*- coding: utf-8 -*-
import datetime
import time

import pandas as pd

import mypack.stock_tools as stl
import mypack.st_time as stt
import akshare as ak
import os
import json

DATA_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "global_data", "day_data"))
print(DATA_ROOT)

main_codes = json.loads(open("main_codes.json", 'r').read())
all_codes = json.loads(open("all_codes.json", 'r').read())
main_codes_list = list(main_codes.keys())
all_codes_list = list(all_codes.keys())

"""
用一个 lasted_date.json 来记录，每个code stock本地已有数据的最新日期，这样可以节约打开excel的时间
但是好像并没有优化什么，因为后面添加新数据，必不可少的还是需要打开原excel文件
"""

# try:
#     lasted_date = json.loads(open("lasted_date.json", 'r').read())
# except:  # 没有就第一次运行并初始化
#     print("lasted_date.json 文件不存在")
#     lasted_date = {}


# 遍历DATA_ROOT 目录下文件
for file in os.listdir(DATA_ROOT):
    if file.endswith(".xlsx"):
        code = file.split(".")[0]

        df = pd.read_excel(os.path.join(DATA_ROOT, file))
        if len(df) == 0:
            print(f"{code} 数据为空")
            continue
        # print(df)
        last_date = df.iloc[-1]["date"]  # 2025-04-25 00:00:00
        last_date_str = str(last_date).split(" ")[0].replace("-", "")  # 提取last_date 中的年月日，到 “yyyymmdd”格式
        begin_date = str(last_date + datetime.timedelta(days=1)).split(" ")[0].replace("-", "")
        end_date = stt.datetime_to_str_day(stt.now_datetime())

        symbol = stl.code2akshare_symbol_name(code)
        next_df = ak.stock_zh_a_daily(symbol=symbol, start_date=begin_date, end_date=end_date, adjust="qfq")
        print(f"NOW: {code} -> {symbol}, 存储日期到：{last_date_str} || 获取更新开始日期：{begin_date}，"
              f"结束日期为：{end_date}，增加记录为：{len(next_df)}条")

        # df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        # next_df['date'] = next_df['date'].dt.strftime('%Y-%m-%d')
        # 合并 df 和 next_df，把 next_df 的数据加到 df 末尾，根据相同列名
        df3 = pd.concat([df, next_df], ignore_index=True)

        # 将日期列转换为只包含日期的字符串格式
        save_path = os.path.join(DATA_ROOT, file)
        ret = stl.dataframe2excel(save_path, df3, idx=False)


    exit()

    # df = ak.stock_zh_a_daily(symbol=symbol, start_date=start_date, end_date=end_date,  adjust="qfq")
