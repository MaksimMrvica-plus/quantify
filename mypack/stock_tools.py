# -*- coding: utf-8 -*-
import concurrent.futures

import threading
import time
import os
import akshare as ak
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pandas.core.frame
import json
import pandas.core.frame
import mplfinance as mpf
import collections
from datetime import datetime

import mypack.st_time as stt
from mypack.define import *

FILE_PATH = os.path.dirname(__file__)  # "...../quantify/mypack"
ROOT_PATH = os.path.join(FILE_PATH, '..')  # "...../quantify"
DATA_PATH = 'stock_data'
HISTORY_DATA_PATH = 'history_data'
A_STOCK_CODE_NAME_DICT_PATH = 'A_stock_code_name.json'


def code2akshare_symbol_name(code_str: str) -> str:
    """
    将股票代码转换为股票名称
    :param code_str: 股票代码
    :return: 股票名称
    """
    res = code_str
    if code_str.startswith('6'):
        res = 'sh' + code_str
    elif code_str.startswith(('0', '3')):
        res = 'sz' + code_str
    elif code_str.startswith(('4', '8', '9')):
        res = 'bj' + code_str
    return res


# 获取A主板常用股票代码和名称
def save_A_code_name_dict_to_json(path_name: str) -> bool:
    """
    获取股票代码和名称字典
    :return:
    """
    dc_code_name = {}
    _df = ak.stock_zh_a_spot_em()
    _df = _df[_df['代码'].str.startswith(('60', '00'))]  # 主板
    for row in _df.itertuples():
        _k = getattr(row, '代码')
        _v = getattr(row, '名称')
        dc_code_name[_k] = _v
    js = json.dumps(dc_code_name, ensure_ascii=False)
    with open(path_name, 'w') as f:
        f.write(js)
    return True


def dataframe2list(dataframe: pandas.core.frame.DataFrame) -> list:
    """
    将DataFrame转换为列表
    :param dataframe: DataFrame
    :return:
    """
    np_array = np.array(dataframe)
    data_list = list(np_array)
    return data_list


def dataframe2excel(path_name, dataframe, idx=False) -> bool:
    """
    将DataFrame保存到Excel
    :param path_name: Excel文件路径
    :param dataframe: DataFrame
    :param idx: 是否写入索引
    :return:
    """
    excel_filename = path_name  # Excel文件名
    dataframe.to_excel(excel_filename, index=idx)  # index=False表示不将行索引写入
    return True


def get_code_and_name_dict() -> dict:
    """
    获取股票代码和名称字典
    :return:
    """
    dc_code_name = {}
    stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
    codes = stock_zh_a_spot_em_df['代码']
    names = stock_zh_a_spot_em_df['名称']
    assert len(codes) == len(names)
    for i in range(len(codes)):
        dc_code_name[codes[i]] = names[i]
    print("获取股票代码和名称字典，数量：", len(dc_code_name))
    return dc_code_name


def save_dict_to_json(path_name, dc_dict) -> bool:
    """
    将字典保存到json
    :param path_name: json文件路径
    :param dc_dict: 字典
    :return:
    """
    with open(path_name, 'w') as f:
        json.dump(dc_dict, f, ensure_ascii=False)
    return True


def read_json_to_dict(path_name) -> dict:
    """
    读取json文件到字典
    :param path_name: json文件路径
    :return:
    """
    with open(path_name, 'r') as f:
        _p = json.load(f)
    return _p


def update_stock_code_name_dict(path_name) -> bool:
    """
    更新股票代码和名称字典
    :param path_name: json文件路径
    """
    try:
        _dict = get_code_and_name_dict()
        save_dict_to_json(path_name, _dict)
        return True
    except Exception as e:
        print(e)
        return False


# 获取过去 N天 中，是交易日的日期
def get_last_n_trade_date(n: int) -> list:
    """
    获取过去 N天 中，是交易日的日期
    :param n:
    :return:    ['20230821', '20230822', '20230823']
    """
    _list = []
    end = datetime.now().strftime("%Y%m%d")
    start = (datetime.now() - datetime.timedelta(days=n)).strftime("%Y%m%d")
    _df = ak.stock_zh_a_hist(symbol='000001', period="daily", start_date=start, end_date=end)
    dates = [x.strftime("%Y%m%d") for x in list(_df['日期'])]
    return dates


