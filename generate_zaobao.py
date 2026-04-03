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

# Step 2: 准备模块列表和通用指令（核心修改：解决AI输出严重压缩问题）
# 现在改为“每次只让AI生成一个模块”，最后程序自动整合所有模块
log(2, "准备模块列表和通用指令（分模块调用AI，确保每个模块完整输出）")

general_instructions = """你是一名情报搜集，整理，分析专家，你通过对主流媒体信息的归集，为我整理一份早报，内容专业、客观、详尽，重点突出，结构清晰。

输出要求：
完整保留原文 / 原事件所有细节。
包含时间、地点、主体、数据、关键引述、背景信息。
不使用 “据悉”“据了解” 等模糊概括。
不删减段落，不合并信息，不省略细节。
结构清晰，逐条 / 分段详细展开。
禁止压缩，禁止简化。
每一模块至少包含10个条目，每条目有标题和200字内容简介。每一条目都需要符合输出要求"""

modules = [
    # 第一部分、投资金融领域
    {"part": "第一部分、投资金融领域", "part_req": "要求内容专业、客观、简洁，重点突出，结构清晰，覆盖以下内容：", "number": 1, "title": "全球宏观要闻", "desc": "隔夜国际重要经济数据、央行政策动向、地缘政治对资本市场的影响。"},
    {"part": "第一部分、投资金融领域", "part_req": "要求内容专业、客观、简洁，重点突出，结构清晰，覆盖以下内容：", "number": 2, "title": "美股及海外市场", "desc": "隔夜美股三大指数表现、热门板块、重要中概股走势、欧洲 / 亚太主要市场概况。"},
    {"part": "第一部分、投资金融领域", "part_req": "要求内容专业、客观、简洁，重点突出，结构清晰，覆盖以下内容：", "number": 3, "title": "A 股市场前瞻", "desc": "昨日 A 股收盘总结、北向资金流向、龙虎榜要点、今日潜在影响市场的重要事件与数据。"},
    {"part": "第一部分、投资金融领域", "part_req": "要求内容专业、客观、简洁，重点突出，结构清晰，覆盖以下内容：", "number": 4, "title": "《新闻联播》全文摘要", "desc": "最新新闻联播咨询，政策、产业政策、涉及的行业以及企业，重要事件。"},
    {"part": "第一部分、投资金融领域", "part_req": "要求内容专业、客观、简洁，重点突出，结构清晰，覆盖以下内容：", "number": 5, "title": "行业与板块机会", "desc": "重点关注金融、消费、科技、新能源、医药、周期等板块的最新政策、产业动态、催化事件。"},
    {"part": "第一部分、投资金融领域", "part_req": "要求内容专业、客观、简洁，重点突出，结构清晰，覆盖以下内容：", "number": 6, "title": "债券、汇率、大宗商品", "desc": "美债收益率、人民币汇率、原油、黄金、有色金属等关键品种简要走势。"},
    {"part": "第一部分、投资金融领域", "part_req": "要求内容专业、客观、简洁，重点突出，结构清晰，覆盖以下内容：", "number": 7, "title": "重要公告与监管动态", "desc": "证监会、交易所、重要公司业绩预告 / 公告、退市与 IPO 相关信息。"},
    {"part": "第一部分、投资金融领域", "part_req": "要求内容专业、客观、简洁，重点突出，结构清晰，覆盖以下内容：", "number": 8, "title": "投资策略简要提示", "desc": "当日市场情绪判断、风险点、值得跟踪的方向，不构成具体买卖建议。"},
    
    # 第二部分、泛知识综合新闻
    {"part": "第二部分、泛知识综合新闻", "part_req": "内容覆盖广泛但不杂乱，重点选取有长期价值、认知增量的信息，包括：", "number": 1, "title": "国内要闻", "desc": "重要政策、产业趋势、科技进展、民生与社会热点。"},
    {"part": "第二部分、泛知识综合新闻", "part_req": "内容覆盖广泛但不杂乱，重点选取有长期价值、认知增量的信息，包括：", "number": 2, "title": "国际动态", "desc": "全球政治经济、科技竞争、国际合作与重大事件。"},
    {"part": "第二部分、泛知识综合新闻", "part_req": "内容覆盖广泛但不杂乱，重点选取有长期价值、认知增量的信息，包括：", "number": 3, "title": "科技前沿", "desc": "人工智能、半导体、新能源、生物医药、航天航空等领域突破。"},
    {"part": "第二部分、泛知识综合新闻", "part_req": "内容覆盖广泛但不杂乱，重点选取有长期价值、认知增量的信息，包括：", "number": 4, "title": "科学研究", "desc": "预印本头条、重大科技突破。"},
    {"part": "第二部分、泛知识综合新闻", "part_req": "内容覆盖广泛但不杂乱，重点选取有长期价值、认知增量的信息，包括：", "number": 5, "title": "商业与产业", "desc": "巨头动态、商业模式创新、行业格局变化。"},
    {"part": "第二部分、泛知识综合新闻", "part_req": "内容覆盖广泛但不杂乱，重点选取有长期价值、认知增量的信息，包括：", "number": 6, "title": "文化、社会、科普", "desc": "有价值的社会观察、科普知识、历史文化、健康常识。"},
    {"part": "第二部分、泛知识综合新闻", "part_req": "内容覆盖广泛但不杂乱，重点选取有长期价值、认知增量的信息，包括：", "number": 7, "title": "会议", "desc": "国内重要政治、经济会议。"},
]

