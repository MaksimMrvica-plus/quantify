# -*- coding: utf-8 -*-
import datetime
import time
import akshare as ak
import os
import json
import logging
import pandas as pd

import mypack.stock_tools as stl
import mypack.st_time as stt
import mypack.general_tools as gtl

LOG_ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "log"))
LOG_PATH = os.path.join(LOG_ROOT_PATH, "update_data.log")
# logger
gtl.init_logger(LOG_ROOT_PATH, LOG_PATH)

DATA_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "global_data", "day_data"))
logging.info(DATA_ROOT)

main_codes = json.loads(open("main_codes.json", 'r').read())
all_codes = json.loads(open("all_codes.json", 'r').read())
main_codes_list = list(main_codes.keys())
all_codes_list = list(all_codes.keys())

"""
- 用一个 lasted_date_bk.json 来记录，每个code stock本地已有数据的最新日期，这样可以节约打开excel的时间
  但是好像并没有优化什么，因为后面添加新数据，必不可少的还是需要打开原excel文件，
- 还是加上了，因为可能更新到一半中断，这样还是可以节省时间。
"""

try:
    lasted_date = json.loads(open("lasted_date_bk.json", 'r').read())
except:  # 没有就第一次运行并初始化
    logging.warning("lasted_date_bk.json 文件不存在")
    lasted_date = {}

end_date = stt.datetime_to_str_day(stt.now_datetime())

maxn = len(os.listdir(DATA_ROOT))
n = 0
# 遍历DATA_ROOT 目录下文件
for file in os.listdir(DATA_ROOT):
    n += 1
    if file.startswith("$"):  # 忽略 $开头的文件
        continue
    if file.endswith(".xlsx"):
        code = file.split(".")[0]
        try:
            if lasted_date[code] == end_date:
                logging.info(f"{code} 数据已是最新, 跳过, 进度: {n}/{maxn}")
                continue
        except:
            logging.info(f"{code} 数据记录不存在, 正常运行, 进度: {n}/{maxn}")
        df = pd.read_excel(os.path.join(DATA_ROOT, file))
        if len(df) == 0:
            logging.warning(f"{code} 数据为空, 无法获取最近存储截至日期，跳过, 进度: {n}/{maxn}")
            continue
        # logging.info(df)
        last_date = df.iloc[-1]["date"]  # 2025-04-25 00:00:00
        last_date_str = str(last_date).split(" ")[0].replace("-", "")  # 提取last_date 中的年月日，到 “yyyymmdd”格式
        begin_date = str(last_date + datetime.timedelta(days=1)).split(" ")[0].replace("-", "")
        symbol = stl.code2akshare_symbol_name(code)
        try:
            next_df = ak.stock_zh_a_daily(symbol=symbol, start_date=begin_date, end_date=end_date, adjust="qfq")
        except:
            logging.warning(f"{code} 获取数据失败，跳过, 进度: {n}/{maxn}")
            continue
        # df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        # next_df['date'] = next_df['date'].dt.strftime('%Y-%m-%d')
        # 合并 df 和 next_df，把 next_df 的数据加到 df 末尾，根据相同列名
        df3 = pd.concat([df, next_df], ignore_index=True)

        record_date = str(df3.iloc[-1]["date"]).split()[0].replace("-", "")
        lasted_date[code] = record_date
        # 将日期列转换为只包含日期的字符串格式
        save_path = os.path.join(DATA_ROOT, file)
        ret = stl.dataframe2excel(save_path, df3, idx=False)
        logging.info(f"NOW: {code} -> {symbol}, 存储日期到：{last_date_str} || 获取更新开始日期：{begin_date}，"
                     f"结束日期为：{end_date}，增加记录为：{len(next_df)}条, 数据更新完毕，记录日期：{record_date}"
                     f", 进度: {n}/{maxn}")
try:
    open("lasted_date_bk.json", 'w').write(json.dumps(lasted_date, ensure_ascii=False))
except:
    logging.error("ERROR | lasted_date_bk.json 文件写入失败")
    # if n > 5:
    #     break
    #    exit()
