# author : menglin.zhu
# date : 2026-05-11
# description ： 编写回测脚本,直接利用 data/processed/ 目录下的数据，不需要重新下载。

import pandas as pd
import os

def run_backtest_v2(symbol):
    file_path = f'data/processed/{symbol}_indicators.csv'
    if not os.path.exists(file_path):
        return

    # 读取并处理日期
    df = pd.read_csv(file_path, index_col=1)
    df.index = pd.to_datetime(df.index)
    if 'symbol' in df.columns:
        df = df.drop(columns=['symbol'])
    df = df.sort_index()

    trades = []
    in_position = False
    buy_date = None
    buy_price = 0

    for i in range(1, len(df)):
        curr_date = df.index[i]
        curr_row = df.iloc[i]
        prev_row = df.iloc[i-1]

        # --- 入场逻辑：金叉 ---
        if not in_position:
            if prev_row['SMA_20'] < prev_row['SMA_120'] and curr_row['SMA_20'] > prev_row['SMA_120']:
                in_position = True
                buy_date = curr_date
                buy_price = curr_row['close']
                rsi_at_buy = curr_row['RSI']
        
        # --- 出场逻辑：跌破 SMA 20 ---
        else:
            if curr_row['close'] < curr_row['SMA_20']:
                sell_price = curr_row['close']
                profit = (sell_price - buy_price) / buy_price
                duration = (curr_date - buy_date).days
                
                trades.append({
                    'Buy_Date': buy_date.strftime('%Y-%m-%d'),
                    'Sell_Date': curr_date.strftime('%Y-%m-%d'),
                    'Days': duration,
                    'Profit': f"{profit:.2%}",
                    'RSI_Buy': round(rsi_at_buy, 2)
                })
                in_position = False

    # 打印回测报告
    print(f"\n==== {symbol} 动态止损策略回测 (出场条件: 跌破 SMA 20) ====")
    if not trades:
        print("未发现交易信号")
    else:
        results_df = pd.DataFrame(trades)
        print(results_df.to_string(index=False))
        
    # 统计
    # 修改统计部分的计算逻辑
    profits = [float(t['Profit'].strip('%')) for t in trades]
    avg_profit = sum(profits) / len(profits)
    # 打印时只需要加一个 % 符号
    win_rate = len([p for p in profits if p > 0]) / len(profits)
    print(f"\n[统计] 交易次数: {len(trades)} | 胜率: {win_rate:.1%} | 平均收益: {avg_profit:.2%}%")        
    
if __name__ == "__main__":
    for s in ["NVDA", "MU", "AAPL"]:
        run_backtest_v2(s)