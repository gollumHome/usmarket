# strategies.py
import yfinance as yf
import pandas as pd
from config import *


class Strategies:
    def fetch_price_data(self, tickers, period="2y"):
        """获取K线价格数据 (增加容错)"""
        try:
            # print(f"正在下载行情: {tickers}")
            # 增加 auto_adjust=True 和 multi_level_index=False 可以减少很多格式问题
            data = yf.download(tickers, period=period, progress=False, auto_adjust=True)

            if data.empty:
                print(f"❌ 警告: 下载数据为空! 请检查网络或股票代码: {tickers}")
                return pd.DataFrame()

            # 处理 yfinance 返回格式的差异
            # 如果是多只股票，直接返回 data (列名通常就是股票代码)
            # 如果包含 'Close' 且不是多级索引，直接返回
            if isinstance(data.columns, pd.MultiIndex):
                # 如果是多级索引，通常 level 0 是 'Close' 或 'Adj Close'
                # 尝试提取 Close 部分
                try:
                    if 'Close' in data.columns.get_level_values(0):
                        return data['Close']
                    elif 'Adj Close' in data.columns.get_level_values(0):
                        return data['Adj Close']
                except:
                    pass

            # 单层索引情况
            if 'Close' in data.columns:
                return data['Close']

            return data

        except Exception as e:
            print(f"❌ 数据下载发生异常: {e}")
            return pd.DataFrame()

    def analyze_macro(self, spy_series, vix_series):
        """
        计算宏观状态 (增加判空保护)
        """
        # === 核心修改：增加判空保护 ===
        if spy_series is None or spy_series.empty or len(spy_series) < 20:
            return {
                "status": "数据缺失",
                "advice": "无法获取大盘数据，请检查网络 (需科学上网)。",
                "spy_price": 0,
                "ma200": 0,
                "ma200_slope": 0,
                "vix": 0,
                "is_safe": False  # 强制不安全，停止扫描
            }

        # 确保 vix 也有数据，如果没有，给个默认值
        if vix_series is None or vix_series.empty:
            curr_vix = 20  # 默认给个中性值
        else:
            curr_vix = vix_series.iloc[-1]

        # === 原有逻辑 ===
        curr_price = spy_series.iloc[-1]

        # 计算 200 日均线
        ma200_series = spy_series.rolling(MA_LONG).mean()

        # 再次检查 MA200 是否计算成功 (数据不够长会导致全是 NaN)
        if pd.isna(ma200_series.iloc[-1]):
            return {
                "status": "数据不足",
                "advice": "历史数据不足200天，无法计算年线。",
                "spy_price": curr_price,
                "ma200": 0,
                "ma200_slope": 0,
                "vix": curr_vix,
                "is_safe": False
            }

        ma200_curr = ma200_series.iloc[-1]
        ma200_prev = ma200_series.iloc[-20]  # 20天前

        # 计算斜率
        slope = (ma200_curr - ma200_prev) / ma200_prev
        is_flat = abs(slope) < 0.005

        # 判定状态
        status = "未知"
        advice = "观望"
        is_safe = False

        if curr_price < ma200_curr:
            status = "🔴 熊市 (Bear)"
            advice = "趋势向下，严格防守，禁止开新仓。"
        elif is_flat:
            status = "⚪️ 滞涨/横盘 (Choppy)"
            advice = "均线走平，方向不明，谨防假突破。"
        elif curr_vix > 20:
            status = "🟡 震荡牛 (Volatile Bull)"
            advice = "趋势向上但波动剧烈，轻仓。"
            is_safe = True
        else:
            status = "🟢 强势牛 (Strong Bull)"
            advice = "趋势健康，积极参与。"
            is_safe = True

        return {
            "status": status,
            "advice": advice,
            "spy_price": curr_price,
            "ma200": ma200_curr,
            "ma200_slope": slope,
            "vix": curr_vix,
            "is_safe": is_safe
        }

    def rank_sectors(self, data_df):
        """板块动量排序 (判空保护)"""
        if data_df.empty:
            return [], []

        scores = {}
        for ticker in data_df.columns:
            try:
                series = data_df[ticker]
                # 剔除空值
                series = series.dropna()

                if len(series) < MOM_WINDOW_LONG: continue
                curr = series.iloc[-1]
                p_3m = series.iloc[-MOM_WINDOW_SHORT]
                p_6m = series.iloc[-MOM_WINDOW_LONG]
                score = ((curr / p_3m - 1) * 0.6) + ((curr / p_6m - 1) * 0.4)
                scores[ticker] = score
            except:
                continue
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:3], ranked[-3:]

    def check_breakout(self, series, volume_series=None):
        """
        多维度个股信号检测
        """
        if series is None or len(series) < 200: return None

        curr = series.iloc[-1]
        prev = series.iloc[-2]

        # 基础均线计算
        ma20 = series.rolling(20).mean().iloc[-1]
        ma50 = series.rolling(50).mean().iloc[-1]
        ma150 = series.rolling(150).mean().iloc[-1]
        ma200 = series.rolling(200).mean().iloc[-1]

        # 价格通道
        high_50d = series.rolling(50).max().shift(1).iloc[-1]
        high_250d = series.rolling(250).max().shift(1).iloc[-1]  # 一年新高

        # --- 信号判定逻辑 ---

        # 1. 经典突破 (刚刚跨越 50日/1年 高点)
        is_breakout_50d = (curr > high_50d) and (prev <= high_50d)
        is_breakout_1y = (curr > high_250d) and (prev <= high_250d)

        # 2. 动能持续 (已经突破，正在 50日高点上方强势运行)
        # 条件：价格在高点上方 0-5% 范围内，且均线多头排列
        is_momentum = (curr > high_50d) and (curr <= high_50d * 1.05) and (ma50 > ma200)

        # 3. 均线回踩 (牛股低吸点)
        # 条件：价格回落到 20日线附近，但整体趋势向上
        is_pullback = (abs(curr - ma20) / ma20 < 0.01) and (curr > ma200) and (ma50 > ma200)

        # --- 结果打包 ---
        res = {"price": curr}

        if is_breakout_1y:
            res["reason"] = "🔥 历史性突破：创一年新高"
            return res
        if is_breakout_50d:
            res["reason"] = "🚀 趋势突破：创50日新高"
            return res
        if is_momentum:
            res["reason"] = "💪 动能强劲：站稳高位运行"
            return res
        if is_pullback:
            res["reason"] = "🎯 缩量回踩：20日线支撑点"
            return res

        return None