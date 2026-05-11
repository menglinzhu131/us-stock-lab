# author : menglin.zhu
# date : 2026-05-11
# description ： 依次调用之前写的获取、计算和扫描模块。支持批量输入股票代码

import json
import os
import sys
from scripts.alpaca_fetcher import AlpacaDataHandler
from indicators.calculator import calculate_metrics
from strategies.golden_cross_scanner import scan_strategies
from datetime import datetime, timedelta

def load_config():
    config_path = 'config.json'
    # 如果文件不存在，提供一个默认配置
    if not os.path.exists(config_path):
        return {"watchlist": ["AAPL"], "settings": {"history_days": 730}}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)
    
def main():
    # 1.定义要处理的股票列表
    config = load_config()
    watchlist = config["watchlist"]
    
    print(f"🚀 开始自动化扫描流程... 标的: {watchlist}")

    # 初始化 Alpaca 客户端
    handler = AlpacaDataHandler()
    
    # 设置获取历史数据的起点（建议获取2年，确保120日均线计算准确）
    start_date = datetime.now() - timedelta(days=730)

    for symbol in watchlist:
        try:
            print(f"\n[1/3]正在获取{symbol}的原始数据...")
            handler.get_bars(symbol, start_date)

            print(f"[2/3]正在计算{symbol}的技术指标...")
            calculate_metrics(symbol)
        except Exception as e:
            print(f"⚠️ 处理 {symbol} 时发生错误: {e}")

    # 3. 执行最终扫描
    print("\n[3/3] 正在生成策略扫描报告...")
    print("-" * 50)
    scan_strategies()
    print("-" * 50)
    print("✅ 所有任务已完成。")

if __name__ == "__main__":
    main()