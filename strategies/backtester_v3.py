import pandas as pd
import os

def run_backtest_v3(symbol):
    file_path = f'data/processed/{symbol}_indicators.csv'
    if not os.path.exists(file_path):
        return

    df = pd.read_csv(file_path, index_col=1)
    df.index = pd.to_datetime(df.index)
    if 'symbol' in df.columns:
        df = df.drop(columns=['symbol'])
    df = df.sort_index()

    trades = []
    in_position = False
    buy_date = None
    buy_price = 0
    rsi_at_buy = 0

    # 策略参数
    RSI_MAX = 75  # 强力过滤：超过75绝对不买
    RSI_MIN = 45  # 强度过滤：低于45说明动能不足

    for i in range(1, len(df)):
        curr_date = df.index[i]
        curr_row = df.iloc[i]
        prev_row = df.iloc[i-1]

        if not in_position:
            # 基础逻辑：金叉
            is_golden_cross = prev_row['SMA_20'] < prev_row['SMA_120'] and curr_row['SMA_20'] > curr_row['SMA_120']
            
            # 过滤逻辑：RSI 必须在 45-75 之间
            is_rsi_healthy = RSI_MIN <= curr_row['RSI'] <= RSI_MAX
            
            if is_golden_cross and is_rsi_healthy:
                in_position = True
                buy_date = curr_date
                buy_price = curr_row['close']
                rsi_at_buy = curr_row['RSI']
        
        else:
            # 出场逻辑：收盘价跌破 SMA 20
            if curr_row['close'] < curr_row['SMA_20']:
                sell_price = curr_row['close']
                profit = (sell_price - buy_price) / buy_price
                duration = (curr_date - buy_date).days
                
                trades.append({
                    'Buy_Date': buy_date.strftime('%Y-%m-%d'),
                    'Sell_Date': curr_date.strftime('%Y-%m-%d'),
                    'Days': duration,
                    'Profit': profit, # 这里存小数，打印时再处理
                    'RSI_Buy': round(rsi_at_buy, 2)
                })
                in_position = False

    print(f"\n==== {symbol} V3 强力过滤策略 (RSI 45-75 + SMA20止损) ====")
    if not trades:
        print("未发现符合过滤条件的交易信号")
    else:
        results_df = pd.DataFrame(trades)
        # 格式化打印
        results_df['Profit'] = results_df['Profit'].apply(lambda x: f"{x:.2%}")
        print(results_df.to_string(index=False))
        
        # 统计修复
        profits = [t['Profit'] for t in trades]
        win_rate = len([p for p in profits if p > 0]) / len(profits)
        avg_profit = sum(profits) / len(profits)
        print(f"\n[统计] 交易次数: {len(trades)} | 胜率: {win_rate:.1%} | 平均收益: {avg_profit:.2%}")

if __name__ == "__main__":
    for s in ["NVDA", "MU", "AAPL"]:
        run_backtest_v3(s)