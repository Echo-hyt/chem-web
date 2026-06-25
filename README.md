# Chem Web

一个用于调用 Chem Agent 的最小前端页面。

## 使用方式

1. 打开 `index.html` 可以本地预览页面。
2. 部署到 GitHub Pages 后，用户可以输入任务指令、上传文献，并填写后端 API 地址。
3. 后端接口建议使用：

```text
POST /api/run-agent
```

请求使用 `multipart/form-data`：

```text
instruction: 用户输入的任务指令
paper: 用户上传的文献文件
```

返回 JSON：

```json
{
  "result": "agent 输出内容"
}
```

## GitHub Pages

在 GitHub 仓库页面进入：

```text
Settings -> Pages -> Build and deployment
```

选择：

```text
Source: Deploy from a branch
Branch: main
Folder: /root
```

保存后，页面地址通常是：

```text
https://echo-hyt.github.io/chem-web/
```
