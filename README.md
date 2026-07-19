# Chem Agent Demo

这是 Chem Agent 最新 `dll_main` 版本 8 个离线消融测试案例的静态可视化 Demo，不依赖后端 API。

页面展示：

- 原始用户 Query；
- 命中论文和匹配词；
- Stage 路线；
- Macro Plan；
- Device 可行性结果；
- 阻塞约束和离线 handoff；
- Research 与 Device 原始输出；
- 真实设备链路缺口、疑似遗漏已有设备能力和参数适配的独立复核结论。

数据来自最新提交 `f4cabf337788b6d1b8395c779c5eae903e545ebf` 的评估运行 `chem-agent-eval-20260719-032031`。本轮关闭联网论文搜索，用于离线知识库消融。页面只读展示，不修改 Query，不调用 LLM，也不会向真实设备下发指令。

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
