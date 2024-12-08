# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 23:57:14 2024

@author: 24292
"""
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from matplotlib import rcParams
rcParams['font.sans-serif'] = 'SimHei'  # 常用的中文字体，SimHei是黑体
rcParams['axes.unicode_minus'] = False  # 解决负号显示为乱码的问题
class BacktestSystem:
    def __init__(self, data, strategy, start_date='2023-01-01',end_date='2023-12-31',initial_balance=1000000, transaction_fee=0.00, slippage=0.0001):
        # 检查并处理输入的 DataFrame
        if 'date' not in data.columns:
            raise ValueError("Input DataFrame must contain a 'date' column.")
        data.date=pd.to_datetime(data.date,format='%Y%m%d')
        data = data[(data['date'] >= start_date) & (data['date'] <= end_date)]
        # 删除重复的日期
        data = data.drop_duplicates(subset='date')
        
        # 按照日期排序
        data = data.sort_values(by='date')
        self.original_data = data.copy()
        self.strategy = strategy
        self.strategy_name = strategy.name
        self.initial_balance = initial_balance
        self.transaction_fee = transaction_fee
        self.slippage = slippage
        self.results = []
        self.trade_log = pd.DataFrame()
        
    def run_backtest(self, size=1):
        signals = self.strategy.generate_signals(self.original_data)
        self.data = pd.merge(self.original_data, signals, on='date', how='left')
        self.data['signal'] = self.data['signal'].fillna(0)
        
        # 生成下一天的开盘价
        self.data['next_open'] = self.data['open'].shift(-1)
        self.data['next_open'] = self.data['next_open'].fillna(self.data['close'])

        balance = self.initial_balance
        position = 0
        if self.data.empty:
            raise ValueError("Merged DataFrame is empty. Please check your input data and strategy.")
        trades = []
        last_date = self.data['date'].iloc[-1]

        for i, row in self.data.iterrows():
            signal = row['signal']
            price = row['next_open']  # 次日开盘价
            today_close = row['close']
            current_date = row['date']

            # 最后一天不交易
            if current_date == last_date and True:
                continue

            # 买卖限制逻辑
            can_buy = (price <= today_close * 1.099)
            can_sell = (price >= today_close * 0.901)

            # 计算当前总资产
            total_asset = balance + position * price

            if signal == 1 and can_buy:
                # 买入总资产的20%或最大现金
                buy_value = min( total_asset * size,balance)
                # 计算滑点和手续费后的买入价格
                buy_cost_per_share = price * (1 + self.slippage) * (1 + self.transaction_fee)
                # 能买到的股数（先不考虑100股整数限制）
                tentative_shares = int(buy_value // buy_cost_per_share)
                
                # 向下取整到100股整数倍
                buy_amount = (tentative_shares // 100) * 100

                if buy_amount > 0:
                    cost = buy_amount * price * (1 + self.slippage) * (1 + self.transaction_fee)
                    if cost <= balance:
                        fee = buy_amount * price * (1 + self.slippage) * self.transaction_fee
                        slip = buy_amount * price * self.slippage
                        traded_amount = buy_amount * price * (1 + self.slippage)

                        balance -= cost
                        position += buy_amount

                        trades.append({
                            'date': current_date,
                            'action': 'buy',
                            'price': price * (1 + self.slippage),
                            'amount': buy_amount,
                            'balance': balance,
                            'position': position,
                            'fee': fee,
                            'slippage': slip,
                            'traded_amount': traded_amount
                        })

            elif signal == -1 and position > 0 and can_sell:
                sell_value = min(total_asset * size,position*price)
                
                # 卖出当前总资产的20%，如果不足则全部持仓卖出
                
                if sell_value > 0:
                    sell_price = price * (1 - self.slippage)
                    sell_amount = (int(sell_value//sell_price ) // 100) * 100
                    base_revenue = sell_amount * sell_price
                    fee = base_revenue * self.transaction_fee
                    slip = sell_amount * price * self.slippage
                    revenue = base_revenue * (1 - self.transaction_fee)
                    
                    balance += revenue
                    position -= sell_amount

                    trades.append({
                        'date': current_date,
                        'action': 'sell',
                        'price': sell_price,
                        'amount': sell_amount,
                        'balance': balance,
                        'position': position,
                        'fee': fee,
                        'slippage': slip,
                        'traded_amount': base_revenue
                    })

            total_asset = balance + position * price
            self.results.append({
                'date': row['date'],
                'balance': balance,
                'position': position,
                'price': price,
                'total_asset': total_asset
            })

        # 最终结算
        final_price = self.data.iloc[-1]['close']
        total_asset = balance + position * final_price
        self.results.append({
            'date': self.data.iloc[-1]['date'],
            'balance': balance,
            'position': position,
            'price': final_price,
            'total_asset': total_asset
        })

        self.trade_log = pd.DataFrame(trades)
        self.results = pd.DataFrame(self.results)
        self.final_balance = total_asset

    def calculate_statistics(self):
        import math
        self.results['daily_return'] = self.results['total_asset'].pct_change().fillna(0)
        self.results['value'] = self.results['total_asset']/self.initial_balance

        total_days = len(self.results)
        first_trade_date = self.results.iloc[0]['date']
        last_trade_date = self.results.iloc[-1]['date']
        winning_days = (self.results['daily_return'] > 0).sum()
        losing_days = (self.results['daily_return'] < 0).sum()

        initial_capital = self.initial_balance
        final_capital = self.final_balance
        total_return = (final_capital - initial_capital) / initial_capital

        annualized_return = (1 + total_return) ** (250 / total_days) - 1 if total_days > 0 else 0

        rolling_max = self.results['total_asset'].cummax()
        drawdown = self.results['total_asset'] / rolling_max - 1
        max_drawdown = drawdown.min()
        max_drawdown_value = rolling_max.max() - rolling_max.max()*(1+max_drawdown)

        # 计算最长回撤天数
        dd_periods = 0
        max_dd_periods = 0
        for d in drawdown:
            if d < 0:
                dd_periods += 1
                if dd_periods > max_dd_periods:
                    max_dd_periods = dd_periods
            else:
                dd_periods = 0

        total_trades = len(self.trade_log)
        total_profit_loss = final_capital - initial_capital
        total_fee = self.trade_log['fee'].sum() if 'fee' in self.trade_log.columns else 0
        total_slippage = self.trade_log['slippage'].sum() if 'slippage' in self.trade_log.columns else 0
        total_traded_amount = self.trade_log['traded_amount'].sum() if 'traded_amount' in self.trade_log.columns else 0

        avg_daily_pnl = total_profit_loss / total_days if total_days > 0 else 0
        avg_daily_fee = total_fee / total_days if total_days > 0 else 0
        avg_daily_slippage = total_slippage / total_days if total_days > 0 else 0
        avg_daily_traded_amount = total_traded_amount / total_days if total_days > 0 else 0
        avg_daily_return = self.results['daily_return'].mean()
        return_std = self.results['daily_return'].std()
        sharpe_ratio = (avg_daily_return / return_std * np.sqrt(250)) if return_std != 0 else 0
        return_drawdown_ratio = total_return / abs(max_drawdown) if max_drawdown != 0 else math.inf

        benchmark_return = (self.data.iloc[-1]['close'] - self.data.iloc[0]['close']) / self.data.iloc[0]['close']

        print("首个交易日：", first_trade_date)
        print("最后交易日：", last_trade_date)
        print("总交易日：", total_days)
        print("盈利交易日：", winning_days)
        print("亏损交易日：", losing_days)
        print("起始资金：", initial_capital)
        print("结束资金：", final_capital)
        print("总收益率：{:.2%}".format(total_return))
        print("年化收益：{:.2%}".format(annualized_return))
        print("最大回撤：{:.2f}".format(max_drawdown_value))
        print("百分比最大回撤：{:.2%}".format(max_drawdown))
        print("最长回撤天数：", max_dd_periods)
        print("总盈亏：{:.2f}".format(total_profit_loss))
        print("总手续费：{:.2f}".format(total_fee))
        print("总滑点：{:.2f}".format(total_slippage))
        print("总成交金额：{:.2f}".format(total_traded_amount))
        print("总成交笔数：", total_trades)
        print("日均盈亏：{:.2f}".format(avg_daily_pnl))
        print("日均手续费：{:.2f}".format(avg_daily_fee))
        print("日均滑点：{:.2f}".format(avg_daily_slippage))
        print("日均成交金额：{:.2f}".format(avg_daily_traded_amount))
        print("日均收益率：{:.4f}".format(avg_daily_return))
        print("收益标准差：{:.4f}".format(return_std))
        print("Sharpe Ratio：{:.4f}".format(sharpe_ratio))
        print("收益回撤比：{:.4f}".format(return_drawdown_ratio))
        print("基准收益率：{:.2%}".format(benchmark_return))

        benchmark_value = self.data['close'] / self.data['close'].iloc[0]
        benchmark_return_line = benchmark_value*self.initial_balance

        sns.set(style="whitegrid")
        plt.figure(figsize=(12, 6))
        plt.plot(self.results['date'], self.results['value'], label=f'{self.strategy_name} Value', color='b')
        plt.plot(self.results['date'], benchmark_value, label='Benchmark Value', color='orange')
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value')
        plt.title(f'{self.strategy_name} Portfolio Value vs Benchmark Over Time')
        plt.legend()
        plt.show()

        excess_return=(self.results['total_asset'] - benchmark_return_line).fillna(0)/self.initial_balance
        plt.figure(figsize=(12, 6))
        plt.plot(self.results['date'], excess_return, label=f'{self.strategy_name} Cumulative Excess Return', color='g')
        plt.xlabel('Date')
        plt.ylabel('Cumulative Excess Return')
        plt.title('Cumulative Excess Returns Over Time')
        plt.legend()
        plt.show()

    def plot_results(self):
        plt.figure(figsize=(18, 9))
        plt.plot(self.results['date'], self.results['total_asset'], label='Total Asset')

        if not self.trade_log.empty:
            buys = self.trade_log[self.trade_log['action'] == 'buy']
            sells = self.trade_log[self.trade_log['action'] == 'sell']
            plt.scatter(buys['date'], buys['price']+10000, marker='^', color='g', label='Buy', s=100)
            plt.scatter(sells['date'], sells['price']+10000, marker='v', color='r', label='Sell', s=100)

        plt.title('Backtest Results')
        plt.xlabel('Date')
        plt.ylabel('Total Asset')
        plt.legend()
        plt.grid(False)
        plt.show()

    def print_trade_log(self):
        print("Trade Log:")
        print(self.trade_log)

    def print_final_balance(self):
        print(f"Final Balance: {self.final_balance:.2f}")

    def get_final_results(self):
        if len(self.results) > 0:
            initial_capital = self.initial_balance
            final_capital = self.final_balance
            total_return = (final_capital - initial_capital) / initial_capital
            trade_log=self.trade_log
            trade_log=trade_log.to_dict(orient='records')
            return {
                'total_return': total_return,
                'final_capital': final_capital,
                
                'trade_log' : trade_log
            }
        else:
            return {
                'total_return': None,
                'final_capital': None
            }


