# author : menglin.zhu
# date : 2026-05-11
# description ： 专门负责处理 data/raw 中的数据并生成技术指标

import pandas as pd
import os

def calculate_metrics(symbol):
    file_path = f"data/raw/{symbol}_daily.csv"
    if not os.path.exists(file_path):
        print(f"数据文件 {file_path} 不存在，请先运行 AlpacaDataHandler 获取数据。")
        return
    
    df = pd.read_csv(file_path, index_col=0, parse_dates=True)
    
    # 计算技术指标

    # SMA : 简单移动平均线(Simple Moving Average)
    """
        Simple → 简单：指每个数据点权重相同
        Moving → 移动：指随着时间滑动窗口不断更新
        Average → 平均值：取窗口内数值的算术平均
        所以 SMA 就是：用固定长度的窗口，计算过去一段时间价格的算术平均，随着时间移动而更新。
    """
    df['SMA_20'] = df['close'].rolling(window=20).mean()  # 20日简单移动平均线
    df['SMA_60'] = df['close'].rolling(window=60).mean()  # 60日简单移动平均线
    df['SMA_120'] = df['close'].rolling(window=120).mean()  # 120日简单移动平均线

    # RSI : 相对强弱指数(Relative Strength Index)
    """
        Relative → 相对：指与过去价格表现进行比较
        Strength → 强弱：指价格上涨和下跌的强度
        Index → 指数：指一个数值指标，通常在0到100之间
        所以 RSI 就是：通过比较一定时期内价格上涨和下跌的平均幅度，来衡量价格的相对强弱程度。
    """
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))  # RSI 计算公式   

    # 保存计算后的数据
    output_path = f"data/processed/{symbol}_indicators.csv"
    os.makedirs('data/processed', exist_ok=True)
    df.to_csv(output_path)
    print(f"技术指标已保存到 {output_path}")
    return df

if __name__ == "__main__":
    calculate_metrics("MU")