beijing_now = datetime.now(timezone(timedelta(hours=8)))
date_info = f"今天是北京时间 {beijing_now.strftime('%Y年%m月%d日 %H:%M')}，请基于最新实时信息生成早报。"

log(2, f"✅ 模块准备完成，共 {len(modules)} 个模块（通用指令 + 日期说明已就绪）")

# Step 3: 分模块调用 OpenAI API（每次只生成一个模块）
log(3, f"初始化 OpenAI 客户端并开始分模块调用模型 {model}")
client = OpenAI(api_key=api_key, base_url=api_base)

module_contents = []
for idx, mod in enumerate(modules, 1):
    log(3, f"[模块 {idx:02d}/{len(modules)}] 正在生成 → {mod['part']} 模块{mod['number']}.{mod['title']}")
    
    module_prompt = f"""{date_info}

{general_instructions}

{mod['part']}
{mod['part_req']}

模块{mod['number']}.{mod['title']}：{mod['desc']}

**重要指令**：请严格只输出 **这个模块** 的完整内容，不要输出任何其他模块、其他部分、引言、结尾或额外说明。只输出模块标题和详细内容，必须严格满足“每一模块至少包含10个条目，每条目有标题和200字内容简介”的输出要求，内容专业、客观、详尽，不得压缩、简化或省略任何细节。"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": module_prompt}],
            temperature=0.6,
            max_tokens=8000,   # 单个模块专用较高 token 限制，确保不被压缩
            top_p=0.95,
        )
        module_content = response.choices[0].message.content.strip()
        module_contents.append({"mod": mod, "content": module_content})
        log(3, f"✅ 模块 {idx} 生成成功，长度: {len(module_content)} 字符")
    except Exception as e:
        log(3, f"❌ 模块 {idx} 调用失败: {str(e)}")
        sys.exit(1)

# 所有模块生成完毕后，由程序自动整合
log(3, "✅ 所有模块生成完成，开始程序自动整合结果")
final_content = ""
current_part = None
for item in module_contents:
    mod = item["mod"]
    content = item["content"]
    if current_part != mod["part"]:
        if current_part is not None:
            final_content += "\n"
        final_content += f"\n{mod['part']}\n\n"
        current_part = mod["part"]
    final_content += f"模块{mod['number']}.{mod['title']}\n\n{content}\n\n"

log(3, f"✅ 整合完成，最终早报总长度: {len(final_content)} 字符")

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
    f.write(final_content)

log(5, "✅ 文件写入成功")

# Step 6: 内容预览（便于调试）
log(6, "内容前 800 字符预览：")
print("-" * 80)
print(final_content[:800])
print("-" * 80)

log(99, "=== 脚本全部执行完成！早报已分模块生成并整合完成 ===")
