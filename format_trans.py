# -*- coding: utf-8 -*-

import akshare as ak
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pandas.core.frame
import json
import os
import datetime
import collections
from pandas import DataFrame


def str_day_to_datetime(str_day: str) -> datetime.date:
    """
    将字符串日期转换为日期类型
    :param str_day: 字符串日期  "20240101"
    :return: 日期类型
    """
    return datetime.datetime.strptime(str_day, "%Y%m%d").date()


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
    return datetime.datetime.now().date()


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
