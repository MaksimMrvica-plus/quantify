import os
import time
import akshare as ak
import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import tkinter as tk
from tkinter import ttk

from mypack.define import *
import mypack.stock_tools as stl
import mypack.ts_tools as tstl
import mypack.st_time

txt = open(os.path.join(stl.ROOT_PATH, 'global_data', 'self_stocks'), 'r', encoding='utf-8')
selfStocks = []
for line in txt.readlines():
    code, name = line.strip().split()
    selfStocks.append([code, name])


def ak_api_show():
    day_details = ak.stock_zh_a_spot_em()
    filtered_day_details = day_details[day_details[DM].isin([x[0] for x in selfStocks])]
    print(filtered_day_details)
    for index, row in filtered_day_details.iterrows():
        name = row[MC]
        latest_price = row[ZXJ]
        change_rate = row[ZDF]
        open_price = latest_price / (1 + change_rate / 100)
        # sign = '↗' if change_rate > 0 else '↘'
        # sign = '📈' if change_rate > 0 else '📉'
        sign = '🔴' if change_rate > 0 else '🟢'

        print(f"{name[:4]:<8} {open_price:>6.2f} -> {latest_price:<6.2f} {change_rate:>6}% {sign}")


# 实时价格和盘口
def ts_api_show(_codes: list) -> pd.DataFrame:
    # 调整codes适应ts格式
    codestr = ""
    for i, co in enumerate(_codes):
        if i >= 50:
            print("WARING: 单次最多只能接收50个")
            break
        codestr += tstl.format_code(co) + ","
    _df = ts.realtime_quote(codestr[:-1])
    return _df


def update_data(_codes: list, root: tk.Tk, frame: tk.Frame):
    # 清空上次的内容
    for widget in frame.winfo_children():
        widget.destroy()

    # 获取新的数据
    df = ts_api_show(_codes)
    # 只取部分数据
    df = df[['TS_CODE', 'NAME', 'PRICE', 'OPEN', 'PRE_CLOSE', 'TIME', 'DATE']]
    df.insert(3, 'CHANGE', '')
    for index, row in df.iterrows():
        change = round((row['PRICE'] - row['PRE_CLOSE']) / row['PRE_CLOSE'] * 100, 2)
        change = str(change) + '% ↗' if change > 0 else str(change) + '% ↘'
        df.at[index, 'CHANGE'] = change
    # 按照change排序从高到低
    df = df.sort_values(by='CHANGE', ascending=False)
    # 将DataFrame转换为表格并显示在GUI中
    tree = ttk.Treeview(frame, columns=list(df.columns), show='headings')
    # 设置列宽
    column_widths = {'TS_CODE': 80, 'NAME': 80, 'PRICE': 60, 'DATE': 80,
                     'TIME': 60, 'OPEN': 60, 'PRE_CLOSE': 80, 'CHANGE': 80}
    for col in df.columns:
        tree.column(col, width=column_widths.get(col, 100), anchor=tk.E)  # 默认宽度为100
        tree.heading(col, text=col)
    for index, row in df.iterrows():
        tree.insert("", "end", values=list(row))
    tree.pack(fill=tk.BOTH, expand=True)

    # 保存数据到Excel文件
    df.to_excel('ts_realtime_quote.xlsx', index=False)

    # 设置定时器，5秒后再次更新数据
    root.after(5000, lambda: update_data(_codes, root, frame))


def run_tkinter_gui(_codes):
    # 创建主窗口
    root = tk.Tk()
    root.title("Realtime Quote Display")


    # 创建一个框架来放置表格
    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)
    # 启动数据更新循环
    update_data(_codes, root, frame)
    # 运行主循环
    root.mainloop()


if __name__ == '__main__':
    codes = [x[0] for x in selfStocks]
    # while 1:
    #     os.system("cls")
    #     df = ts_api_show(codes)
    #     print(df)
    #     df.to_excel('ts_realtime_quote.xlsx', index=False)
    #     time.sleep(5)
    run_tkinter_gui(codes)
