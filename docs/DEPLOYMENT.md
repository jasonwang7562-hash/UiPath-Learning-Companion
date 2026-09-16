# 在线运行与部署

## 选择运行方式

| 方式 | 用途 | 是否运行 Python 服务 |
| --- | --- | --- |
| 本地 Streamlit | 开发、离线资料预览、组内演示 | 是，在自己的电脑 |
| GitHub Codespaces | 浏览器开发、临时预览 | 是，在开发容器 |
| Streamlit Community Cloud | 通过应用链接访问 | 是，由 Streamlit 托管 |
| GitHub Pages | 静态项目介绍页 | 否，不适合本应用 |

## Streamlit Community Cloud 部署步骤

1. 登录 https://share.streamlit.io/ ，连接拥有本仓库访问权限的 GitHub 账号。
2. 选择 **Create app → Deploy a public app from GitHub**，或界面提供的对应 GitHub 部署入口。私有仓库需要授予该服务相应仓库权限。
3. Repository：`jasonwang7562-hash/UiPath-Learning-Companion`；Branch：`main`；Main file：`app.py`。
4. 在 Advanced settings 中选择 Python 3.11。初次部署可留空 Secrets，或填写：

   ```toml
   MOCK_LLM = true
   UI_LANGUAGE = "zh"
   ```

5. 点击 Deploy，等待安装依赖和启动。打开生成的 `*.streamlit.app` 地址。
6. 检查三个模块、问号帮助、示例填入和资料检索；确认顶部显示资料预览状态。
7. 在应用管理界面检查访问设置，再将链接分享给组员。私有仓库不意味着应用必然公开，也不意味着所有组员自动有访问权限。

部署依赖账户登录、GitHub 授权和服务当前限制；配置文件本身不表示线上部署已经成功。

## 可选：真实模型

在当前应用的 Secrets 中设置，而不是写进 GitHub：

```toml
MOCK_LLM = false
LLM_API_KEY = "replace-with-your-own-key"
LLM_BASE_URL = "https://api.openai.com/v1"
LLM_MODEL = "gpt-4.1-mini"
LLM_TEMPERATURE = 0.0
LLM_TIMEOUT = 45
UI_LANGUAGE = "zh"
```

保存后重启应用，先做一次小规模请求验证。服务费用与配额取决于模型供应商。
不要将 API key 发到聊天、截图或提交记录中。

## GitHub Codespaces

从仓库 **Code → Codespaces** 创建环境。依赖安装完成后运行：

```bash
python -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501 --server.headless=true
```

从 **Ports → 8501** 打开预览。保留默认私有端口，应用仍使用预览模式。
重连已有环境时先检查终端中的服务是否仍在运行，避免重复占用 8501。
结束后在 Codespaces 管理页停止环境；计算和存储受账户额度及计费设置约束。

## 常见部署问题

- **找不到仓库**：核对登录账号，并检查 Streamlit/GitHub 应用授权是否包含此私有仓库。
- **找不到 app.py**：入口必须是仓库根目录 `app.py`，分支选择 `main`。
- **组件参数不兼容**：确保安装仓库 `requirements.txt` 中固定的 Streamlit 1.63.0。
- **仍是资料预览模式**：检查当前应用的 Secrets、环境变量以及是否已重启。
- **模型请求失败**：检查服务地址、模型名、服务商配额和错误信息；不要把密钥贴入问题描述。
- **Codespaces 无法访问端口**：确认 Streamlit 进程运行中，使用 8501 的转发地址；不要把 `launch.py` 的本机专用地址作为云部署地址。

## 官方说明

- [GitHub Pages 是静态站点托管](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
- [Codespaces 端口转发](https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace)
- [Codespaces 额度与计费](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces)
- [Streamlit Community Cloud 部署](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [Streamlit 云端密钥配置](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
