import json
import unittest
import pandas as pd
import akshare as ak
from unittest.mock import patch, MagicMock
import mypack.stock_tools as stl




class MyTestCase(unittest.TestCase):
    def test_something(self):
        stl.get_codes()
    def test_yest_lmtup_today_no(self):
        res = stl.get_yest_limit_today_no("20250305", "20250306")
    def getStockHistory(self):
        codes = open(r"D:\my_projects\quantify\global_data\main_code2name.json",'r').read()
        codes = json.loads(codes)
        codes = codes.keys()
        for code in codes:
            stocks = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20220310", end_date="20250310")
            stocks.to_excel(fr"D:\my_projects\quantify\global_data\sotckHistory\{code}.xlsx", index=False)

if __name__ == '__main__':

    # unittest.main()
    runner = unittest.TextTestRunner(buffer=False)
    # 只测试 test_yest_lmtup_today_no 函数
    suite = unittest.TestSuite()
    suite.addTest(MyTestCase('test_yest_lmtup_today_no'))
    runner.run(suite)