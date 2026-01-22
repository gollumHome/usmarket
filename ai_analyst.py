import os

import google.generativeai as genai


class GeminiAnalyst:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            self.model = None
            print("错误: 未在环境变量中配置 GEMINI_API_KEY")
        else:
            genai.configure(api_key=api_key)
            try:
                self.model = genai.GenerativeModel('gemini-flash-latest')
            except Exception as e:
                print(f"模型初始化失败: {e}")
                self.model = None

    def _get_etf_mapping(self):
        """定义常用 ETF 的中文化映射，强制 AI 在分析时使用"""
        return """
        【ETF 中文手册】:
        - IWM: 罗素2000小盘股指数 (风险偏好风向标)
        - GLD: 黄金现货 (避险/通胀工具)
        - TLT: 20年期以上国债 (利率敏感指标)
        - XLU: 公用事业板块 (防御性指标)
        - XLV: 医疗保健板块 (防御/价值)
        - XLK: 科技板块 (进攻性)
        - SMH: 半导体板块 (AI/硬科技核心)
        - IBIT: 比特币现货 ETF (数字黄金)
        - KWEB/FXI: 中国互联网/中概股
        - XLE: 能源/石油板块
        """

    def generate_market_brief(self, macro_data, top_sectors, bottom_sectors):
        if not self.model: return "AI 分析器未准备就绪"

        etf_mapping = self._get_etf_mapping()

        prompt = f"""
        你是一位资深美股策略师。请根据以下数据生成【市场早报】。

        {etf_mapping}

        1. 【宏观环境】:
           - 状态: {macro_data['status']}
           - 标普500价格: {macro_data['spy_price']:.2f} (200日均线: {macro_data['ma200']:.2f})
           - VIX 恐慌指数: {macro_data['vix']:.2f}
           - 系统操作建议: {macro_data['advice']}

        2. 【资金流向数据】:
           - 强势标的: {', '.join([f"{k}" for k, v in top_sectors])}
           - 弱势标的: {', '.join([f"{k}" for k, v in bottom_sectors])}

        请按以下结构回答（约 200 字，禁止使用 ** 或 # 等 Markdown 符号，仅输出纯文本）：
        - 市场性质定性：基于标普与200日线的距离判断“趋势强度”，基于VIX判断“恐慌情绪”。
        - 资金逻辑拆解：结合强势和弱势板块，分析资金是在交易“降息预期”、“通胀复苏”还是“人工智能”。
        - 操作策略建议：明确现在适合“积极追逐动能”还是“保留现金等待”。
        - 注意：提及任何 ETF 时，必须带上中文括号说明，如 IWM (罗素2000小盘股)。
        - 特别限制：请只关注宏观大盘和板块流向，不要分析或提及任何具体个股。
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"宏观分析生成失败: {str(e)}"

    def generate_stock_reviews(self, stock_list):
        if not self.model or not stock_list: return "没有待分析的股票数据"

        stocks_info = ""
        for item in stock_list:
            stocks_info += f"""
            --- 代码: {item['symbol']} ---
            - 价格: {item['price']:.2f} (创50日新高)
            - 业务/板块: {item.get('sector', '未知')}
            - 核心新闻: {item['news']}
            - 内部人/机构行为: {item['insider']}
            --------------------------------
            """

        prompt = f"""
        你是一位对冲基金经理，擅长筛选“真突破”与“假突破”。
        请对以下触发 50 日新高的股票进行批量深度分析：

        {stocks_info}

        请输出纯文本列表（严禁使用表格，严禁使用 ** 或 # 符号）：
        格式要求：代码 | 核心业务 | 突破含金量 | 筹码/内部人态度 | 推荐分(0-10) | 一句话点评(逻辑与风险)

        分析准则：
        1. [突破含金量]：分析新闻是属于“一次性噪音”还是“持续性基本面改善”。
        2. [筹码评估]：如果内部人高位减持，需严厉指出风险。
        3. [逻辑风险]：必须一针见血，指出如果买入，哪里是止损核心点。
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"个股深度分析失败: {str(e)}"