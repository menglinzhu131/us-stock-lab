# author : menglin.zhu
# date : 2026-05-11
# description ： 编写回测脚本,直接利用 data/processed/ 目录下的数据，不需要重新下载。

import pandas as pd
import os

def run_backtest(symbol, hold_days=20):
    file_path = f'data/processed/{symbol}_indicators.csv'
    
    # 修改 index_col 为 1，因为 timestamp 在第二列
    df = pd.read_csv(file_path, index_col=1) 
    
    # 现在 index 拿到的就是 "2020-01-02..." 这种字符串了，转换就不会报错
    df.index = pd.to_datetime(df.index)
    
    # 删掉已经没用的 symbol 列，让 dataframe 只剩下数值，方便后面计算
    if 'symbol' in df.columns:
        df = df.drop(columns=['symbol'])

    df = df.sort_index()

    signals = []

    # 遍历数据找金叉点
    for i in range(1, len(df) - hold_days):
        prev_row = df.iloc[i-1]
        curr_row = df.iloc[i]
        # 金叉逻辑：SMA20 从下方穿过 SMA120
        if prev_row['SMA_20'] < prev_row['SMA_120'] and curr_row['SMA_20'] > curr_row['SMA_120']:
            buy_price = curr_row['close']
            sell_price = df.iloc[i + hold_days]['close']
            profit = (sell_price - buy_price) / buy_price

            signals.append({
                'Date': df.index[i].strftime('%Y-%m-%d'),
                'Buy_Price': round(buy_price, 2),
                'RSI_at_Buy': round(curr_row['RSI'], 2),
                'Profit_20d': f"{profit:.2%}"
            })

# 输出结果
    print(f"\n--- {symbol} 金叉策略回测 (持有{hold_days}天) ---")
    if not signals:
        print("在该时间段内未发现金叉信号。")
    else:
        results_df = pd.DataFrame(signals)
        print(results_df.to_string(index=False))
        
        # 计算胜率
        win_rate = len([s for s in signals if float(s['Profit_20d'].strip('%')) > 0]) / len(signals)
        print(f"\n策略统计: 信号次数: {len(signals)} | 胜率: {win_rate:.1%}")

if __name__ == "__main__":
    # 先测试关注的 AAPL 或 NVDA
    run_backtest("NVDA")
    run_backtest("MU")