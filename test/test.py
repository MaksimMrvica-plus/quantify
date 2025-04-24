import pandas as pd
import akshare as ak
import mypack.stock_tools as stl
import mypack.ts_tools as tstl
from datetime import datetime
from st_time import *

# res = stl.get_yest_limit_today_no("20250305", "20250306")

res = tstl.pro.query("daily", ts_code='603173.sh,605208.sh,603665.sh', trade_date='20250423')
for x in res:
    print(x)
print(res)


def pre_n_days_trade_date(n: int = 5) -> list:
    now_date = now_datetime()
    _end = datetime_to_str_day(now_date)
    pre_date = now_date - timedelta(days=n * 2)  # 防止假期，结果数量不足
    _begin = datetime_to_str_day(pre_date)
    _code = "600000.sh"
    df = tstl.pro.query("daily", ts_code=_code, start_date=_begin, end_date=_end)
    # print(df)
    _res = df['trade_date'].tolist()
    return _res[:n]


tdays = pre_n_days_trade_date(3)
print(tdays)