# 筛选策略
def DF_filter_limit_up(df: pandas.core.frame.DataFrame) -> pandas.core.frame.DataFrame:
    """
    股票筛选, 不会改变原 df 内容
    :param df: DataFrame
    :return:
    """
    _df = df
    _df = _df[_df['代码'].str.startswith(('60', '0'))]  # 主板
    _df = _df[_df['涨跌幅'] >= 9.8]  # 涨停
    return _df


# 查看A股主板当天涨停股票
def DF_get_stock_A_limit_up_today() -> pandas.core.frame.DataFrame:
    """
    获取当日涨停股票
    :return:
    """
    _df = ak.stock_zh_a_spot_em()

    # 应用涨停策略
    _df1 = DF_filter_limit_up(_df)
    # 刷新序号
    _df1.reset_index(drop=True, inplace=True)

    return _df1.loc[:, ['代码', '名称', '涨跌幅']]


# 某一天，某些股票信息
def DF_concat_oneday_stocks_info(date: str, code_list: list) -> pandas.core.frame.DataFrame:
    """
    获取某一天，所有股票信息, 如果当天不是交易日，则返回 Empty DataFrame
    :param code_list:
    :param date: 日期  ex: '20240101'
    :return:
    """
    n = len(code_list)
    idx = 0
    res_df = pd.DataFrame()

    for code in code_list:
        idx += 1
        print(f"\r正在收集 日期：[{date}]  [{code}]   进度：{idx}/{n}", end="")
        _df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=date, end_date=date)
        if _df.empty:
            continue
        else:
            res_df = pd.concat([res_df, _df], ignore_index=True)
            # print(_df, res_df)
    res_df.reset_index(drop=True, inplace=True)
    print()
    return res_df


# 提取df中的股票票代码到字典中
def DICT_df_code_to_dict(df: pandas.core.frame.DataFrame) -> dict:
    """
    提取股票代码到集合中
    :param df: DataFrame
    :return:
    """
    _dict = {}
    for row in df.itertuples():
        _k = getattr(row, '代码')
        _v = getattr(row, '名称')
        _dict[_k] = _v
    return _dict


def get_codes():
    pt = pd.read_excel(r"D:\my_projects\quantify\strategy1\20250306\main_board_stocks.xlsx", dtype={"代码": str})
    codes = pt['代码'].to_list()
    names = pt['名称'].to_list()
    wp = r'D:\my_projects\quantify\main_code2name.json'
    wp2 = r'D:\my_projects\quantify\main_name2code.json'
    dc = {}
    dc2 = {}
    for i in range(len(codes)):
        dc[codes[i]] = names[i]
        dc2[names[i]] = codes[i]
    print(len(dc))
    save_dict_to_json(wp, dc)
    save_dict_to_json(wp2, dc2)


# 判断一天是否为交易日
def is_trade_day(date: str) -> bool:
    """
    判断是否为交易日
    :param date: 日期  '20240101'
    :return:
    """
    stock_szse_summary_df = ak.stock_szse_summary(date=date)
    return not stock_szse_summary_df.empty


# 文件目录初始化
def init_file_dir(path_name: str, code_list: list) -> bool:
    """
    初始化文件目录
    :param path_name:
    :param code_list:
    :return:
    """
    cwd = os.getcwd()
    root_path = os.path.join(cwd, path_name)
    print("执行根目录：", root_path)
    # 创建数据根目录
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    # 创建股票子目录
    for code in code_list:
        path_name = os.path.join(root_path, code)
        if not os.path.exists(path_name):
            os.makedirs(path_name)
    return True


def init_file_dir_history_day(path_name: str, start_day: str, end_day: str) -> bool:
    cwd = os.getcwd()
    root_path = os.path.join(cwd, path_name)
    print("执行根目录：", root_path)
    # 创建数据根目录
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    # 创建股票子目录
    s_date = stt.str_day_to_datetime(start_day)
    e_date = stt.str_day_to_datetime(end_day)

    _day = s_date
    while _day <= e_date:
        _date = _day.strftime("%Y%m%d")
        if is_trade_day(_date):
            save_path = os.path.join(root_path, _date)
            if not os.path.exists(save_path):
                os.makedirs(save_path)
        _day = _day + datetime.timedelta(days=1)
    return True


