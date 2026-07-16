# Chem Agent Demo

这是 Chem Agent 8 个联网测试案例的静态可视化 Demo，不依赖后端 API。

页面展示：

- 原始用户 Query；
- 命中论文和匹配词；
- Stage 路线；
- Macro Plan；
- Device 可行性结果；
- 阻塞约束和离线 handoff；
- Research 质量门错误。

数据来自 `chem-agent/campaigns/exact-online-suite-20260715/`。页面只读展示，不修改 Query，不调用 LLM，也不会向真实设备下发指令。

## 本地预览

```bash
python3 -m http.server 8765
```

然后打开 <http://127.0.0.1:8765/>。

## GitHub Pages

在 GitHub 仓库中进入：

```text
Settings → Pages → Build and deployment
```

选择：

```text
Source: Deploy from a branch
Branch: main
Folder: / (root)
```

页面地址通常是：

```text
https://echo-hyt.github.io/chem-web/
```
