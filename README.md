GitHub 每日早报自动生成项目
项目名称：daily-morning-report

一句话简介：使用 GitHub Actions + OpenAI 每天北京时间 7:30 自动生成专业金融投资早报 + 泛知识综合新闻（TXT 文件），完全零服务器、无需本地运行，支持任意 OpenAI 兼容接口。

✨ 项目功能特点
全自动定时运行：每天北京时间 7:30 准时生成（cron 精确对应 UTC 23:30）
完全符合你的原始要求：
自动读取 3 个环境变量：OPENAI_API_KEY、OPENAI_API_BASE、OPENAI_MODEL
使用你完整提供的提示词（未做任何修改）
生成文件名为 yyyymmdd-1.txt，同一天自动递增为 -2.txt、-3.txt……
每一步输出超详细运行报告，便于 GitHub Actions 日志调试
自动提交文件：生成后自动 git commit & push 到 reports/ 目录
支持手动触发：随时在 GitHub 网页一键测试
兼容任意 OpenAI 接口：OpenAI 官方、国内各种代理、OneAPI 等均可
高可读性日志：所有步骤带北京时间戳 + STEP 编号
📁 项目文件结构
<TEXT>
.
├── .github/
│   └── workflows/
│       └── daily-morning-report.yml     # ← Workflow 主文件（已修复）
├── generate_zaobao.py                   # ← Python 主脚本
├── reports/                             # ← 自动生成的早报文件夹（首次运行后自动创建）
│   ├── 20250402-1.txt
│   ├── 20250402-2.txt
│   └── ...
└── README.md
🚀 快速部署（3 分钟上手）
步骤 1：Fork / 新建仓库
Fork 本仓库，或新建一个空仓库（推荐公开仓库，便于查看报告）
把下面两个文件完整复制到你的仓库对应位置。
步骤 2：创建 Workflow 文件
文件路径：.github/workflows/daily-morning-report.yml

<YAML>
name: 每日早报生成（北京时间 7:30）
on:
  schedule:
    - cron: '30 23 * * *'     # UTC 23:30 = 北京时间次日 07:30
  workflow_dispatch:          # 支持手动测试
jobs:
  generate:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout 仓库
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: 设置 Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: 安装依赖
        run: pip install openai
      - name: 生成早报
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          OPENAI_API_BASE: ${{ secrets.OPENAI_API_BASE }}
          OPENAI_MODEL: ${{ secrets.OPENAI_MODEL }}
        run: python generate_zaobao.py
      - name: 自动提交并推送报告
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: '📄 添加每日早报 (${{ github.event_name }})'
          file_pattern: 'reports/*.txt'
          branch: ${{ github.ref_name }}
步骤 3：创建 Python 主脚本
文件路径：generate_zaobao.py

（完整代码请直接复制我之前提供的最终版本，已包含详细日志、文件名自动递增、提示词完整保留等所有功能）

步骤 4：添加 GitHub Secrets（必须）
进入仓库 → Settings → Secrets and variables → Actions → New repository secret，添加以下 3 个：

Secret 名称	说明	示例值
OPENAI_API_KEY	API 密钥	sk-...
OPENAI_API_BASE	接口地址	https://api.openai.com/v1 或你的代理地址
OPENAI_MODEL	模型名称	gpt-4o-mini 或 claude-3-5-sonnet 等
📋 操作方法
1. 自动运行
每天北京时间 7:30 自动执行
生成文件自动保存在 reports/ 目录并提交到仓库
2. 手动测试
进入仓库 → Actions 页面
左侧找到 “每日早报生成（北京时间 7:30）”
点击右侧绿色按钮 Run workflow → 立即运行
等待 1-2 分钟，刷新页面查看日志
3. 查看生成结果
打开 reports/ 文件夹
文件名格式：20250402-1.txt（同一天第几次生成就递增）
🔍 运行日志示例（GitHub Actions 中可见）
<TEXT>
[北京时间 2025-04-02 07:30:12] [STEP 01] === 开始执行每日早报生成脚本 ===
[北京时间 2025-04-02 07:30:12] [STEP 01] 读取系统环境变量...
[北京时间 2025-04-02 07:30:13] [STEP 02] 提示词准备完成（总长度 2456 字符）
[北京时间 2025-04-02 07:30:45] [STEP 03] API 调用成功，生成内容长度: 8567 字符
[北京时间 2025-04-02 07:30:46] [STEP 04] 最终文件名 → reports/20250402-1.txt
[北京时间 2025-04-02 07:30:46] [STEP 99] === 脚本全部执行完成！ ===
🛠️ 自定义与扩展
修改提示词：直接编辑 generate_zaobao.py 中的 prompt 变量
修改生成时间：修改 workflow 中的 cron: '30 23 * * *'
增加通知：需要邮件、企业微信、Telegram、飞书推送等功能，请告诉我，我立刻给你加上
同时生成 Markdown：可在脚本末尾增加写入 .md 文件
失败重试：可在 workflow 中增加 strategy: fail-fast: false + retry
❓ 常见问题排查
Workflow 报错 "Invalid Argument" → 已使用修复后的 YAML（commit_message 使用 github.event_name）
API 调用失败 → 检查 Secrets 是否正确、API Base 是否可访问
文件没有递增 → 脚本已自动处理 while True 循环
reports 文件夹没出现 → 首次运行后会自动创建
想改成其他时间 → 修改 cron 表达式即可（可参考 crontab.guru）
📬 需要更多功能？
欢迎随时在 Issues 或 Discussion 中提出，我可以立即帮你扩展：

自动推送早报到企业微信 / 钉钉 / Telegram
生成 Markdown + GitHub Pages 美化展示
增加图片 / 图表分析
多模型轮询、失败自动重试
历史早报归档与搜索
本 README 基于你提供的完整对话历史生成，已包含所有关键细节，可直接复制使用。

祝使用愉快！每天 7:30 准时收到专业早报，投资与认知双提升 🚀
