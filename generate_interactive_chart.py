# author : menglin.zhu
# date : 2026-05-13
# description ：集成 Plotly 动态图表的交互式量化报告 (完整修复版)

import json
import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from tqdm import tqdm
from datetime import datetime, timedelta

# 注意：这里需要确保你的路径能找到这些自定义模块
from scripts.alpaca_fetcher import AlpacaDataHandler
from indicators.calculator import calculate_metrics

def load_config():
    """加载配置文件"""
    config_path = 'config.json'
    if not os.path.exists(config_path):
        return {"watchlist": ["AAPL", "NVDA", "TSLA"], "settings": {"history_days": 730}}
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_interactive_chart(df, symbol):
    # 确保索引是 DatetimeIndex
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    
    # 统一选取最近 120 个交易日的数据，避免 X 轴长度不一致
    df_plot = df.tail(120).copy() 

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05, row_heights=[0.7, 0.3])

    # 绘制 K 线
    fig.add_trace(go.Candlestick(
        x=df_plot.index, 
        open=df_plot['open'], high=df_plot['high'],
        low=df_plot['low'], close=df_plot['close'], 
        name='价格'
    ), row=1, col=1)

    # 3. 叠加 SMA 线条 (Row 1) - 全部改用 df_plot
    colors = {'SMA_20': '#00ff88', 'SMA_60': '#3498db', 'SMA_120': '#f1c40f'}
    for ma_name, color in colors.items():
        if ma_name in df_plot.columns:
            fig.add_trace(go.Scatter(
                x=df_plot.index, # 使用切片后的索引
                y=df_plot[ma_name], 
                mode='lines', 
                name=ma_name,
                line=dict(width=1.5, color=color)
            ), row=1, col=1)

    # 4. 副图：RSI (Row 2) - 改用 df_plot
    if 'RSI' in df_plot.columns:
        fig.add_trace(go.Scatter(
            x=df_plot.index, 
            y=df_plot['RSI'], 
            mode='lines', 
            name='RSI',
            line=dict(color='#e74c3c')
        ), row=2, col=1)
        
        # 增加 RSI 阈值线
        fig.add_hline(y=70, line_dash="dash", line_color="#ff4444", row=2, col=1, opacity=0.5)
        fig.add_hline(y=30, line_dash="dash", line_color="#00ff88", row=2, col=1, opacity=0.5)

    # 5. 关键布局修复
    fig.update_layout(
        template="plotly_dark",
        xaxis_type='date',           # 强制 X 轴识别为日期
        xaxis_rangeslider_visible=False, # 必须关闭，否则 K 线会因 rangeslider 再次挤压
        height=600,                  # 给定固定高度
        margin=dict(l=50, r=50, b=50, t=80),
        hovermode='x unified'        # 十字准星模式，方便查看数据
    )
    
    # 修复 X 轴自动缩放问题
    fig.update_xaxes(rangebreaks=[
        dict(bounds=["sat", "mon"]), # 隐藏周末，防止图表出现空白断层
    ])

    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def generate_full_report(table_rows, chart_map):
    """生成带有点选交互的完整 HTML 报告"""
    charts_html = ""
    for symbol, chart_div in chart_map.items():
        charts_html += f'<div id="chart-{symbol}" class="chart-container" style="display:none;">{chart_div}</div>'

    html_template = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Vibe Quant Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background-color: #121212; color: #e0e0e0; padding: 20px; }}
            h2 {{ color: #00ff88; text-shadow: 0 0 10px rgba(0,255,136,0.3); }}
            .main-container {{ display: flex; flex-direction: column; gap: 20px; }}
            table {{ width: 100%; border-collapse: collapse; background-color: #1e1e1e; border-radius: 8px; overflow: hidden; }}
            th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #333; }}
            th {{ background-color: #252525; color: #00ff88; }}
            tr {{ cursor: pointer; transition: 0.2s; }}
            tr:hover {{ background-color: #333; }}
            .buy {{ color: #00ff88; font-weight: bold; }}
            .sell {{ color: #ff4444; font-weight: bold; }}
            .neutral {{ color: #888; }}
            .chart-area {{ background-color: #1a1a1a; padding: 20px; border-radius: 8px; border: 1px solid #333; min-height: 600px; }}
            .hint {{ color: #00ff88; font-size: 0.9em; opacity: 0.8; }}
        </style>
        <script>
            function showChart(symbol) {{
                document.querySelectorAll('.chart-container').forEach(el => el.style.display = 'none');
                const target = document.getElementById('chart-' + symbol);
                if (target) {{
                    target.style.display = 'block';
                    // 触发 plotly 自适应大小
                    window.dispatchEvent(new Event('resize'));
                }}
                document.getElementById('chart-placeholder').style.display = 'none';
            }}
        </script>
    </head>
    <body>
        <h2>📈 交互式量化仪表盘 <span style="font-size:0.5em; color:#666;">v3.5 - menglin.zhu</span></h2>
        <div class="main-container">
            <p class="hint">🎯 点击下方表格行，即刻查看该标的动态 K 线与 RSI 走势</p>
            <table>
                <thead>
                    <tr><th>股票代码</th><th>建议信号</th><th>关键指标</th></tr>
                </thead>
                <tbody>
                    {" ".join(table_rows)}
                </tbody>
            </table>
            
            <div class="chart-area">
                <div id="chart-placeholder" style="text-align: center; padding-top: 200px; color: #444;">
                    <h3>点击上方列表唤起交互式图表</h3>
                </div>
                {charts_html}
            </div>
        </div>
    </body>
    </html>
    """
    with open("report.html", "w", encoding="utf-8") as f:
        f.write(html_template)

def main():
    config = load_config()
    watchlist = config["watchlist"]
    handler = AlpacaDataHandler()
    start_date = datetime.now() - timedelta(days=config.get("settings", {}).get("history_days", 730))
    
    report_rows = []
    chart_map = {}
    
    print(f"🚀 正在构建交互式终端，处理标的: {watchlist}")

    for symbol in tqdm(watchlist, desc="Processing"):
        try:
            # 1. 更新数据
            handler.get_bars(symbol, start_date)
            calculate_metrics(symbol)
            
            # 2. 读取数据
            target_path = f"data/processed/{symbol}_indicators.csv"
            df = pd.read_csv(target_path)
            # 显式转换 timestamp 列为日期格式
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            # 将真正的日期列设置为索引
            df.set_index('timestamp', inplace=True)
            # 确保按日期排序（修复绘图挤压的关键）
            df.sort_index(inplace=True)
            last = df.iloc[-1]
            
            # 3. 策略判断
            signal = "HOLD"
            css_class = "neutral"
            if last['SMA_20'] > last['SMA_120'] and 45 < last['RSI'] < 75:
                signal, css_class = "BUY", "buy"
            elif last['RSI'] > 75:
                signal, css_class = "SELL", "sell"
            
            # 4. 填充 HTML
            report_rows.append(f"""
                <tr onclick="showChart('{symbol}')">
                    <td><b>{symbol}</b></td>
                    <td class="{css_class}">{signal}</td>
                    <td>RSI: {last['RSI']:.1f} | SMA20: {last['SMA_20']:.2f}</td>
                </tr>
            """)
            
            chart_map[symbol] = generate_interactive_chart(df, symbol)
            
        except Exception as e:
            report_rows.append(f"<tr><td>{symbol}</td><td colspan='2' style='color:orange'>跳过: {e}</td></tr>")

    generate_full_report(report_rows, chart_map)
    print(f"\n✨ 任务完成！仪表盘已就绪: {os.path.abspath('report.html')}")

if __name__ == "__main__":
    main()