# 遍历代码，获取 股票列表中 每个股票 一定时间范围内 的 历史数据并保存。
def get_stock_history_data(path_name: str, code_list: list, pre_day=365) -> bool:
    """
    获取股票历史数据
    :param pre_day:
    :param path_name: 保存路径
    :param code_list:
    :return:
    """
    e_date = datetime.now().strftime("%Y%m%d")
    s_date = (datetime.now() - datetime.timedelta(days=pre_day)).strftime("%Y%m%d")
    try:
        _end = len(code_list)
        idx = 0
        for code in code_list:
            idx += 1
            save_path = os.path.join(path_name, f'{code}.xlsx')
            print("\r", end="")
            if os.path.exists(save_path):
                print(f"{code} 已存在，跳过", end="")
                continue
            print(f"正在处理 ：{code}    {idx}/{_end}", end="")
            df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=s_date, end_date=e_date)

            dataframe2excel(save_path, df, idx=False)
        print("\n获取股票历史数据成功")
        return True
    except Exception as e:
        print("获取股票历史数据失败, Error: ", e)
        return False


def thread_for_GET_A_STOCK_HISTORY_DATA(path_name, code_list, s_date, e_date, update):
    _date = s_date
    str_end_date = stt.datetime_to_str_day(e_date)
    try:
        str_date = stt.datetime_to_str_day(_date)
        if not is_trade_day(str_date):
            print(f"{str_date} 不是交易日，跳过")
            return True

        save_path = os.path.join(path_name, f'{str_date}.xlsx')
        if not update:  # 如果不更新旧数据，则使用已存在的内容。
            if os.path.exists(save_path):
                print(f"{str_date} 数据已存在，跳过")
                return True

        print(f"正在处理 ： {str_date}/{str_end_date}")
        _df = DF_concat_oneday_stocks_info(str_date, code_list)
        # 确保目录存在，并写入文件
        _df.to_excel(save_path, idx=False)
        dataframe2excel(save_path, _df, idx=False)
        return True
    except Exception as e:
        print("\nError: ", e)
        return False


# 获取A主板  之前 天数范围内  每一天  主板股票历史数据
def get_A_stock_history_data(path_name: str, code_list: list, pre_day=30, update=False) -> bool:
    """
    获取A主板  之前 天数范围内  每一天  主板股票历史数据
    :param path_name: 保存路径
    :param code_list:
    :param pre_day:
    :param update:  是否采取更新策略， True: 重新获取数据，覆盖更新旧内容
    :return:
    """
    e_date = datetime.now()
    s_date = datetime.now() - datetime.timedelta(days=pre_day + 1)
    # 单线程
    # _date = s_date
    # str_end_date = datetime_to_str_day(e_date)
    # try:
    #     while _date <= e_date:
    #         _date = _date + datetime.timedelta(days=1)
    #
    #         str_date = datetime_to_str_day(_date)
    #         if not is_trade_day(str_date):
    #             print(f"{str_date} 不是交易日，跳过")
    #             continue
    #
    #         _p = os.path.join(path_name, str_date)
    #         save_path = os.path.join(_p, 'A_history.xlsx')
    #         if not update:  # 如果不更新旧数据，则使用已存在的内容。
    #             if os.path.exists(save_path):
    #                 print(f"\r{str_date} 数据已存在，跳过")
    #                 continue
    #
    #         print(f"正在处理 ： {str_date}/{str_end_date}")
    #         _df = DF_concat_oneday_stocks_info(str_date, code_list)
    #         # 确保目录存在，并写入文件
    #
    #         ensure_dir_exists(_p)
    #         dataframe2excel(save_path, _df, idx=False)
    #
    #     print("\n获取大A主板历史数据成功")
    #     return True
    # except Exception as e:
    #     print("\n获取大A主板历史数据失败, Error: ", e)
    #     return False

    # 多线程：创建线程池
    _date = s_date
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # 提交任务到线程池
        while _date <= e_date:
            _date = _date + datetime.timedelta(days=1)
            futures = {executor.submit(thread_for_GET_A_STOCK_HISTORY_DATA,
                                       path_name, code_list, _date, e_date, update)}
    return True


# 读取excel内容到DataFrame
def read_excel_to_df(path_name: str) -> pandas.core.frame.DataFrame:
    """
    读取excel内容到DataFrame
    :param path_name:
    :return:
    """
    df = pd.read_excel(path_name)
    return df


