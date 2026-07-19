# Chem Agent Demo

这是 Chem Agent 最新 `dll_main` 版本 8 个测试案例的静态可视化 Demo，不依赖后端 API。

页面展示：

- 原始用户 Query；
- 命中论文和匹配词；
- Stage 路线；
- Macro Plan；
- Device 可行性结果；
- 阻塞约束和离线 handoff；
- Research 与 Device 原始输出；
- 真实设备链路缺口、疑似遗漏已有设备能力和参数适配的独立复核结论。

基础数据来自最新提交 `f4cabf337788b6d1b8395c779c5eae903e545ebf` 的八题评估。C01、C02、D01 已更新为 Research↔Device 闭环结果：Device 不可行反馈返回 Research B2 重新规划后，三个案例均最终生成 Device workflow 并返回 `success`。页面只读展示，不修改 Query，不调用 LLM，也不会向真实设备下发指令。

闭环结果来源：

```text
chem-agent-dll-main-online-transfer-eval-20260719/
result/device-retry-C01-C02-D01-20260719/closed-loop/
```

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
