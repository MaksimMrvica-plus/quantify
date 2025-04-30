# -*- coding: utf-8 -*-

import os
from datetime import datetime, timedelta


def str_day_to_datetime(str_day: str) -> datetime.date:
    """
    将字符串日期转换为日期类型
    :param str_day: 字符串日期  "20240101"
    :return: 日期类型
    """
    return datetime.strptime(str_day, "%Y%m%d").date()


def datetime_to_str_day(date: datetime.date) -> str:
    """
    将日期类型转换为字符串日期
    :param date: 日期类型
    :return: 字符串日期  "20240101"
    """
    return date.strftime("%Y%m%d")


def now_datetime() -> datetime.date:
    """
    获取当前日期
    :return: 日期类型
    """
    return datetime.now().date()


def now_date_str() -> str:
    return datetime_to_str_day(now_datetime())


#   确保一个目录存在
def ensure_dir_exists(path_name: str) -> bool:
    """
    确保一个目录存在.   无论返回 True or False 都会创建目录，保证目录存在
    :param path_name: 目录路径
    :return: True or False   ，  True： 本来就存在   ，  False： 本来不存在
    """
    if not os.path.exists(path_name):
        os.makedirs(path_name)
        return False
    else:
        return True


def current_time_to_string(format_str="%Y-%m-%d %H:%M:%S"):
    """
    将当前时间转换为指定格式的字符串。

    :param format_str: 时间格式字符串，默认为"%Y-%m-%d %H:%M:%S"
    :return: 当前时间的字符串表示
    """
    now = datetime.now()
    return now.strftime(format_str)


def current_time_before_n_minutes(n, format_str="%Y-%m-%d %H:%M:%S"):
    """
    获取当前时间前N分钟的字符串格式。

    :param n: 分钟数
    :param format_str: 时间格式字符串，默认为"%Y-%m-%d %H:%M:%S"
    :return: 当前时间前N分钟的字符串表示
    """
    now = datetime.now()
    n_minutes_ago = now - timedelta(minutes=n)
    return n_minutes_ago.strftime(format_str)
