# -*- coding: utf-8 -*-
import mypack.stock_tools as stl
import akshare as ak


"stock_info_sz_name_code"  # 深证证券交易所股票代码和简称
"stock_info_sh_name_code"  # 上海证券交易所股票代码和简称
"stock_info_bj_name_code"  # 北京证券交易所股票代码和简称

sz_codes = ak.stock_info_sz_name_code()
sh_codes = ak.stock_info_sh_name_code()
bj_codes = ak.stock_info_bj_name_code()
# print(sz_codes)
# print(sh_codes)
# print(bj_codes)
print(f"sz nums:{len(sz_codes)}")
print(f"sh nums:{len(sh_codes)}")
print(f"bj nums:{len(bj_codes)}")

main_codes = {}
all_codes = {}

# sz
codes = sz_codes["A股代码"]
names = sz_codes["A股简称"]
dates = sz_codes["A股上市日期"]
for a, b, c in zip(codes, names, dates):
    c = str(c).replace("-", "")
    if a.startswith("60") or a.startswith("00"):
        main_codes[a] = [b, c, "sz"]
    all_codes[a] = [b, c, "sz"]
# sh
codes = sh_codes["证券代码"]
names = sh_codes["证券简称"]
dates = sh_codes["上市日期"]
for a, b, c in zip(codes, names, dates):
    c = str(c).replace("-", "")
    if a.startswith("60") or a.startswith("00"):
        main_codes[a] = [b, c, "sh"]
    all_codes[a] = [b, c, "sh"]
# bj
codes = bj_codes["证券代码"]
names = bj_codes["证券简称"]
dates = sh_codes["上市日期"]

for a, b, c in zip(codes, names, dates):
    c = str(c).replace("-", "")
    if a.startswith("60") or a.startswith("00"):
        main_codes[a] = [b, c, "bj"]
    all_codes[a] = [b, c, "bj"]

# print(main_codes)
# print(all_codes)
print(f"main nums:{len(main_codes)}")
print(f"all nums:{len(all_codes)}")

stl.save_dict_to_json("main_codes.json", main_codes)
stl.save_dict_to_json("all_codes.json", all_codes)
