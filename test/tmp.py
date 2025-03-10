import json
import unittest
import pandas as pd
import akshare as ak
from unittest.mock import patch, MagicMock
import mypack.stock_tools as stl
import os

def count_files_in_directory(directory):
    try:
        # 获取目录中的所有文件和子目录
        files = os.listdir(directory)
        # 过滤出文件（排除子目录）
        files = [f for f in files if os.path.isfile(os.path.join(directory, f))]
        return len(files)
    except FileNotFoundError:
        print(f"目录 {directory} 不存在")
        return 0
    except Exception as e:
        print(f"发生错误: {e}")
        return 0


def getstockhistory():
    codes = open(r"D:\my_projects\quantify\global_data\main_code2name.json", 'r').read()
    codes = json.loads(codes)
    codes = codes.keys()
    for code in codes:
        try:
            stocks = ak.stock_zh_a_hist(symbol=str(code), period="daily", start_date="20240311", end_date="20250309")
            stocks.to_excel(fr"D:\my_projects\quantify\global_data\sotckHistory\{code}.xlsx", index=False)
        except Exception as e:
            print(f"{code}获取失败", e)
            continue


if __name__ == '__main__':
    getstockhistory()
    exit()
    # 指定目录路径
    directory_path = r"D:\my_projects\quantify\global_data\sotckHistory"

    # 统计文件数量
    file_count = count_files_in_directory(directory_path)
    print(f"目录 {directory_path} 下的文件数量: {file_count}")
    exit()
