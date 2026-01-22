import pprint

from colorama import Fore, Style, init
from config import *
from data_feed import DataFeed
from ai_analyst import GeminiAnalyst
from notifier import WechatNotifier
from strategies import Strategies
import os

# 设置代理，解决 yfinance 连不上的问题
os.environ["http_proxy"] = "http://127.0.0.1:10809"
os.environ["https_proxy"] = "http://127.0.0.1:10809"

# 初始化
init(autoreset=True)
feed = DataFeed()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_URL = os.getenv("WECHAT_WEBHOOK")
logic = Strategies()
pp = pprint.PrettyPrinter(indent=4) # 初始化打印器

def print_header(text):
    print(f"\n{Style.BRIGHT}{'='*40}")
    print(f"{text.center(40)}")
    print(f"{'='*40}{Style.RESET_ALL}")

def print_debug(name, data):
    print(f"\n{Fore.YELLOW}------ [DEBUG: {name}] ------{Style.RESET_ALL}")
    pp.pprint(data)
    print(f"{Fore.YELLOW}--------------------------------{Style.RESET_ALL}\n")



def run():
    if not GEMINI_API_KEY or not WEBHOOK_URL:
        print("❌ 错误: 环境变量 GEMINI_API_KEY 或 WECHAT_WEBHOOK 未配置")
        return
    print("⏳ 系统启动，正在扫描市场数据...")
    notifier = WechatNotifier(WECHAT_WEBHOOK)
    # === 1. 宏观分析 (Macro) ===
    # 获取价格数据
    macro_prices = logic.fetch_price_data([BENCHMARK, RISK_INDICATOR])


    # 计算宏观状态
    macro_data = logic.analyze_macro(
        macro_prices[BENCHMARK],
        macro_prices[RISK_INDICATOR]
    )
    # 🐞 DEBUG 打印 1: 宏观数据
    print_debug("macro_data", macro_data)

    # === 2. 板块分析 (Sector) ===
    sector_prices = logic.fetch_price_data(SECTOR_POOL, period="1y")
    top_sectors, bottom_sectors = logic.rank_sectors(sector_prices)
    # 🐞 DEBUG 打印 2: 板块数据
    print_debug("top_sectors", top_sectors)
    print_debug("bottom_sectors", bottom_sectors)

    # === 3. AI 生成早报 (调用你指定的 generate_market_brief) ===
    print(f"{Fore.CYAN}🤖 正在生成市场早报...")
    # 这里直接传入 macro_data 字典，里面的 key 完美匹配 prompt
    market_report = analyst.generate_market_brief(macro_data, top_sectors, bottom_sectors)
    # 发送第一份报告
    notifier.send_markdown("🌍 PART 1: 市场早报", market_report)
    # === 4. 个股扫描 (Stock Scan) ===
    breakout_list = []

    if macro_data['is_safe']:
        # 获取字典里所有的代码 (list)
        all_tickers = list(WATCHLIST.keys())
        print(f"⏳ 市场环境安全，开始扫描 {len(all_tickers)} 只个股...")

        # 批量获取价格
        stock_prices = logic.fetch_price_data(all_tickers, period="1y")

        # 遍历字典：同时获得代码(ticker)和板块标签(sector_desc)
        for ticker, sector_desc in WATCHLIST.items():
            signal = None
            try:
                # 提取该股票的时间序列
                if ticker not in stock_prices.columns:
                    continue
                series = stock_prices[ticker].dropna()
                if series.empty:
                    continue

                # 检查突破
                signal = logic.check_breakout(series)
            except Exception as e:
                print(f"⚠️ 计算 {ticker} 出错: {e}")
                continue

            # 如果发现突破，获取辅助信息
            if signal:
                print(f"{Fore.GREEN}🔥 捕获突破: {ticker} [{sector_desc}]")

                news_text = "未找到近期重大新闻"
                insider_text = "近期无重大内部人交易"

                try:
                    news_text = feed.get_stock_news(ticker)
                except:
                    pass

                try:
                    insider_text = feed.get_insider_transactions(ticker)
                except:
                    pass

                # 🚀 重点：把 sector_desc 传给列表，供 AI 使用
                breakout_list.append({
                    "symbol": ticker,
                    "price": signal['price'],
                    "reason": signal['reason'],
                    "sector": sector_desc,
                    "news": news_text,
                    "insider": insider_text
                })
    else:
        print(f"{Fore.RED}⛔ 市场环境危险，跳过个股扫描。")

    # === 5. AI 生成点评 ===
    if breakout_list:
        top_10_breakouts = breakout_list[:10]

        print(f"🤖 正在分析前 {len(top_10_breakouts)} 只标的...")
        stock_reviews = analyst.generate_stock_reviews(top_10_breakouts)
        # 发送第二份报告
        notifier.send_markdown("🔭 PART 2: 机会雷达", stock_reviews)
    else:
        notifier.send_markdown("🔭 PART 2: 机会雷达", "今日市场无符合条件的突破标的。")

    print("🏁 所有任务处理完毕")


if __name__ == "__main__":
    run()