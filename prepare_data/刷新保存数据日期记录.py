# -*- coding: utf-8 -*-
import os
import json
import random

import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed


DATA_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "global_data", "day_data"))
print(DATA_ROOT)

# 设置线程数量
THREAD_COUNT = 8  # 可根据 CPU 核心数调整


def process_files(file_list):
    """
    处理一组文件，返回对应的 lasted_date 字典
    """
    thread_result = {}
    for file in file_list:
        code = file.split(".")[0]
        full_path = os.path.join(DATA_ROOT, file)
        try:
            df = pd.read_excel(full_path)
            if len(df) == 0:
                print(f"{code} 数据为空, 无法获取最近存储截至日期，跳过")
                continue
            last_date = df.iloc[-1]["date"]
            last_date_str = str(last_date).split(" ")[0].replace("-", "")
            print(f"NOW: {code}, 存储日期到：{last_date_str}")
            thread_result[code] = last_date_str
        except Exception as e:
            print(f"处理文件 {file} 出错: {e}")
    return thread_result


def chunk_list(lst, n):
    """将列表均分成 n 段"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


if __name__ == '__main__':
    # 收集所有 .xlsx 文件
    all_files = [f for f in os.listdir(DATA_ROOT) if f.endswith(".xlsx")]
    random.shuffle(all_files)
    # 均分任务
    chunked_files = list(chunk_list(all_files, THREAD_COUNT))

    # 使用线程池执行
    results = {}
    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        future_to_chunk = {executor.submit(process_files, chunk): chunk for chunk in chunked_files}

        for future in future_to_chunk:
            try:
                result = future.result()
                results.update(result)
            except Exception as exc:
                print(f'生成某块数据时发生异常: {exc}')

    # 写入 JSON 文件
    with open("lasted_date.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print("✅ 所有文件处理完成，已写入 lasted_date.json")
