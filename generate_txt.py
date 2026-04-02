#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日早报生成器
功能：调用OpenAI API生成投资金融和泛知识综合新闻早报，保存为txt文件
"""

import os
import sys
from datetime import datetime
import pytz

# ==================== 第一步：环境初始化报告 ====================
print("=" * 60)
print("【步骤1】环境初始化")
print("=" * 60)

# 设置北京时间时区
print("[INFO] 正在设置时区...")
try:
    beijing_tz = pytz.timezone('Asia/Shanghai')
    print(f"[SUCCESS] 时区设置成功: Asia/Shanghai")
except Exception as e:
    print(f"[ERROR] 时区设置失败: {e}")
    sys.exit(1)

# 获取当前北京时间
print("[INFO] 正在获取当前北京时间...")
now = datetime.now(beijing_tz)
current_date = now.strftime("%Y%m%d")
current_time = now.strftime("%Y-%m-%d %H:%M:%S")
print(f"[SUCCESS] 当前北京时间: {current_time}")
print(f"[INFO] 日期标识: {current_date}")

# ==================== 第二步：读取环境变量 ====================
print("\n" + "=" * 60)
print("【步骤2】读取系统环境变量")
print("=" * 60)

def get_env_variable(var_name, required=True):
    """读取环境变量，支持调试输出"""
    print(f"[INFO] 正在读取环境变量: {var_name}")
    value = os.getenv(var_name)
    
    if value:
        # 对于API密钥，只显示前8位和后4位，保护安全
        if "KEY" in var_name and len(value) > 12:
            masked = f"{value[:8]}...{value[-4:]}"
            print(f"[SUCCESS] {var_name} 已读取: {masked} (长度: {len(value)})")
        else:
            print(f"[SUCCESS] {var_name} 已读取: {value}")
        return value
    else:
        if required:
            print(f"[ERROR] 环境变量 {var_name} 未设置，这是必需项")
            sys.exit(1)
        else:
            print(f"[WARNING] 环境变量 {var_name} 未设置，使用默认值")
            return None

# 读取必需的环境变量
OPENAI_API_KEY = get_env_variable("OPENAI_API_KEY")
OPENAI_API_BASE = get_env_variable("OPENAI_API_BASE")
OPENAI_MODEL = get_env_variable("OPENAI_MODEL")

print(f"\n[INFO] 环境变量读取完成")
print(f"  - API基础地址: {OPENAI_API_BASE}")
print(f"  - 使用模型: {OPENAI_MODEL}")

# ==================== 第三步：构建提示词 ====================
print("\n" + "=" * 60)
print("【步骤3】构建提示词")
print("=" * 60)

PROMPT = """请为我整理一份早报，内容专业、客观、简洁，重点突出，结构清晰
第一部分、投资金融领域
要求内容专业、客观、简洁，重点突出，结构清晰，覆盖以下内容：
全球宏观要闻：隔夜国际重要经济数据、央行政策动向、地缘政治对资本市场的影响。
美股及海外市场：隔夜美股三大指数表现、热门板块、重要中概股走势、欧洲 / 亚太主要市场概况。
A 股市场前瞻：昨日 A 股收盘总结、北向资金流向、龙虎榜要点、今日潜在影响市场的重要事件与数据。
新闻联播摘要：最新新闻联播咨询，政策、产业政策、涉及的行业以及企业，重要事件。
行业与板块机会：重点关注金融、消费、科技、新能源、医药、周期等板块的最新政策、产业动态、催化事件。
债券、汇率、大宗商品：美债收益率、人民币汇率、原油、黄金、有色金属等关键品种简要走势。
重要公告与监管动态：证监会、交易所、重要公司业绩预告 / 公告、退市与 IPO 相关信息。
投资策略简要提示：当日市场情绪判断、风险点、值得跟踪的方向，不构成具体买卖建议。
要求：逻辑清晰、数据准确、无冗余内容，适合长期投资者与趋势交易者阅读。
第二部分、泛知识综合新闻
内容覆盖广泛但不杂乱，重点选取有长期价值、认知增量的信息，包括：
国内要闻：重要政策、产业趋势、科技进展、民生与社会热点。
国际动态：全球政治经济、科技竞争、国际合作与重大事件。
科技前沿：人工智能、半导体、新能源、生物医药、航天航空等领域突破。
科学研究：预印本头条、重大科技突破。
商业与产业：巨头动态、商业模式创新、行业格局变化。
文化、社会、科普：有价值的社会观察、科普知识、历史文化、健康常识。
会议：国内重要政治、经济会议。
要求：客观中立、信息密度高、适合提升认知，避免娱乐化碎片化内容。"""

print(f"[INFO] 提示词构建完成")
print(f"[INFO] 提示词长度: {len(PROMPT)} 字符")
print(f"[INFO] 提示词预览（前100字符）: {PROMPT[:100]}...")

# ==================== 第四步：调用OpenAI API ====================
print("\n" + "=" * 60)
print("【步骤4】调用OpenAI API生成早报内容")
print("=" * 60)

print("[INFO] 正在导入OpenAI库...")
try:
    from openai import OpenAI
    print("[SUCCESS] OpenAI库导入成功")
except ImportError as e:
    print(f"[ERROR] 导入OpenAI库失败: {e}")
    print("[INFO] 请确保已安装: pip install openai")
    sys.exit(1)

print("[INFO] 正在初始化OpenAI客户端...")
try:
    # 使用环境变量方式初始化，避免 proxies 参数问题
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    if OPENAI_API_BASE:
        os.environ["OPENAI_BASE_URL"] = OPENAI_API_BASE
    
    client = OpenAI()  # 从环境变量自动读取
    print(f"[SUCCESS] OpenAI客户端初始化成功")
    print(f"[INFO] API基础地址: {OPENAI_API_BASE or 'https://api.openai.com/v1'}")
except Exception as e:
    print(f"[ERROR] OpenAI客户端初始化失败: {e}")
    sys.exit(1)




print("[INFO] 正在发送API请求...")
print(f"[INFO] 使用模型: {OPENAI_MODEL}")
print(f"[INFO] 请求时间: {datetime.now(beijing_tz).strftime('%H:%M:%S')}")

try:
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "你是一位专业的财经分析师和新闻编辑，擅长整合投资金融信息和泛知识综合新闻。请确保内容专业、客观、简洁，数据准确，结构清晰。"
            },
            {
                "role": "user",
                "content": PROMPT
            }
        ],
        temperature=0.7,
        max_tokens=4000
    )
    print("[SUCCESS] API请求成功")
    print(f"[INFO] 响应ID: {response.id}")
    print(f"[INFO] 使用Token: 输入{response.usage.prompt_tokens} / 输出{response.usage.completion_tokens} / 总计{response.usage.total_tokens}")
    
    # 提取内容
    ai_content = response.choices[0].message.content
    print(f"[SUCCESS] 内容生成成功，长度: {len(ai_content)} 字符")
    print(f"[INFO] 内容预览（前200字符）: {ai_content[:200]}...")
    
except Exception as e:
    print(f"[ERROR] API调用失败: {e}")
    sys.exit(1)

# ==================== 第五步：生成文件名 ====================
print("\n" + "=" * 60)
print("【步骤5】生成文件名（自动递增）")
print("=" * 60)

def get_next_filename(base_date):
    """获取下一个可用的文件名，自动递增"""
    print(f"[INFO] 正在查找可用的文件名...")
    print(f"[INFO] 基础日期: {base_date}")
    
    # 从1开始尝试
    counter = 1
    max_attempts = 100  # 防止无限循环
    
    while counter <= max_attempts:
        filename = f"{base_date}-{counter}.txt"
        print(f"[INFO] 检查文件是否存在: {filename}")
        
        if not os.path.exists(filename):
            print(f"[SUCCESS] 找到可用文件名: {filename}")
            return filename
        
        print(f"[INFO] 文件已存在，尝试下一个编号")
        counter += 1
    
    print(f"[ERROR] 已达到最大尝试次数({max_attempts})，无法生成新文件名")
    sys.exit(1)

# 获取文件名
output_filename = get_next_filename(current_date)
print(f"[SUCCESS] 最终文件名: {output_filename}")

# ==================== 第六步：构建文件内容 ====================
print("\n" + "=" * 60)
print("【步骤6】构建文件内容")
print("=" * 60)

file_content = f"""早报生成报告
==================
生成时间: {current_time}
时区: Asia/Shanghai (北京时间)
文件名: {output_filename}
API模型: {OPENAI_MODEL}
API基础地址: {OPENAI_API_BASE}

