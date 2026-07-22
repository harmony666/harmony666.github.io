# 云端共享行程设计（腾讯云轻量 + Nginx）

> 日期：2026-07-22  
> 状态：现役规格。此前 Cloudflare Workers + GitHub Pages 方案已废弃（大陆访问失败）。  
> 相关代码：`server/itinerary-api/`、`server/nginx-itinerary.conf`、`scripts/deploy_vps.py`、`generate_html.py`

## 1. 目标

在不依赖境外 Serverless 的前提下，让「一份共享山东九日行」的修改对所有打开同一网址的人在数秒内可见。

非目标：多用户多行程、账号体系、WebSocket 实时协同、微信小程序。

## 2. 已锁定决策

| 项 | 决策 |
|----|------|
| 协作 | 全世界一份共享行程 |
| 权限 | 读公开；写需共享口令 |
| 同步 | 保存后短时间可见（轮询），非 WebSocket |
| 托管 | **前端 + API 同机**：腾讯云轻量（Ubuntu） |
| 入口 | Nginx `:80` 静态页；`/api` 反代到本机 Node `:8787` |
| 存储 | 服务器本地 JSON 文件（`DATA_DIR/itinerary.json`） |
| 客户端 | 云端为准 + localStorage 缓存兜底 |
| 恢复初始 | 口令 + 二次确认后重置**云端** |
| 导入导出 | 保留；导入写云端需口令 |

线上地址：`http://124.222.108.66/`（`API_BASE` 同主机，无尾斜杠）。

## 3. 架构

```text
浏览器 → http://124.222.108.66/
  ├─ GET  /                 → Nginx 静态 index.html
  ├─ GET  /api/itinerary    → Nginx → Node Express
  ├─ PUT  /api/itinerary    → 口令保存（整份 JSON + version）
  ├─ POST /api/itinerary/reset → 口令重置为 seed
  └─ localStorage           → 成功拉取/保存后的缓存；API 失败时只读兜底

Node (systemd: itinerary-api)
  └─ data/itinerary.json
```

- CORS：允许站点源、`localhost:8000`（开发）。
- 口令：服务端 `/etc/itinerary-api.env` 的 `EDIT_PASSWORD`；前端输入后存 `sessionStorage`，请求头 `X-Edit-Password`。
- 前端配置：`generate_html.py` 注入 `API_BASE`；留空则纯本地模式。

## 4. 数据文档

```json
{
  "schemaVersion": 1,
  "version": 1,
  "updatedAt": "ISO-8601",
  "title": "武汉 → 山东 9日旅行计划",
  "points": [ /* Point 模型，经 ItineraryCore.normalizePoints */ ]
}
```

- `version`：整数，成功 PUT/reset +1；PUT 须带客户端当前 `version`，否则 `409`。
- Seed：`server/itinerary-api/src/seed.json`（`scripts/export_seed.py` 自 `coords.json` 生成）。

## 5. 接口摘要

| 方法 | 路径 | 鉴权 | 说明 |
|------|------|------|------|
| GET | `/api/itinerary` | 无 | 返回文档；无文件则写入 seed |
| PUT | `/api/itinerary` | 口令 | body：`version` + `points`（+可选 `title`） |
| POST | `/api/itinerary/reset` | 口令 | 重置为 seed，version +1 |
| GET | `/healthz` | 无 | 健康检查 |

## 6. 部署与运维

1. `python scripts/export_seed.py`（如改了 coords）
2. `python generate_html.py`（`API_BASE=http://124.222.108.66`）
3. `$env:ITINERARY_SSH_PASSWORD=...` → `python scripts/deploy_vps.py`
4. 腾讯云轻量防火墙放行 **TCP 80**
5. 腾讯地图 Key 白名单含 `124.222.108.66`

口令与 SSH 密码不要写入仓库。

## 7. 废弃说明

- 已删除：`workers/itinerary-api/`（Cloudflare Workers + KV + wrangler）
- 不再以 GitHub Pages 为线上入口（仓库可保留源码）
- 控制台若仍有旧 Worker `itinerary-api`，可手动停用/删除（不影响现役站点）
