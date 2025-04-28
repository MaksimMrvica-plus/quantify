import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
from datetime import datetime
# Import the backtrader platform
import backtrader as bt
import pandas as pd

OPEN_HUANCE = 0
if OPEN_HUANCE == 1:
    HUANCE = True
else:
    HUANCE = False

BEGIN_PERIOD = 3
END_PERIOD = 20

MAPERIOD = 3

FILE_PATH = r"D:\my_projects\quantify\global_data\day_data\603195.xlsx"
INIT_CASH = 1000000.0
COMMISSION = 0.0001  # 万分之一， 0.01%
FIXED_STAKE = 1000
PERCENT_STAKE = 80  # 50%
MAXCPUS = 1

START_DATE = datetime(2020, 3, 6)  # 回测开始时间
# START_DATE = None

# END_DATE = datetime(2025, 3, 7)  # 回测结束时间
END_DATE = None


# --------------------------------------------------
# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('myparam', 27),
        ('exitbars', 3),
        ('maperiod', 15),
        ('printlog', False),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.success_times = 0
        self.fail_times = 0
        self.trade_times = 0
        self.max_value = float('-inf')
        self.min_value = float('inf')
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

        # Indicators for the plotting show
        # bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        # bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
        #                                     subplot=True)
        # bt.indicators.StochasticSlow(self.datas[0])
        # bt.indicators.MACDHisto(self.datas[0])
        # rsi = bt.indicators.RSI(self.datas[0])
        # bt.indicators.SmoothedMovingAverage(rsi, period=10)
        # bt.indicators.ATR(self.datas[0], plot=False)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm),
                         doprint=not HUANCE)

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm),
                         doprint=not HUANCE)
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f, ALLVALUE %.2f' %
                 (trade.pnl, trade.pnlcomm, self.broker.getvalue()), doprint=not HUANCE)
        self.trade_times += 1
        if trade.pnlcomm > 0:
            self.success_times += 1
        else:
            self.fail_times += 1
        if self.broker.getvalue() > self.max_value:
            self.max_value = self.broker.getvalue()
        if self.broker.getvalue() < self.min_value:
            self.min_value = self.broker.getvalue()

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > self.sma[0]:
                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            if self.dataclose[0] < self.sma[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

    def stop(self):
        self.log('(MA Period %2d) Ending Value %.2f 成功次数：%d, 失败次数：%d, 成功率：%.2f%%, 最高值：%.2f, 最低值：%.2f' %
                 (self.params.maperiod, self.broker.getvalue(), self.success_times, self.fail_times,
                  self.success_times / self.trade_times * 100, self.max_value, self.min_value), doprint=True)


def read_and_format_excel(file_path):
    # 先读取文件列名
    column_names = pd.read_excel(file_path, nrows=0).columns
    if '日期' in column_names:
        # 读取Excel文件，指定index_col为'日期'列，并解析日期
        df = pd.read_excel(file_path, index_col='日期', parse_dates=True)
    elif 'date' in column_names:
        df = pd.read_excel(file_path, index_col='date', parse_dates=True)
    else:
        raise ValueError("Excel文件没有包含日期(date)列")
    # 重命名列名
    if '开盘' in column_names:
        df.rename(columns={'开盘': 'open'}, inplace=True)
    if '收盘' in column_names:
        df.rename(columns={'收盘': 'close'}, inplace=True)
    if '最高' in column_names:
        df.rename(columns={'最高': 'high'}, inplace=True)
    if '最低' in column_names:
        df.rename(columns={'最低': 'low'}, inplace=True)
    if '成交量' in column_names:
        df.rename(columns={'成交量': 'volume'}, inplace=True)

    return df


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    if HUANCE:
        strats = cerebro.optstrategy(
            TestStrategy,
            maperiod=range(BEGIN_PERIOD, END_PERIOD))
    if not HUANCE:
        cerebro.addstrategy(TestStrategy, maperiod=MAPERIOD)

    # Create a Data Feed
    # stock_qfq_df = pd.read_excel("002338.xlsx", index_col='date', parse_dates=True)
    stock_qfq_df = read_and_format_excel(FILE_PATH)
    # start_date = datetime(2022, 3, 9)  # 回测开始时间
    # end_date = datetime(2025, 3, 7)  # 回测结束时间
    # data = bt.feeds.PandasData(dataname=stock_qfq_df, fromdate=start_date, todate=end_date)  # 加载数据
    data = bt.feeds.PandasData(dataname=stock_qfq_df, fromdate=START_DATE, todate=END_DATE)  # 加载数据

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(INIT_CASH)
    # 0.01% ... divide by 100 to remove the % 万一
    cerebro.broker.setcommission(commission=COMMISSION)
    # Set the sizer stake from the params
    # cerebro.addsizer(bt.sizers.FixedSize, stake=FIXED_STAKE)
    # cerebro.addsizer(bt.sizers.PercentSizer, percents=PERCENT_STAKE)
    cerebro.addsizer(bt.sizers.PercentSizerInt, percents=PERCENT_STAKE)
    # Print out the starting conditions
    # print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run(maxcpus=MAXCPUS)
    # Print out the final result
    # print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    if not HUANCE:
        cerebro.plot()
