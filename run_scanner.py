# author : menglin.zhu
# date : 2026-05-13
# description ： 基于实际 data/processed/*.csv 路径生成的自动化扫描器

import json
import os
import pandas as pd
from tqdm import tqdm
from datetime import datetime, timedelta
from scripts.alpaca_fetcher import AlpacaDataHandler
from indicators.calculator import calculate_metrics
import webbrowser

def load_config():
    config_path = 'config.json'
    if not os.path.exists(config_path):
        # 默认监控你截图中的三个股票
        return {"watchlist": ["AAPL", "NVDA", "TSLA"], "settings": {"history_days": 730}}
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_html_report(results):
    html_template = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background-color: #121212; color: #e0e0e0; padding: 30px; }}
            h2 {{ color: #00ff88; border-left: 5px solid #00ff88; padding-left: 15px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background-color: #1e1e1e; box-shadow: 0 4px 8px rgba(0,0,0,0.5); }}
            th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #333; }}
            th {{ background-color: #252525; color: #00ff88; text-transform: uppercase; letter-spacing: 1px; }}
            tr:hover {{ background-color: #2a2a2a; }}
            .buy {{ color: #00ff88; font-weight: bold; }}
            .sell {{ color: #ff4444; font-weight: bold; }}
            .neutral {{ color: #888; }}
            .reason {{ font-size: 0.9em; color: #bbb; }}
        </style>
    </head>
    <body>
        <h2>📈 每日量化策略扫描报告 ({datetime.now().strftime('%Y-%m-%d')})</h2>
        <table>
            <tr>
                <th>代码</th>
                <th>建议信号</th>
                <th>详细理由 (RSI & SMA Filter)</th>
            </tr>
            {" ".join(results)}
        </table>
        <footer style="margin-top: 30px; font-size: 0.8em; color: #666;">
            数据源: Alpaca Markets | 处理引擎: us-stock-lab v3
        </footer>
    </body>
    </html>
    """
    with open("report.html", "w", encoding="utf-8") as f:
        f.write(html_template)

def main():
    config = load_config()
    watchlist = config["watchlist"]
    
    print(f"🚀 正在启动 Vibe 扫描器... 目标列表: {watchlist}")
    
    handler = AlpacaDataHandler()
    start_date = datetime.now() - timedelta(days=config.get("settings", {}).get("history_days", 730))
    report_rows = []
    
    # 使用 tqdm 显示扫描进度
    for symbol in tqdm(watchlist, desc="市场扫描中", bar_format="{l_bar}{bar:20}{r_bar}"):
        try:
            # 1. 获取并保存到 data/raw/{symbol}_daily.csv
            handler.get_bars(symbol, start_date)
            
            # 2. 读取 raw 计算并保存到 data/processed/{symbol}_indicators.csv
            calculate_metrics(symbol)
            
            # 3. 核心：精准读取处理后的指标文件
            target_path = f"data/processed/{symbol}_indicators.csv"
            
            if os.path.exists(target_path):
                df = pd.read_csv(target_path)
                last_row = df.iloc[-1]
                
                rsi = last_row['RSI']
                sma20 = last_row['SMA_20']
                sma120 = last_row['SMA_120']
                
                signal = "HOLD"
                css_class = "neutral"
                reason = "未满足 V3 策略入场或出场条件。"

                # 策略 Vibe 逻辑
                if sma20 > sma120 and 45 < rsi < 75:
                    signal = "BUY"
                    css_class = "buy"
                    reason = f"均线多头 (SMA20 > SMA120) 且 RSI ({rsi:.1f}) 处于 45-75 强势区间。"
                elif rsi > 75:
                    signal = "SELL"
                    css_class = "sell"
                    reason = f"RSI ({rsi:.1f}) 触发超买报警 (高于 75)，建议获利了结。"
                elif rsi < 30:
                    signal = "WATCH"
                    css_class = "neutral"
                    reason = f"RSI ({rsi:.1f}) 极度超跌，进入观察区，等待均线走平。"

                report_rows.append(f"""
                    <tr>
                        <td><b>{symbol}</b></td>
                        <td class="{css_class}">{signal}</td>
                        <td class="reason">{reason}</td>
                    </tr>
                """)
            else:
                report_rows.append(f"<tr><td>{symbol}</td><td colspan='2'>❌ 指标文件丢失</td></tr>")
                
        except Exception as e:
            report_rows.append(f"<tr><td>{symbol}</td><td colspan='2'>⚠️ 错误: {str(e)}</td></tr>")

    # 4. 生成 HTML
    generate_html_report(report_rows)
    print(f"\n✨ 报告生成成功: {os.path.abspath('report.html')}")
    webbrowser.open('file://' + os.path.realpath('report.html'))

if __name__ == "__main__":
    main()