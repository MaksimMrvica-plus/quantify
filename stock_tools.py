# -*- coding: utf-8 -*-
import concurrent.futures
import threading
import time
import os

import pandas.core.frame

from format_trans import *

DATA_PATH = 'stock_data'
HISTORY_DATA_PATH = 'history_data'
A_STOCK_CODE_NAME_DICT_PATH = 'A_stock_code_name.json'


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
    dataframe.to_excel(excel_filename, index=True)  # index=False表示不将行索引写入
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
    end = datetime.datetime.now().strftime("%Y%m%d")
    start = (datetime.datetime.now() - datetime.timedelta(days=n)).strftime("%Y%m%d")
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
        print(f"\r正在收集 日期：[{date}]  股票：[{code}]   进度：{idx}/{n}", end="")
        # print(f"正在收集 日期：[{date}]  股票：[{code}]   进度：{idx}/{n}")
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
    s_date = str_day_to_datetime(start_day)
    e_date = str_day_to_datetime(end_day)

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
    e_date = datetime.datetime.now().strftime("%Y%m%d")
    s_date = (datetime.datetime.now() - datetime.timedelta(days=pre_day)).strftime("%Y%m%d")
    try:
        _end = len(code_list)
        idx = 0
        for code in code_list:
            idx += 1
            save_path = os.path.join(path_name, code, 'history_' + str(pre_day) + '.xlsx')
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
    str_end_date = datetime_to_str_day(e_date)
    try:
        str_date = datetime_to_str_day(_date)
        if not is_trade_day(str_date):
            print(f"{str_date} 不是交易日，跳过")
            return True

        _p = os.path.join(path_name, str_date)
        save_path = os.path.join(_p, 'A_history.xlsx')
        if not update:  # 如果不更新旧数据，则使用已存在的内容。
            if os.path.exists(save_path):
                print(f"{str_date} 数据已存在，跳过")
                return True

        print(f"正在处理 ： {str_date}/{str_end_date}")
        _df = DF_concat_oneday_stocks_info(str_date, code_list)
        # 确保目录存在，并写入文件

        ensure_dir_exists(_p)
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
    e_date = datetime.datetime.now()
    s_date = datetime.datetime.now() - datetime.timedelta(days=pre_day + 1)
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

    # TODO
# check_stock_history_limit_up_date()

# get_last_n_trade_date(365)


# TODO : 1.获取某一天的所有股票数据，然后保存到文件中。
# DF_concat_oneday_stocks_info('20240101', ['000001', '000002', '000003'])
# TODO : 2.然后根据当天涨停股票收集的历史涨停日期，获取该涨停日期下其他涨停股票代码。
