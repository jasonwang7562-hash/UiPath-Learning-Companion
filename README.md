# UiPath Learning Companion

**PE6203 · Group 5** — 面向 PE6202 UiPath 课程的中英双语学习辅助应用。

把课程知识、操作实践与练习连起来：先理解概念，再排查工作流，最后用练习检查理解。
基于 Python、Streamlit 和 Pydantic；课程依据来自仓库中的结构化资料卡片。

> **默认可直接运行，无需 API key。** 资料预览模式展示相关课程资料和固定示例，不生成真实 AI 回答、诊断或试题，也不判分。真实模型功能需要另行配置服务。

## 在线体验

**[点击打开小组在线演示 →](https://uipath-learning-companion-bilingual-2026.streamlit.app/)**

无需在自己的电脑上安装 Python，打开浏览器即可访问。此链接由小组成员 `tonya0719` 在 Streamlit Community Cloud 上维护；已核对页面包含新版界面与使用帮助，并显示真实模型模式。页面可访问不代表所有模型请求均已验证。

线上配置和版本以该部署为准，本仓库的更新不保证自动同步至该地址。演示服务若休眠，首次打开可能需要等待启动。下文的“默认资料预览模式”指从本仓库自行运行时的默认配置。

## 功能与使用方式

| 模块 | 适合什么时候用 | 主要交互 |
| --- | --- | --- |
| 知识问答 | 不理解概念或 Activity 的区别 | 按 Week 检索、展开资料来源、填入追问、带入练习主题 |
| 操作与排错 | 不知道下一步，或结果与预期不同 | 分别填写预期、实际现象、报错与最近修改；按检查、修复、验证阅读建议 |
| 练习与测验 | 希望检查自己是否理解 | 按主题、难度与题型出题，提交选项后查看讲解；生成内容需人工复核 |
| 使用帮助 | 不知道该问什么或遇到使用问题 | 导航下方的问号入口；按当前模块提供提问模板、常见问题及一键示例 |

- 中英文界面；课程原文保留原语言。
- 深蓝紫色视觉主题、课程插画、分区卡片与清晰的表单层级。
- 示例、追问和主题跳转仅填入内容，由使用者检查后提交。
- 当前会话最多保留 50 条运行记录，可导出 JSON / Markdown。

## 本地运行

推荐 Python **3.11**，依赖版本见 `requirements.txt`。在项目根目录执行：

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe launch.py
```

如果已经创建虚拟环境，可直接执行 `./start.ps1`。启动后打开 http://127.0.0.1:8501 。

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

不要使用 `python app.py`；页面需要通过 Streamlit 启动。

## 在浏览器中运行

### GitHub Codespaces：适合开发和临时演示

1. 打开本仓库，选择 **Code → Codespaces → Create codespace**。
2. 容器将使用 Python 3.11 并安装 `requirements.txt`。
3. 在终端执行：

   ```bash
   python -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501 --server.headless=true
   ```

4. 打开 **Ports** 中的 **8501** 预览。端口默认保持私有。
5. 用完后停止 Codespace；不再需要时删除开发环境，减少计算和存储用量。

Codespaces 按账户额度及计费设置使用资源，不能视为永久免费的网站托管。
仓库权限与端口访问权限分别控制，不会因为有仓库链接就自动获得应用访问权限。

### Streamlit Community Cloud：适合提供应用链接

见 [完整部署步骤](docs/DEPLOYMENT.md)。使用本仓库的 `main` 分支，入口为 `app.py`，Python 选择 3.11。
初次部署保持资料预览模式；无需填写 API key。

**GitHub Pages 只托管静态网页，无法直接运行本项目的 Python/Streamlit 服务。**
GitHub Actions 用于自动检查代码，也不是长期运行网站的方式。

## 启用真实模型（可选）

复制 `.env.example` 为 `.env`，填入你自己的 OpenAI 兼容服务配置：

```dotenv
MOCK_LLM=false
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4.1-mini
LLM_TEMPERATURE=0.0
LLM_TIMEOUT=45
UI_LANGUAGE=zh
```

模型名称只是配置示例，需要与你的服务商实际可用模型一致。真实请求可能产生服务商费用。
配置优先级：进程环境变量 → 根目录 `.env` → Streamlit Secrets → 默认值。
在云端通过应用管理界面的 Secrets 配置，**不要提交 `.env` 或 `.streamlit/secrets.toml`**。

## 项目结构

```text
app.py                 Streamlit 页面入口
ui_theme.py            视觉主题与页面组件
ui_help.py             按模块组织的双语帮助与 FAQ
ui_learning.py         资料来源与追问辅助
ui_debug.py            排错输入整理与必填检查
ui_locale.py           双语文案
ui_examples.py         示例输入与固定讲题示例
ui_runs.py             会话记录、脱敏与导出
config.py              环境变量、.env 与 Secrets 配置
llm_client.py          模型请求、重试与结构化输出校验
modules/               知识问答、操作指导、练习业务逻辑
retrieval/             轻量关键词检索
schemas/               Pydantic 输入输出结构
data/                  31 个概念、20 个操作任务、9 道例题、3 张官方资料卡
prompts/               A/B/C 提示词版本
evaluation/            评估用例与脚本
tests/                 单元测试和 Streamlit 交互测试
docs/                  部署及项目说明
.github/workflows/     自动检查
.devcontainer/         Codespaces 开发环境
```

## 验证与评估

在项目根目录运行：

```bash
python scripts/validate_data.py
python -m unittest discover -s tests -v
python evaluation/run_eval.py
```

默认测试和评估结构检查无需真实模型。GitHub Actions 在推送或 PR 时运行数据校验、单元测试及评估结构检查。
只有配置模型后显式运行 `python evaluation/run_eval.py --run --variant all --allow-draft` 才会执行真实评估请求。

## 范围与限制

- 概念资料覆盖 Weeks 1–5，课堂操作练习覆盖 Weeks 1–4。
- 采用轻量关键词检索，不是向量检索系统；资料不足时应补充上下文或核对原课程材料。
- 9 道参考例题的答案仍待人工核对；生成题不代表教师原题或考试预测。
- 当前会话记录不是持久数据库。切换语言会重置输入、结果及记录，需要时先导出。
- 本工具提供步骤与建议，不会直接操作 UiPath Studio 或执行机器人工作流。
- 导出会做常见字段脱敏，分享前仍需检查内容。

## 来源与小组成员

基于小组原项目 [Tonya0719/UiPath-Learning-Companion](https://github.com/Tonya0719/UiPath-Learning-Companion) 继续开发。
本版本保留原项目历史，并加入界面、交互和上下文帮助优化。

Group 5：Fang Xinyi、Li Zihao、Miao Jiaxuan、Wang Chenyu、Wang Senmiao、Wu Yushan。
这是学生课程项目，非 NTU 官方服务。课程资料与第三方内容的权利属于各自权利人。
本仓库尚未指定开源许可证；上传到 GitHub 不等于授予任意再分发许可。

### English summary

A bilingual, course-grounded UiPath learning companion for concept explanations, workflow troubleshooting and practice.
Run `python -m pip install -r requirements.txt`, then `python -m streamlit run app.py`.
The default preview mode needs no API key and does not generate or grade model answers.
See [deployment instructions](docs/DEPLOYMENT.md) for Codespaces and Streamlit Community Cloud.
