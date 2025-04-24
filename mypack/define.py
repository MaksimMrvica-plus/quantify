import os

DM = "代码"
GPDM = "股票代码"
MC = "名称"
ZXJ = "最新价"
ZDF = "涨跌幅"
ZDE = "涨跌额"
CJL = "成交量"
CJE = "成交额"
ZF = "振幅"
ZGJ = "最高"
ZDJ = "最低"
JKJ = "今开"
ZSJ = "昨收"
LB = "量比"
HSL = "换手率"
ZSZ = "总市值"
LTSZ = "流通市值"
ZS = "涨速"
ZD5 = "5分钟涨跌"
ZDF60 = "60日涨跌幅"
NCZJZF = "年初至今涨幅"


FILE_PATH = os.path.dirname(__file__)  # "...../quantify/mypack"
ROOT_PATH = os.path.join(FILE_PATH, '..')  # "...../quantify"
DATA_PATH = 'stock_data'
HISTORY_DATA_PATH = 'history_data'
A_STOCK_CODE_NAME_DICT_PATH = 'A_stock_code_name.json'
