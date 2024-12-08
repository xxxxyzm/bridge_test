##策略
当12日的价格均线穿越26日的价格均线时买入。当价格跌破26均线时卖出。
##回测
这个回测系统 `BacktestSystem` 是一个用于评估交易策略的工具，它通过模拟交易过程来计算策略的性能指标。以下是对该系统中各个函数的介绍：
### 说明
- **数据要求**: 数据 DataFrame 必须包含 'date', 'open', 'close' 等列，并且日期格式形如 '20230101'。参考文件000001.csv
- **策略要求**: 策略对象必须有一个 `generate_signals` 方法，该方法返回包含信号的 DataFrame，信号列名为 'signal'。
- **交易规则**:
  - 策略使用收盘价给出信号，因此采用第二天开盘价成交
  - 如果第二天开盘涨停或者跌停（波动超过9.9%），则无法进行买入或卖出。
  - 交易数量向下取整到100股的整数倍。
  - 买入和卖出时考虑滑点和手续费。
  - 因为采用第二天开盘价成交，所以最后一天不进行交易。
### 1. `__init__` 方法
- **功能**: 初始化回测系统。
- **参数**:
  - `data`: 包含历史交易数据的 DataFrame，必须包含 'date', 'open', 'close' 等列。
  - `strategy`: 策略对象，包含生成交易信号的方法 `generate_signals`。
  - `start_date`, `end_date`: 回测的时间范围。
  - `initial_balance`: 初始资金。
  - `transaction_fee`: 交易手续费比例。
  - `slippage`: 滑点比例。
  -  `size`: 成交仓位比例，默认为1，全仓。
- **操作**:
  - 检查并处理输入数据，确保数据在指定的时间范围内，并按日期排序。
  - 初始化回测结果和交易日志的存储变量。

### 2. `run_backtest` 方法
- **功能**: 执行回测过程。
- **参数**:
  - `size`: 交易时使用的资金比例，默认为1（即全仓交易）。
- **操作**:
  - 生成交易信号，并将其合并到原始数据中。
  - 计算下一天的开盘价，用于模拟交易价格。
  - 初始化资金和仓位。
  - 遍历数据，根据信号进行买卖操作，计算交易成本（包括手续费和滑点），并更新资金和仓位。
  - 记录每一步的总资产和交易日志。
  - 最终结算，计算并记录最终总资产。

### 3. `calculate_statistics` 方法
- **功能**: 计算并输出回测结果的统计指标。
- **操作**:
  - 计算每日收益率、累计收益、年化收益率、最大回撤、夏普比率等指标。
  - 输出统计指标，包括交易日范围、总交易日、盈利交易日、亏损交易日、总收益率、年化收益率、最大回撤、最长回撤天数等。
  - 绘制资产变化图和超额收益图。

### 4. `plot_results` 方法
- **功能**: 绘制回测结果的图表。
- **操作**:
  - 绘制总资产的变化曲线。
  - 在图表上标记买入和卖出的交易点。
  - 显示图表。

### 5. `print_trade_log` 方法
- **功能**: 打印交易日志。
- **操作**:
  - 输出交易日志 DataFrame，包含每次交易的日期、动作、价格、数量、资金、仓位、手续费、滑点和成交金额。

### 6. `print_final_balance` 方法
- **功能**: 打印最终资金余额。
- **操作**:
  - 输出最终的总资产。

### 7. `get_final_results` 方法
- **功能**: 获取最终回测结果。
- **操作**:
  - 返回一个字典，包含总收益率、最终资金和交易日志的记录。


### 说明
- **数据要求**: 数据 DataFrame 必须包含 'date', 'open', 'close' 等列，并且日期格式必须是字符串格式，例如 '2023-01-01'。
- **策略要求**: 策略对象必须有一个 `generate_signals` 方法，该方法返回包含信号的 DataFrame，信号列名为 'signal'。
- **交易规则**: 
  - 买入和卖出时考虑滑点和手续费。
  - 交易数量向下取整到100股的整数倍。
  - 最后一天不进行交易。

这个回测系统可以帮助你评估交易策略的性能，通过模拟真实的交易环境，计算出策略的收益、风险和其他重要指标。
## 在 PowerShell 中使用 API 的说明

以下是在 PowerShell 中调用 Flask API 的步骤和示例。

### 1. 发送 POST 请求运行回测

#### 步骤:

1. **准备请求体数据**: 包含回测参数的 JSON 对象。
2. **发送 POST 请求**: 使用 `Invoke-RestMethod` 发送请求到 `/post` 端点。
3. **处理响应**: 检查响应消息。

#### 示例脚本:

```powershell
# 定义请求体参数
$param = @{
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    stock_file = "000001.csv"
    short_window = 12
    long_window = 26
    initial_balance = 1000000
    transaction_fee = 0.000
    slippage = 0.0001
    size = 0.2
}

# 将参数转换为 JSON 格式
$body = $param | ConvertTo-Json

# 发送 POST 请求

$response = Invoke-RestMethod -Uri http://127.0.0.1:5001/post `
>>                                -Method POST `
>>                                -ContentType "application/json" `
>>                                -Body $body
# 输出响应
$response
```

### 2. 发送 GET 请求获取回测结果

#### 步骤:

1. **发送 GET 请求**: 使用 `Invoke-RestMethod` 发送请求到 `/get` 端点。
```powershell
# 发送 POST 请求
 $response = Invoke-RestMethod -Uri http://127.0.0.1:5001/post `
>>                                -Method POST `
>>                                -ContentType "application/json" `
>>                                -Body $body
```
3. **处理响应**: 解析并显示回测结果。

#### 示例脚本:

```powershell
# 发送 GET 请求
 $results = Invoke-RestMethod -Uri http://127.0.0.1:5001/get -Method GET
```

### 3. 确保 API 服务器正在运行

在运行上述脚本之前，确保 Flask 应用在另一终端窗口中运行：

```bash
python run.py
```

### 4.如果一切顺利，应该返回如下结果
```
{
    "final_capital": 996942.6127,
    "total_return": -0.003057387299999944,
    "trade_log": [
        {
            "action": "buy",
            "amount": 15600,
            "balance": 800300.032,
            "date": "Mon, 15 May 2023 00:00:00 GMT",
            "fee": 0,
            "position": 15600,
            "price": 12.80128,
            "slippage": 19.968,
            "traded_amount": 199699.968
        },
        {
            "action": "sell",
            "amount": 15600,
            "balance": 996528.4072,
            "date": "Tue, 16 May 2023 00:00:00 GMT",
            "fee": 0,
            "position": 0,
            "price": 12.578742,
            "slippage": 19.6248,
            "traded_amount": 196228.3752
        },
        {
            "action": "buy",
            "amount": 17100,
            "balance": 797293.4857000001,
            "date": "Tue, 25 Jul 2023 00:00:00 GMT",
            "fee": 0,
            "position": 17100,
            "price": 11.651165,
            "slippage": 19.9215,
            "traded_amount": 199234.9215
        },
        {
            "action": "sell",
            "amount": 17000,
            "balance": 996003.6127,
            "date": "Mon, 14 Aug 2023 00:00:00 GMT",
            "fee": 0,
            "position": 100,
            "price": 11.688831,
            "slippage": 19.873,
            "traded_amount": 198710.127
        }
    ]
}
```