# 检查今日涨停股票在历史上的涨停日期
def check_stock_history_limit_up_date(pre_day: int) -> bool:
    """
    检查今日涨停股票在历史上的涨停日期
    :param pre_day: 检查范围
    :return:
    """
    _df = DF_get_stock_A_limit_up_today()  # 筛选：大A 主板
    _dict = DICT_df_code_to_dict(_df)
    print(_dict)
    res_dict = collections.defaultdict(list)
    for code in _dict.keys():
        path_name = os.path.join('stock_data', code, 'history_' + str(pre_day) + '.xlsx')
        if not os.path.exists(path_name):
            print(f"\r{code} {_dict[code]} [{pre_day}]天范围内 历史数据不存在，跳过", end="")
            continue
        print(f"\r正在处理 ：{code} {_dict[code]}", end="")
        df = read_excel_to_df(path_name)
        df = df[df['涨跌幅'] >= 9.8]
        for row in df.itertuples():
            _date = getattr(row, '日期')
            print(_date)
            res_dict[code].append(_date)


def get_current_n_minutes_time_sharing(stock_code="000001", n=0, period="1") -> pd.DataFrame:
    ss = ak.stock_zh_a_hist_min_em(stock_code, period="1", start_date=stt.current_time_before_n_minutes(n + 1),
                                   end_date=stt.current_time_to_string())
    return ss


def get_a_share_main_board() -> pd.DataFrame:
    try:
        # merged_data = ak.stock_zh_a_spot_em()
        merged_data = pd.concat([ak.stock_sh_a_spot_em(), ak.stock_sz_a_spot_em()])
        # 去掉无数据股票
        merged_data = merged_data.dropna(subset=["最新价"])
        # 筛选
        main_board_stocks = merged_data[
            (~merged_data["名称"].str.contains("ST"))
            & (~merged_data["名称"].str.contains("C"))
            & (~merged_data["名称"].str.contains("退市"))
            & (
                    (merged_data["代码"].str.startswith("00"))
                    | (merged_data["代码"].str.startswith("60"))
            )]
        # 去重
        main_board_stocks = main_board_stocks.drop_duplicates(subset=["代码"])
        return main_board_stocks
    except Exception as e:
        print(f"获取时发生错误: {e}")
        return pd.DataFrame()


def has_limit_up_in_last_month(pd):
    rescodes = []
    codes = pd["代码"]
    n = len(codes)
    i = 1
    now_date = datetime.now()
    now_str = stt.datetime_to_str_day(now_date)
    pre_month = now_date - datetime.timedelta(days=30)
    pre_str = stt.datetime_to_str_day(pre_month)
    print(f"查询日期在 {pre_str} 到 {now_str} 之间的涨停情况")
    for code in codes:
        print('\r', code, "\t", i, "/", n, end="")
        i += 1
        try:
            stock_data = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=pre_str, end_date=now_str)
            if "涨跌幅" not in stock_data.columns:
                print(f"数据列中没有找到 '涨跌幅' 列，无法判断。")
                continue
            limit_up_price = stock_data["涨跌幅"] >= 9.0
            if limit_up_price.any():
                rescodes.append(code)
        except Exception as e:
            print(f"获取 {code} 历史数据时发生错误: {e}")
            continue
    # 取交集
    limitup = pd[pd["代码"].isin(rescodes)]
    return limitup


def today_rate_less_x(data, ratio):
    data = data.drop_duplicates(subset=["代码"])
    try:
        if "涨跌幅" not in data.columns:
            print("数据列中没有找到 '涨跌幅' 列，无法进行过滤。")
            return pd.DataFrame()

        # 过滤出 '涨跌幅' 小于 ratio 的行
        filtered_data = data[data["涨跌幅"] < ratio]

        return filtered_data
    except Exception as e:
        print(f"过滤数据时发生错误: {e}")
        return data


def today_price_less_x(data, price):
    try:
        if "最新价" not in data.columns:
            print("数据列中没有找到 '最新价' 列，无法进行过滤。")
            return pd.DataFrame()

        # 过滤出 '现价' 小于 price 的行
        filtered_data = data[data["最新价"] < price]

        return filtered_data
    except Exception as e:
        print(f"过滤数据时发生错误: {e}")
        return data


# 去掉市值超过300亿的, value单位为 亿
def filter_market_value(data, max_market_value=300):
    try:
        if "总市值" not in data.columns:
            print("数据列中没有找到 '总市值' 列，无法进行过滤。")
            return data
        filtered_data = data[data["总市值"] < max_market_value * 100000000]
        return filtered_data
    except Exception as e:
        print(f"过滤数据时发生错误: {e}")
        return data


