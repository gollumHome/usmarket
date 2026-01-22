# ==========================================
# 策略配置中心
# ==========================================
# ==========================================
# 1. API 密钥配置
# ==========================================
# 前往 https://aistudio.google.com/app/apikey 免费获取
GEMINI_API_KEY = "AIzaSyC1jLCVc4OcItVaLITjDb12BWRwz2VjlMU"
WECHAT_WEBHOOK='https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=586286fe-7298-4335-8c9d-5227959445fa'

# --- 1. 市场风向标 (用于宏观择时策略) ---
# 逻辑：大盘代表整体水位，VIX代表市场恐慌程度
BENCHMARK = 'SPY'       # 标普500 ETF
RISK_INDICATOR = '^VIX' # 恐慌指数

# --- 2. 核心资产/板块池 (用于动量轮动策略) ---
# 逻辑：包含美股11大行业 + 宽基指数 + 另类资产，用于捕捉资金流向
SECTOR_POOL = [
    'XLK',  # 科技 (Technology)
    'XLV',  # 医疗 (Health Care)
    'XLF',  # 金融 (Financials)
    'XLE',  # 能源 (Energy)
    'XLI',  # 工业 (Industrials)
    'XLY',  # 可选消费 (Discretionary)
    'XLP',  # 必选消费 (Staples)
    'XLU',  # 公用事业 (Utilities)
    'XLB',  # 原材料 (Materials)
    'XLRE', # 房地产 (Real Estate)
    'XLC',  # 通讯服务 (Communication)
    'QQQ',  # 纳斯达克100 (成长股风向)
    'IWM',  # 罗素2000 (小盘股风向)
    'GLD',  # 黄金 (避险/通胀)
    'TLT',  # 20年期美债 (避险/利率敏感)
    'IBIT'  # 比特币ETF (流动性溢价)
]

# --- 3. 明星股观察列表 (用于趋势突破策略) ---
# 逻辑：此处体现 PEAD(盈后漂移) 和 Insider(内部人) 策略。
# 建议放在 config.py 或 main.py 顶部
WATCHLIST = {
    # 七巨头/大盘成长
    'NVDA': 'AI 芯片/大盘权重', 'MSFT': '软件/云服务', 'META': '社交媒体/AI广告',
    'AMZN': '电商/云服务', 'GOOGL': '搜索/AI', 'AAPL': '消费电子/大盘权重',
    'TSLA': '新能源车/机器人', 'NFLX': '流媒体',

    # 半导体/AI 热门
    'AMD': '算力芯片', 'AVGO': '通信芯片/并购', 'SMCI': 'AI 服务器',
    'ARM': '架构/IP', 'TSM': '芯片代工', 'MU': '存储芯片',

    # 太空经济/星链关联
    'RKLB': '商业航天/发射服务', 'ASTS': '卫星通信/手机直连',
    'LUNR': '登月服务', 'SATS': '卫星频谱/星链关联', 'RDW': '空间站基础设施',

    # AI 能源/核电/基础建设
    'CEG': '核电/数据中心供电', 'VST': '电力生产', 'GEV': '电网更新',
    'CCJ': '铀矿/核燃料', 'PLTR': 'AI 软件/大数据分析',

    # 机器人/物理 AI
    'ISRG': '手术机器人', 'SYM': '物流自动化', 'TER': '芯片测试/协作机器人',

    # 跨境电商/中概科技
    'PDD': '跨境电商/Temu', 'BABA': '中国电商/云',

    # 软件与云安全
    'CRWD': '云安全/终端安全', 'PANW': '网络安全平台', 'SNOW': '数据仓库/AI数据'
}

# --- 4. 参数设置 ---
# 判定趋势的均线周期
MA_SHORT = 50   # 短期趋势
MA_MID = 150    # 中期趋势
MA_LONG = 200   # 长期牛熊分界线

# 动量计算回看周期 (用于板块轮动)
MOM_WINDOW_SHORT = 60  # 3个月 (约60交易日)
MOM_WINDOW_LONG = 120  # 6个月 (约120交易日)