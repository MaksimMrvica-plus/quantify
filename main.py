import mypack.stock_tools as stl
from mypack.stock_tools import *

DATA_PATH = DATA_PATH
STOCK_HISTORY_PATH = os.path.join(ROOT_PATH, "global_data", "stockHistory")

# 本地加载所有字典  {股票代码 : 名称}
ALL_CODE_NAME_DICT = read_json_to_dict('all_stock_code_name.json')
CODE_LIST = list(ALL_CODE_NAME_DICT.keys())

# 本地加载A股主板字典 （自己用的）
A_CODE_NAME_DICT = read_json_to_dict('A_stock_code_name.json')
A_CODE_LIST = list(A_CODE_NAME_DICT.keys())

if __name__ == '__main__':
    # # 初始化 股票数据目录
    # init_file_dir(DATA_PATH, CODE_LIST)
    # # 初始化 历史日期目录
    # init_file_dir_history_day(HISTORY_DATA_PATH, '20240601', '20240818')
    # # 获取所有股票历史1年(60天)的数据（保存数据，用全部股票）
    get_stock_history_data(STOCK_HISTORY_PATH, CODE_LIST, pre_day=720)
    # 获取大A主板 过去N天信息
    # get_A_stock_history_data(HISTORY_DATA_PATH, A_CODE_LIST, pre_day=720,update=False)
    # df = DF_concat_oneday_stocks_info('20240815', A_CODE_LIST)
    # print(df)

    # TODO : 1.获取某一天的所有股票数据，然后保存到文件中。
    # DF_concat_oneday_stocks_info('20240101', ['000001', '000002', '000003'])
    # TODO : 2.然后根据当天涨停股票收集的历史涨停日期，获取该涨停日期下其他涨停股票代码。
    # ————————————————
    # 获取今日涨停
    # df = DF_get_stock_A_limit_up_today()
    # print(df)
    # code_set = DICT_df_code_to_dict(df)
    # print(code_set)
    # for x in code_set:
    #     print(x, ALL_CODE_NAME_DICT[x])
