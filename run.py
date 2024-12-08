# app.py

from flask import Flask, request, jsonify
import pandas as pd
import os
import logging

from backtest.MovingAverageStrategy import MovingAverageStrategy
from backtest.BacktestSystem import BacktestSystem

from matplotlib import rcParams
rcParams['font.sans-serif'] = 'SimHei'  # 常用的中文字体，SimHei是黑体
rcParams['axes.unicode_minus'] = False  # 解决负号显示为乱码的问题

app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.DEBUG)

# 全局存储回测结果（注意：在生产环境中应使用更可靠的存储方式，如数据库）
backtest_result = None

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Backtest API is running."}), 200

@app.route('/post', methods=['POST'])
def run_backtest():
    global backtest_result
    try:
        req_data = request.get_json()
        start_date = req_data.get('start_date', '2023-01-01')
        end_date = req_data.get('end_date', '2023-12-31')
        stock_file = req_data.get('stock_file', '000001.csv') 
        short_window = req_data.get('short_window', 12)
        long_window = req_data.get('long_window', 26)
        initial_balance = req_data.get('initial_balance', 1000000)
        transaction_fee = req_data.get('transaction_fee', 0.0000)
        slippage = req_data.get('slippage', 0.0001)
        size=req_data.get('szie', 0.2)
        # 加载数据
        data_path = os.path.join('backtest',stock_file)
        if not os.path.exists(data_path):
            data_path = os.path.join(stock_file)
            if not os.path.exists(data_path):
                return jsonify({"error": "Stock data file not found."}), 400

        data = pd.read_csv(data_path)

        # 确保包含所需列: date, open, close
        if not all(col in data.columns for col in ['date','open','close']):
            return jsonify({"error": "Data missing required columns."}), 400

        # 按日期排序并重置索引
        data.sort_values('date', inplace=True)
        data.reset_index(drop=True, inplace=True)

        # 创建策略与回测系统实例
        strategy = MovingAverageStrategy(short_window=short_window, long_window=long_window)
        backtest_system = BacktestSystem(
            data=data,
            start_date=start_date,
            end_date=end_date,
            strategy=strategy,
            initial_balance=initial_balance,
            transaction_fee=transaction_fee,
            slippage=slippage
        )

        # 运行回测
        backtest_system.run_backtest(size=size)

        # 存储回测结果以便GET接口提取
        backtest_result = backtest_system.get_final_results()

        return jsonify({"message": "Backtest completed."}), 200
    except Exception as e:
        app.logger.error(f"Error in /post: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/get', methods=['GET'])
def get_results():
    global backtest_result
    if backtest_result is None:
        return jsonify({"error": "No backtest results available. Run /post first."}), 400
    # 如果 backtest_result 是 DataFrame，转换为字典
    if isinstance(backtest_result, pd.DataFrame):
        return backtest_result.to_dict(orient='records'), 200
    return jsonify(backtest_result), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
