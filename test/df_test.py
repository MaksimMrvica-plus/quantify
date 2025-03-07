import unittest
import pandas as pd
import numpy as np
import akshare as ak
from unittest.mock import patch, MagicMock
import mypack.stock_tools as stl


class MyTestCase(unittest.TestCase):
    def test_df_use(self):
        df = pd.DataFrame(np.random.randint(5, 100, size=(5, 3)), index=range(3, 8), columns=list("ABC"))
        print(df)
        print(df.dtypes)
        print(df.describe())
        print(df.head(3))
        print(df.tail(2))
        print(df.T)
        print(df.T.describe())
        print('sum:')
        print(df.sum())  # 列求和
        print(df.sum(1))  # 行求和
        print(df.index)
        print(df.columns)
        print(df.values)
        print(df['C'].values)
        print(df.iloc[1])
        print(df.shape)  # 行，列
        print(df)
        print(df[2:4])  # print(df['a':'b'] 根据index索引类型,如果index是字符，则包括两边，如果index是数字，就代表行数，则不包括右边
        print(df.loc['2':'4', 'A':'B'])  # loc，行切片，无论是数字还是字符，而且是具体行，不是索引号，都是包括两边 ： 从索引格中值为 ‘2’ 到值为 ‘4’
        print(df.loc[2:4, 'A':'B'])  # loc，行切片，无论是数字还是字符，而且是具体行，不是索引号，都是包括两边 ： 从索引格中值为 2 到值为 4
        print(df)
        df['D'] = [1, 2, 3, 4, 5]  # 最右端扩充列
        df.insert(0, 'P', np.array([1, 2, 3, 4, 5]))  # 插入列到中间位置
        df.insert(0, 'Z', [1, 2, 3, 4, 5])
        print(df)

        df2 = pd.DataFrame([5, 1, 2, 3, 4], columns=['Px'])
        print(df2)
        # 以df为基准,根据行列名合并
        df3 = df.join(df2)  # 默认是并集
        print(df3)
        df4 = df.join(df2, how='outer')  # 交集
        print(df4)

        df10 = pd.DataFrame([1, 2, 3, 4, 5, 6], index=list('ABCDEF'), columns=['a'])
        df11 = pd.DataFrame([10, 20, 30, 40, 50, 60], index=list('ABCDEF'), columns=['b'])
        df12 = pd.DataFrame([100, 200, 300, 400, 500, 600], index=list('ABCDEF'), columns=['c'])
        list1 = [df10.T, df11.T, df12.T]
        df13 = pd.concat(list1)  # 行拼接 ，默认是 outer, 最终表拥有所有存在的列
        print(df13)

        df21 = pd.DataFrame([[1, 2, 3, 4, 5, 6, 8]], columns=list('ABCDEFH'), index=['e'])
        df22 = pd.DataFrame([[10, 20, 30, 40, 50, 60]], columns=list('ABCDEF'), index=['f'])
        df23 = pd.DataFrame([[100, 200, 300, 400, 500, 600, 700]], columns=list('ABCDEFG'), index=['g'])
        df14 = pd.concat([df21, df22, df23], join="inner")  # inner，最终表只有，都共同存在的列
        print(df14)

        df15 = pd.concat([df10.T, df11.T, df12.T, df21, df22, df23])
        print(df15)

        df16 = df15.drop_duplicates(subset=['H','G'], keep='first', inplace=False)
        print(df16)


if __name__ == '__main__':
    unittest.main()
