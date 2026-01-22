import yfinance as yf
import pandas as pd

class DataFeed:
    def __init__(self):
        pass

    def get_stock_news(self, symbol):
        """获取新闻 (增加容错和调试)"""
        try:
            ticker = yf.Ticker(symbol)
            news_list = ticker.news

            if not news_list:
                return "暂无最新新闻数据"

            formatted_news = []
            for item in news_list[:3]:  # 只取前3条，省Token
                # 尝试不同的键名 (yfinance 不同版本返回的 key 可能不同)
                title = item.get('title') or item.get('content', {}).get('title')

                if title:
                    formatted_news.append(f"- {title}")
                else:
                    # 如果拿不到标题，打印出来看看结构 (调试用)
                    print(f"⚠️ [Debug] 无法解析新闻项: {item}")

            if not formatted_news:
                return "新闻标题解析失败 (可能是网络或源格式问题)"

            return "\n".join(formatted_news)
        except Exception as e:
            return f"新闻获取报错: {e}"

    def get_insider_transactions(self, symbol):
        """获取内部人交易 (清洗数据，只保留关键列)"""
        try:
            ticker = yf.Ticker(symbol)
            insider = ticker.insider_transactions

            if insider is not None and not insider.empty:
                # 1. 只需要最近 5 条
                recent = insider.head(5)

                # 2. 尝试清洗列 (去除无关的 URL 和 None)
                # yfinance 的列名通常是 ['Shares', 'Value', 'Text', 'Start Date']
                # 我们把 DataFrame 转成更简洁的字符串

                # 选取关键列 (如果存在)
                cols_to_keep = []
                for col in ['Start Date', 'Insider', 'Position', 'Text', 'Value']:
                    if col in recent.columns:
                        cols_to_keep.append(col)

                if cols_to_keep:
                    cleaned_df = recent[cols_to_keep]
                    # 格式化日期，去掉时分秒
                    if 'Start Date' in cleaned_df.columns:
                        cleaned_df['Start Date'] = pd.to_datetime(cleaned_df['Start Date']).dt.strftime('%Y-%m-%d')

                    return cleaned_df.to_string(index=False)

                return recent.to_string()
            return "近期无重大内部人交易"
        except:
            return "内部人数据获取失败"