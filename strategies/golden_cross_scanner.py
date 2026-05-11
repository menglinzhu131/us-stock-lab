# author : menglin.zhu
# date : 2026-05-11
# description ： 专门负责处理 data/raw 中的数据并生成技术指标

import pandas as pd
import os
from datetime import datetime

def scan_strategies():
    processed_dir = "data/processed"
    if not os.path.exists(processed_dir):
        print(f"数据目录 {processed_dir} 不存在，请先运行指标计算器生成技术指标。")
        return
    
    print(f"--- 策略扫描启动 (基准日期: {datetime.now().strftime('%Y-%m-%d')}) ---")
    
    results = []

    # 遍历 processed 文件夹下所有的 CSV 文件
    for file_name in os.listdir(processed_dir):
        if file_name.endswith('_indicators.csv'):
            symbol = file_name.split('_')[0]
            df = pd.read_csv(os.path.join(processed_dir, file_name), index_col=0, parse_dates=True)
            
            if len(df) < 2: continue
            
            # 获取最近两行数据
            last_row = df.iloc[-1]
            prev_row = df.iloc[-2]

            # --- 逻辑 A: 检测金叉 (Golden Cross) ---
            # 条件：前一天 20 < 120，且今天 20 > 120
            is_golden_cross = (prev_row['SMA_20'] < prev_row['SMA_120']) and \
                              (last_row['SMA_20'] > last_row['SMA_120'])
            # --- 逻辑 B: 检测多头排列 (Bullish Alignment) ---
            is_bullish = last_row['SMA_20'] > last_row['SMA_60'] > last_row['SMA_120']
            
            results.append({
                'Symbol': symbol,
                'Price': round(last_row['close'], 2),
                'RSI': round(last_row['RSI'], 2),
                'Golden Cross': "★" if is_golden_cross else "",
                'Bullish': "√" if is_bullish else ""
            })

            # 打印结果表格
    scan_df = pd.DataFrame(results)
    print(scan_df.to_string(index=False))

if __name__ == "__main__":
    scan_strategies()