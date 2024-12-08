# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 21:16:27 2024

@author: 24292
"""
import numpy as np
   
class MovingAverageStrategy:
    def __init__(self, short_window=12, long_window=26):
        self.short_window = short_window
        self.long_window = long_window
        self.name = f'MovingAverage ({self.short_window},{self.long_window})'
        
    def generate_signals(self, data):
        data = data.copy()
        data['ma_short'] = data['close'].rolling(window=self.short_window).mean()
        data['ma_long'] = data['close'].rolling(window=self.long_window).mean()

        # 生成买入信号：短期均线向上突破长期均线
        data['signal'] = 0
        data['signal'] = np.where((data['ma_short'] > data['ma_long']) & (data['ma_short'].shift(1) <= data['ma_long'].shift(1)), 1, data['signal'])

        # 生成卖出信号：价格跌破长期均线
        data['signal'] = np.where((data['close'] < data['ma_long']) & (data['close'].shift(1) >= data['ma_long'].shift(1)), -1, data['signal'])

        # 去除连续相同信号，只保留第一次出现的信号
        #data['signal'] = np.where(data['signal'] != data['signal'].shift(), data['signal'], 0)
        #data['signal'] = 1
        return data[['date', 'signal']]
        #return data