def today_amplitude_more_than_x(data, ratio):
    try:
        if "涨跌幅" not in data.columns:
            print("数据列中没有找到 '涨跌幅' 列，无法进行过滤。")
            return pd.DataFrame()

        # 过滤出 '涨跌幅' 大于 ratio 的行
        filtered_data = data[data["涨跌幅"] > ratio]

        return filtered_data
    except Exception as e:
        print(f"过滤数据时发生错误: {e}")
        return data


def today_liangbi_more_than_x(data, ratio):
    try:
        if "量比" not in data.columns:
            print("数据列中没有找到 '量比' 列，无法进行过滤。")
            return data

        # 过滤出 '量比' 大于 ratio 的行
        filtered_data = data[data["量比"] > ratio]

        return filtered_data
    except Exception as e:
        print(f"过滤数据时发生错误: {e}")
        return data


def today_amplitude_range(data, low, high):
    try:
        if "涨跌幅" not in data.columns:
            print("数据列中没有找到 '涨跌幅' 列，无法进行过滤。")
            return pd.DataFrame()

        # 过滤出 '涨跌幅' 大于low，小于high 的行
        filtered_data = data[data["涨跌幅"] > low]
        filtered_data = filtered_data[filtered_data["涨跌幅"] < high]

        return filtered_data
    except Exception as e:
        print(f"过滤数据时发生错误: {e}")
        return data


def get_stock_minute_data(stock_code, last_n_rows=250):
    try:
        # 获取分时数据
        min_data = ak.stock_zh_a_minute(symbol=stock_code, period='1')
        # 取最后 last_n_rows 行
        last_minute_data = min_data.tail(last_n_rows)
        return last_minute_data
    except Exception as e:
        print(f"获取股票 {stock_code} 分时数据时发生错误: {e}")
        return pd.DataFrame()


def now7open7yesterday(data):
    try:
        if (
                ("最新价" not in data.columns)
                or ("今开" not in data.columns)
                or ("昨收" not in data.columns)
        ):
            print("数据列中没有找到 ['最新价','今开','昨收'] 列，无法进行过滤。")
            return pd.DataFrame()
        filtered_data = data[data["最新价"] >= data["今开"]]
        filtered_data = filtered_data[filtered_data["今开"] >= filtered_data["昨收"]]
        return filtered_data
    except Exception as e:
        print(f"过滤数据时发生错误: {e}")
        return data


def draw_price(prices, stock_code="SECRET"):
    # 绘制收盘价折线图
    plt.figure(figsize=(12, 6))
    plt.plot(prices, label='Close Price', color='b')
    plt.title(f'Last 250 Minutes Close Prices for {stock_code}')
    plt.xlabel('Time')
    plt.ylabel('Close Price')
    plt.legend()
    plt.grid(True)
    plt.show()


def draw_price_details(open, high, low, close, stock_code="SECRET"):
    res = []
    for i in range(len(open)):
        o = open[i]
        h = high[i]
        l = low[i]
        c = close[i]
        res.append(o)
        res.append(h)
        res.append(l)
        res.append(c)
    draw_price(res, stock_code)


def draw_candlestick_chart(data, stock_code="SECRET"):
    # 确保数据列名正确
    data.columns = ['day', 'open', 'high', 'low', 'close', 'volume']
    # 将时间列转换为datetime类型
    data['day'] = pd.to_datetime(data['day'])
    # 设置时间列为索引
    data.set_index('day', inplace=True)

    # 绘制图
    mpf.plot(data, type='candle', style='yahoo', title=f'Last 250 Minutes Candlestick Chart for {stock_code}',
             ylabel='Price', ylabel_lower='Volume', volume=True, figratio=(12, 6))


def get_yest_limit_today_no(yeststr: str = "20250305", todaystr: str = "20250306"):
    cj = read_json_to_dict(os.path.join(ROOT_PATH, 'global_data', 'main_code2name.json'))
    code_list = list(cj.keys())
    yest_lmtup = DF_concat_oneday_stocks_info(yeststr, code_list)
    # print(yest_lmtup)
    today_no = DF_concat_oneday_stocks_info(todaystr, code_list)
    # print(today_no)
    yest_lmtup = yest_lmtup[yest_lmtup[ZDF] > 9.8]
    today_no = today_no[today_no[ZDF] < 9.8]
    merge = pd.merge(yest_lmtup, today_no, on=GPDM, how='inner')
    # print(merge)
    # print(len(merge))
    # merge.to_excel(f'lmtup_no_{todaystr}.xlsx', index=False)
    return merge
