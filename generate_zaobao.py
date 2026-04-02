import os
import sys
from datetime import datetime, timezone, timedelta
from openai import OpenAI

def log(step: int, message: str):
    beijing_time = datetime.now(timezone(timedelta(hours=8)))
    timestamp = beijing_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[北京时间 {timestamp}] [STEP {step:02d}] {message}")
    sys.stdout.flush()

log(1, "=== 开始执行每日早报生成脚本 ===")

# Step 1: 读取环境变量
log(1, "读取系统环境变量 OPENAI_API_KEY / OPENAI_API_BASE / OPENAI_MODEL")
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")
model = os.getenv("OPENAI_MODEL")

if not all([api_key, api_base, model]):
    log(1, "❌ 错误：缺少一个或多个必要的环境变量")
    sys.exit(1)

log(1, f"✅ OPENAI_API_BASE = {api_base}")
log(1, f"✅ OPENAI_MODEL = {model}")

# Step 2: 准备提示词（完全使用你提供的原文，仅在最前面增加日期说明以确保内容时效性）
log(2, "准备提示词（已严格按要求使用原文提示词）")
prompt = """你是一名情报搜集，整理，分析专家，你通过对主流媒体信息的归集，为我整理一份早报，内容专业、客观、详尽，重点突出，结构清晰
每一模块至少包含10个条目，每条目有标题和200字内容简介。
输出要求：
完整保留原文 / 原事件所有细节。
包含时间、地点、主体、数据、关键引述、背景信息。
不使用 “据悉”“据了解” 等模糊概括。
不删减段落，不合并信息，不省略细节。
结构清晰，逐条 / 分段详细展开。

第一部分、投资金融领域
要求内容专业、客观、简洁，重点突出，结构清晰，覆盖以下内容：
模块1.全球宏观要闻：隔夜国际重要经济数据、央行政策动向、地缘政治对资本市场的影响。
模块2.美股及海外市场：隔夜美股三大指数表现、热门板块、重要中概股走势、欧洲 / 亚太主要市场概况。
模块3.A 股市场前瞻：昨日 A 股收盘总结、北向资金流向、龙虎榜要点、今日潜在影响市场的重要事件与数据。
模块4.《新闻联播》全文摘要：最新新闻联播咨询，政策、产业政策、涉及的行业以及企业，重要事件。
模块5.行业与板块机会：重点关注金融、消费、科技、新能源、医药、周期等板块的最新政策、产业动态、催化事件。
模块6.债券、汇率、大宗商品：美债收益率、人民币汇率、原油、黄金、有色金属等关键品种简要走势。
模块7.重要公告与监管动态：证监会、交易所、重要公司业绩预告 / 公告、退市与 IPO 相关信息。
模块8.投资策略简要提示：当日市场情绪判断、风险点、值得跟踪的方向，不构成具体买卖建议。
要求：逻辑清晰、数据准确、无冗余内容，适合长期投资者与趋势交易者阅读。
第二部分、泛知识综合新闻
内容覆盖广泛但不杂乱，重点选取有长期价值、认知增量的信息，包括：
模块1.国内要闻：重要政策、产业趋势、科技进展、民生与社会热点。
模块2.国际动态：全球政治经济、科技竞争、国际合作与重大事件。
模块3.科技前沿：人工智能、半导体、新能源、生物医药、航天航空等领域突破。
模块4.科学研究：预印本头条、重大科技突破。
模块5.商业与产业：巨头动态、商业模式创新、行业格局变化。
模块6.文化、社会、科普：有价值的社会观察、科普知识、历史文化、健康常识。
模块7.会议：国内重要政治、经济会议。
要求：客观中立、信息密度高、适合提升认知，避免娱乐化碎片化内容。"""

# 增加日期说明（强烈推荐，不影响原文提示词逻辑）
beijing_now = datetime.now(timezone(timedelta(hours=8)))
date_info = f"今天是北京时间 {beijing_now.strftime('%Y年%m月%d日 %H:%M')}，请基于最新实时信息生成早报。"
prompt = date_info + "\n\n" + prompt

log(2, f"✅ 提示词准备完成（总长度 {len(prompt)} 字符）")

# Step 3: 调用 OpenAI API
log(3, f"初始化 OpenAI 客户端并调用模型 {model}")
client = OpenAI(api_key=api_key, base_url=api_base)

try:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=12000,
        top_p=0.95,
    )
    content = response.choices[0].message.content.strip()
    log(3, f"✅ API 调用成功，生成内容长度: {len(content)} 字符")
except Exception as e:
    log(3, f"❌ API 调用失败: {str(e)}")
    sys.exit(1)

# Step 4: 生成文件名（yyyymmdd-N.txt，N自动递增）
log(4, "生成文件名")
today = beijing_now.strftime("%Y%m%d")
os.makedirs("reports", exist_ok=True)

i = 1
while True:
    filename = f"reports/{today}-{i}.txt"
    if not os.path.exists(filename):
        break
    i += 1

log(4, f"最终文件名 → {filename}")

# Step 5: 写入 TXT 文件
log(5, f"写入文件 {filename}")
with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

log(5, "✅ 文件写入成功")

# Step 6: 内容预览（便于调试）
log(6, "内容前 600 字符预览：")
print("-" * 80)
print(content[:600])
print("-" * 80)

log(99, "=== 脚本全部执行完成！早报已生成并准备自动提交 ===")
