# author : menglin.zhu
# date : 2026-05-11
# description ： 自动读取处理过的 data/processed/AAPL_indicators.csv 并生成图表。

import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_stock_analysis(symbol):
    # 1. 读取处理后的数据
    file_path = f"data/processed/{symbol}_indicators.csv"
    if not os.path.exists(file_path):
        print(f"数据文件 {file_path} 不存在，请先运行 calculate_metrics 生成技术指标。")
        return
    # 核心修复：手动指定索引列和解析日期
    # index_col=1 对应的是 timestamp 这一列
    df = pd.read_csv(file_path, index_col=1, parse_dates=True)
    
    # 如果 DataFrame 里还有 symbol 这一列，删掉它避免干扰绘图
    if 'symbol' in df.columns:
        df = df.drop(columns=['symbol'])
    
    # 按照时间排序，确保连线不会乱跳
    df = df.sort_index()
    plot_df = df.tail(504)    # 只取最后 252 个交易日（大约一年）

    plt.figure(figsize=(14, 10))

    # 2. 创建画布 (包含两个子图：上方画价格，下方画 RSI)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True, 
                                   gridspec_kw={'height_ratios': [3, 1]})

    # --- 上图：价格与均线 ---
    ax1.plot(plot_df.index, plot_df['close'], label='Close Price', color='black', alpha=0.6)
    ax1.plot(plot_df.index, plot_df['close'].rolling(20).mean(), label='SMA 20', color='blue', linestyle='--')
    ax1.plot(plot_df.index, plot_df['close'].rolling(60).mean(), label='SMA 60', color='orange')
    ax1.plot(plot_df.index, plot_df['close'].rolling(120).mean(), label='SMA 120', color='red')
    
    ax1.set_title(f'{symbol} Stock Price & Moving Averages')
    ax1.set_ylabel('Price (USD)')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)

    # --- 下图：RSI 指标 ---
    ax2.plot(plot_df.index, plot_df['RSI'], label='RSI (14)', color='purple')
    
    # 绘制 RSI 的警戒线
    ax2.axhline(70, color='red', linestyle='--', alpha=0.5) # 超买
    ax2.axhline(30, color='green', linestyle='--', alpha=0.5) # 超卖
    
    ax2.set_title('Relative Strength Index (RSI)')
    ax2.set_ylabel('RSI Value')
    ax2.set_ylim(0, 100)
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)

    # 3. 布局优化调整
    plt.tight_layout()
    
    # 4. 保存图表并展示
    output_img = f'analysis/{symbol}_analysis.png'
    plt.savefig(output_img)
    print(f"图表已保存至: {output_img}")

if __name__ == "__main__":
    plot_stock_analysis("MCD")