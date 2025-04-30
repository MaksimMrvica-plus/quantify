# -*- coding: utf-8 -*-
import datetime
import random
import time
from typing import List

import pandas as pd

import mypack.stock_tools as stl
import mypack.st_time as stt
import mypack.general_tools as gtl
from mypack.ts_tools import pro
import mypack.ts_tools as tstl
import akshare as ak
import tushare as ts
import os
import logging
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

DATA_ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "global_data", "day_data"))
LOG_ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "log"))
LOG_FILE_PATH = os.path.join(LOG_ROOT_PATH, "real_time_inday.log")
gtl.init_logger(LOG_ROOT_PATH, LOG_FILE_PATH)

MAXN = len(os.listdir(DATA_ROOT_PATH))

THREAD_COUNT = 8


# 一次性获取昨日所有个股信息（）
def collect_yesterday_stock_info_single(maxn: int) -> pd.DataFrame:
    """
    收集 DATA_ROOT_PATH 目录下所有 Excel 文件的最后一行数据，并合并到一个 DataFrame 中
    """
    last_rows = []  # 存储每个文件的最后一行数据
    _n = 0
    # 遍历目录下的所有 .xlsx 文件
    for file in os.listdir(DATA_ROOT_PATH):
        _n += 1
        # if _n > 10:
        #     break
        if file.endswith(".xlsx"):
            code = file.split(".")[0]  # 提取文件名（作为股票代码）
            full_path = os.path.join(DATA_ROOT_PATH, file)

            try:
                # 读取 Excel 文件
                df = pd.read_excel(full_path)
                if len(df) == 0:
                    print(f"{code} 数据为空，跳过", end=" ")
                    continue

                # 获取最后一行数据
                last_row = df.iloc[-1].copy()
                last_row["code"] = code  # 添加股票代码列
                last_rows.append(last_row)
            except Exception as e:
                print(f"处理文件 {file} 出错: {e}", end=" ")
            finally:
                print(f"\r进度: {_n}/{maxn}", end="")

    # 合并所有最后一行数据到一个 DataFrame
    if not last_rows:
        print("目录下没有有效的 Excel 文件")
        return pd.DataFrame()

    combined_df = pd.DataFrame(last_rows)  # 将所有最后一行数据组合成一个 DataFrame

    return combined_df


def process_files(file_list, maxn) -> List:
    last_rows = []  # 存储每个文件的最后一行数据
    _n = 0
    # 遍历目录下的所有 .xlsx 文件
    for file in file_list:
        _n += 1
        if file.startswith("$"):
            continue
        if file.endswith(".xlsx"):
            code = file.split(".")[0]  # 提取文件名（作为股票代码）
            full_path = os.path.join(DATA_ROOT_PATH, file)

            try:
                # 读取 Excel 文件
                df = pd.read_excel(full_path)
                if len(df) == 0:
                    print(f"{code} 数据为空，跳过", end=" ")
                    continue

                # 获取最后一行数据
                last_row = df.iloc[-1].copy()
                last_row["code"] = code  # 添加股票代码列
                last_rows.append(last_row)
            except Exception as e:
                print(f"处理文件 {file} 出错: {e}", end=" ")
            finally:
                print(f"进度: {_n}/{maxn}")

    # 合并所有最后一行数据到一个 DataFrame
    if not last_rows:
        print("目录下没有有效的 Excel 文件")
        return []

    return last_rows


