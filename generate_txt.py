import os
from datetime import datetime
import pytz

# 设置北京时间时区
beijing_tz = pytz.timezone('Asia/Shanghai')

# 获取当前北京时间
now = datetime.now(beijing_tz)

# 生成文件名：2026-04-02_10-58-00.txt
filename = now.strftime("%Y-%m-%d_%H-%M-%S") + ".txt"

# 文件内容
content = f"""生成时间: {now.strftime("%Y-%m-%d %H:%M:%S")}
时区: Asia/Shanghai (北京时间)
文件名: {filename}
"""

# 写入文件
with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print(f"已生成文件: {filename}")
