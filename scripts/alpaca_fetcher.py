# author : menglin.zhu
# date : 2026-05-11
# description ： Alpaca 抓取数据并存入 data/raw/

import os
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.enums import Adjustment
from datetime import datetime
from dotenv import load_dotenv

# 加载配置
load_dotenv()

class AlpacaDataHandler:
    def __init__(self):
        self.client = StockHistoricalDataClient(
            os.getenv('ALPACA_API_KEY'), 
            os.getenv('ALPACA_SECRET_KEY')
        )
        print(f"API Key loaded: {os.getenv('ALPACA_API_KEY')[:5]}****")
    
    def get_bars(self, symbol, start_date):
        # 使用 Alpaca 的官方 Python SDK (alpaca-py) 获取股票历史“K线”（Bars）数据的核心逻辑
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=start_date,
            adjustment=Adjustment.ALL
        )
        bars = self.client.get_stock_bars(request_params)
        df = bars.df
        # 确保目录存在并保存
        os.makedirs('data/raw', exist_ok=True)
        file_path = f"data/raw/{symbol}_daily.csv"        
        df.to_csv(file_path)
        print(f"数据已保存到 data/raw/{symbol}_bars.csv")
        return df
    
if __name__ == "__main__":
    handler = AlpacaDataHandler()
    # 获取 MU 从 2020-01-01 开始的日线数据
    handler.get_bars("MU", "2020-01-01")

