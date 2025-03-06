import time

import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf

import st_time
import stock_tools


def get_a_share_main_board() -> pd.DataFrame:
    try:
        merged_data = ak.stock_zh_a_spot_em()

        # 筛选
        main_board_stocks = merged_data[
            (~merged_data["名称"].str.contains("ST"))
            & (~merged_data["名称"].str.contains("C"))
            & (~merged_data["名称"].str.contains("退市"))
            & (~merged_data["代码"].str.startswith("688"))
            & (~merged_data["代码"].str.startswith("689"))
            & (~merged_data["代码"].str.startswith("30"))
            & (~merged_data["代码"].str.startswith("8"))
            & (~merged_data["代码"].str.startswith("9"))
            & (~merged_data["代码"].str.startswith("4"))
            ]
        # 根据代码去重
        main_board_stocks = main_board_stocks.drop_duplicates(subset=["代码"])
        main_board_stocks.to_excel("stock_data.xlsx", index=False)
        return main_board_stocks
    except Exception as e:
        print(f"获取时发生错误: {e}")
        return pd.DataFrame()


def has_limit_up_in_last_month(pd):
    rescodes = []
    codes = pd["代码"]
    n = len(codes)
    i = 1
    for code in codes:
        print(code, "\t", i, "/", n)
        i += 1
        try:
            stock_data = ak.stock_zh_a_hist(
                symbol=code, period="daily", start_date="20250204", end_date="20250304"
            )
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


def today_amplitude_more_than_x(data, ratio):
    try:
        if "振幅" not in data.columns:
            print("数据列中没有找到 '振幅' 列，无法进行过滤。")
            return pd.DataFrame()

        # 过滤出 '振幅' 大于 ratio 的行
        filtered_data = data[data["振幅"] > ratio]

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

    # 绘制K线图
    mpf.plot(data, type='candle', style='yahoo', title=f'Last 250 Minutes Candlestick Chart for {stock_code}',
             ylabel='Price', ylabel_lower='Volume', volume=True, figratio=(12, 6))


# 示例调用
if __name__ == "__main__":
    # # 1 主筛
    # main_board_stocks = get_a_share_main_board()
    # print("主筛结果: ", len(main_board_stocks))
    # #print(main_board_stocks)
    # # 2 停
    # limitup = has_limit_up_in_last_month(main_board_stocks)
    # print("停: ", len(limitup))
    # #print(limitup)
    # limitup.to_excel("limitup.xlsx", index=False)
    # limitup = pd.read_excel("limitup.xlsx", dtype={"代码": str})
    # # 3 浮动低
    # low_today = today_rate_less_x(limitup, 7.5)
    # print("当天低位: ", len(low_today))
    # low_today.to_excel("low_today.xlsx", index=False)
    # # 4 低值
    # low_today = pd.read_excel("low_today.xlsx", dtype={"代码": str})
    # price = 35
    # low_price_today = today_price_less_x(low_today, price)
    # print(f"当天值低于 {price}:  {len(low_price_today)}")
    # low_price_today.to_excel("low_price_today.xlsx", index=False)
    # # 5 浮动
    # low_price_today = pd.read_excel("low_price_today.xlsx", dtype={"代码": str})
    # amplow = 1.5
    # amphigh = 5
    # low_amplitude_today = today_amplitude_range(low_price_today, amplow, amphigh)
    # print(f"当天浮动{amplow} ~ {amphigh}:  {len(low_amplitude_today)}")
    # low_amplitude_today.to_excel("low_amplitude_today.xlsx",index=False)
    # # 6 当前>开>收
    # low_amplitude_today = pd.read_excel("low_amplitude_today.xlsx", dtype={"代码": str})
    # now_open_yest = now7open7yesterday(low_amplitude_today)
    # print(f"当前>开>收:  {len(now_open_yest)}")
    # now_open_yest.to_excel("now_open_yest.xlsx", index=False)
    # # 7 liangbi
    # now_open_yest = pd.read_excel("now_open_yest.xlsx", dtype={"代码": str})
    # lb_val = 1.5
    # liangbi = today_liangbi_more_than_x(now_open_yest, lb_val)
    # print(f"量比>{lb_val}:  {len(liangbi)}")
    # liangbi.to_excel("liangbi.xlsx", index=False)
    # # 8.1 time sharing
    # liangbi = pd.read_excel("liangbi.xlsx", dtype={"代码": str})
    # for stock_code, name in zip(liangbi["代码"], liangbi["名称"]):
    #     print(f"正在处理 {stock_code} {name}")
    #     ss = stock_tools.get_current_n_minutes_time_sharing(stock_code)
    #     ssnp = ss.to_numpy()
    #     # print(ssnp)
    #     for i in range(len(ssnp)):
    #         print(ssnp[i][0], ssnp[i][2])
    #     # break
    #     time.sleep(1)
    # # 8.2 详情
    liangbi = pd.read_excel("liangbi.xlsx", dtype={"代码": str})
    # 提取代码列和名称列
    liangbi_extracted = liangbi[["代码", "名称"]]
    # 创建一个新的数据框
    new_liangbi = pd.DataFrame(columns=["代码", "名称"])
    # 将提取的数据添加到新数据框中
    new_liangbi = pd.concat([new_liangbi, liangbi_extracted], ignore_index=True)
    # 插入新的数据行
    new_row = pd.DataFrame({"代码": ["600839"], "名称": ["四川长虹"]})
    new_liangbi = pd.concat([new_liangbi, new_row], ignore_index=True)
    liangbi = new_liangbi

    liangbi_codes = liangbi["代码"].unique()
    day_details = ak.stock_zh_a_spot_em()
    filtered_day_details = day_details[day_details["代码"].isin(liangbi_codes)]
    print(filtered_day_details)
    for index, row in filtered_day_details.iterrows():
        name = row["名称"]
        latest_price = row["最新价"]
        change_rate = row["涨跌幅"]
        open_price = latest_price/(1+change_rate/100)
        sign = '↑' if change_rate > 0 else '↓'
        print(f"{name[:4]:>5} {open_price:>6.2f} -> {latest_price:<6.2f} {change_rate:>6}% {sign}")

    # 完整分时内分时
    # stock_code = "sz000001"
    # last_minute_data = get_stock_minute_data(stock_code, 1700)
    # print(last_minute_data)
    # last_minute_data.to_excel(f"{stock_code}_last_minute_data.xlsx", index=False)
    # minute_data = pd.read_excel("sz000001_last_minute_data.xlsx", dtype={"代码": str})
    # # 一天238，一周1190
    # tail = minute_data.tail(238)
    # print(tail)
    # print("week:\n")
    # print(minute_data.tail(1190))
    # # draw_price(prices,"sz000001")
    # low = tail["low"].tolist()
    # high = tail["high"].tolist()
    # open = tail["open"].tolist()
    # close = tail["close"].tolist()
    # # draw_price_details(open,high,low,close,"sz000001")
    # draw_candlestick_chart(tail)
"""
当天低位:  1095
当天值低于 35:  988
当天浮动1.5 ~ 5:  201
当前>开>收:  102
量比>1.5:  16

当天低位:  724
当天值低于 35:  656
当天浮动1.5 ~ 5:  136
当前>开>收:  71
量比>1.5:  10
"""