================== 早报正文 ==================

{ai_content}

================== 生成结束 ==================
本文件由AI自动生成，内容仅供参考，不构成投资建议。
"""

print(f"[INFO] 文件内容构建完成")
print(f"[INFO] 文件总长度: {len(file_content)} 字符")
print(f"[INFO] 包含AI生成内容: {len(ai_content)} 字符")

# ==================== 第七步：写入文件 ====================
print("\n" + "=" * 60)
print("【步骤7】写入文件到磁盘")
print("=" * 60)

print(f"[INFO] 正在写入文件: {output_filename}")
try:
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(file_content)
    print(f"[SUCCESS] 文件写入成功")
    
    # 验证文件
    file_size = os.path.getsize(output_filename)
    print(f"[INFO] 文件大小: {file_size} 字节")
    print(f"[INFO] 绝对路径: {os.path.abspath(output_filename)}")
    
except Exception as e:
    print(f"[ERROR] 文件写入失败: {e}")
    sys.exit(1)

# ==================== 第八步：完成报告 ====================
print("\n" + "=" * 60)
print("【步骤8】执行完成")
print("=" * 60)

print(f"[SUCCESS] 早报生成流程全部完成！")
print(f"[INFO] 输出文件: {output_filename}")
print(f"[INFO] 生成时间: {datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')}")
print(f"[INFO] 文件内容预览:")
print("-" * 40)
print(file_content[:500] + "...")
print("-" * 40)
print("[INFO] 程序正常退出")