def chunk_list(lst, n):
    """将列表均分成 n 段"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def collect_yesterday_stock_info_multithread(maxn: int) -> pd.DataFrame:
    # 收集所有 .xlsx 文件
    all_files = [f for f in os.listdir(DATA_ROOT_PATH) if f.endswith(".xlsx")][:100]
    random.shuffle(all_files)
    # 均分任务
    chunked_files = list(chunk_list(all_files, THREAD_COUNT))

    # 使用线程池执行
    results = []
    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        future_to_chunk = {executor.submit(process_files, chunk, maxn): chunk for chunk in chunked_files}

        for future in future_to_chunk:
            try:
                result = future.result()
                results += result
            except Exception as exc:
                print(f'生成某块数据时发生异常: {exc}')

    # 合并结果
    combined_df = pd.DataFrame(results)
    print("✅ 所有文件处理完成，已合并成功")
    return combined_df


if __name__ == "__main__":
    tmp_data_root = os.path.join(os.path.dirname(__file__), "..", "tmp", "real_time")
    now_date_str = stt.now_date_str()
    yest_info = pd.DataFrame()
    init_yest_flag = True  # 是否需要初始化昨天信息
    print("初始化昨日信息...")
    if os.path.exists(os.path.join(tmp_data_root, now_date_str + ".xlsx")):  # 存在还要检查一下数量，如果数量太少可能有问题
        yest_info = pd.read_excel(os.path.join(tmp_data_root, now_date_str + ".xlsx"))
        print(f"已有本地数据，读取昨天信息数量: {len(yest_info)}, 已知标的数量:{MAXN}", end="")
        if len(yest_info) < int(MAXN * 0.9):
            print("\t数量较少,需要重新初始化")
        else:
            init_yest_flag = False
            print("\t数量正常,不需要重新初始化")
    if init_yest_flag:  # 需要初始化昨天信息
        if True:  # 默认使用多线程
            yest_info = collect_yesterday_stock_info_multithread(MAXN)
        else:
            yest_info = collect_yesterday_stock_info_single(MAXN)

    yest_info.to_excel(os.path.join(tmp_data_root, now_date_str + ".xlsx"), index=False)
    print("初始化完成，DataFrame数据类型:\n", yest_info.dtypes)

    # 构建 字典 yest_dict  {code : [open,close,high,low,vol , amount]}
    print("构建数据字典...", end="")
    yest_data = {}
    for index, row in yest_info.iterrows():
        code = row['code']
        yest_data[str(code)] = [row['open'], row['close'], row['high'], row['low'], row['volume'], row['amount']]
    print("\r构建数据字典完成")
    # print(yest_data)
    # 轮询实时数据
    while True:
        time.sleep(5)
        # now_df = ak.stock_zh_a_spot_em()
        now_df = pd.read_csv(r"D:\my_projects\quantify\prepare_data\now_df_em.csv", dtype={'代码': str})
        for index, row in now_df.iterrows():
            print(f"正在处理：{code}")
            code = row['代码']
            if len(code) == 8:
                code = code[2:]
            if code in yest_data:
                now_price = row['最新价']
                now_vol = row['成交量']
                now_amplitude = row['涨跌幅']
                now_open = row['今开']
                now_yest_close = row['昨收']
                now_vol_ratio = row['量比']
                now_change_ratio = row['换手率']
                now_pe = row['市盈率-动态']
                # 成交量对比时，要注意单位，daydata中是 股数， nowdata中是 手数，统一转换成 股数 计算
                vol_rate = now_vol*100 / yest_data[code][4]  # 成交量比值
                if 0.5 < vol_rate < 0.8:
                    print(f"✅代码：{code}, "
                          f"昨日收盘价：{now_yest_close:.2f} —> "
                          f"今日开盘价：{now_open:.2f} —> "
                          f"最新价：{now_price:.2f}"
                          f"\t涨跌幅：{row['涨跌幅']:.2f}%"
                          f"\t成交量比值：{vol_rate:.2f}")
                else:
                    print(f"\t\t✅代码：{code}, "
                          f"昨日收盘价：{now_yest_close:.2f} —> "
                          f"今日开盘价：{now_open:.2f} —> "
                          f"最新价：{now_price:.2f}"
                          f"\t涨跌幅：{row['涨跌幅']:.2f}%"
                          f"\t成交量比值：{vol_rate:.2f}")
# 序号,代码,名称,最新价,涨跌幅,涨跌额,成交量,成交额,振幅,最高,最低,今开,昨收,量比,换手率,
# 市盈率-动态,市净率,总市值,流通市值,涨速,5分钟涨跌,60日涨跌幅,年初至今涨跌幅
# now_df = ak.stock_zh_a_spot_em()
# now_df.to_csv("now_df_em.csv", index=False)
# now_df = ak.stock_zh_a_spot()  # 代码,名称,最新价,涨跌额,涨跌幅,成交量,成交额,     最高,最低,今开,昨收,卖出,买入,,时间戳
# now_df.to_csv("now_df.csv", index=False)

# 1. 量能位于昨天的50-80%
