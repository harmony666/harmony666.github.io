# 云端共享行程设计（Cloudflare Workers + GitHub Pages）

> 日期：2026-07-22  
> 状态：基于 grilling 共识；用户已口头确认「理解一致」，本文为落库规格。  
> 相关现役前端：`generate_html.py` → `index.html` / `itinerary.html`；核心：`src/itinerary-core.js`

## 1. 目标

在**不买云主机**的前提下，让「一份共享山东九日行」的修改对所有打开同一网址的人在数秒内可见，取代日常依赖 JSON 导入导出同步。

非目标：多用户多行程、账号体系、在线文档级实时协同、微信小程序（另案）。

## 2. 已锁定决策

| 项 | 决策 |
|----|------|
| 协作 | 全世界一份共享行程 |
| 权限 | 读公开；写需共享口令 |
| 同步 | 保存后短时间可见（轮询/拉取），非 WebSocket |
| 托管 | 前端继续 GitHub Pages；API 用 Cloudflare Workers（免费） |
| 存储 | 单个 JSON 文档（KV） |
| 客户端 | 云端为准 + localStorage 缓存兜底 |
| 恢复初始 | 口令 + 二次确认后重置**云端**（全员生效） |
| 导入导出 | 保留；导入写云端需口令 |

大陆访问 Workers 可能偶发不稳：可接受；前端仍走 Pages。

## 3. 架构

```text
浏览器 (harmony666.github.io)
  ├─ GET  /api/itinerary          → 拉共享行程
  ├─ PUT  /api/itinerary          → 口令保存（整份 JSON + version）
  ├─ POST /api/itinerary/reset    → 口令重置为 seed
  └─ localStorage                 → 成功拉取/保存后的缓存；API 失败时只读兜底

Cloudflare Worker
  └─ KV binding ITINERARY_KV
       key: "itinerary:v1"
       value: 文档 JSON
```

- CORS：允许 `https://harmony666.github.io`（及本地 `http://localhost:8000` 开发）。
- 口令：仅存在于 Worker **secrets**（如 `EDIT_PASSWORD`），前端不入库明文；用户在页面输入后存 `sessionStorage`（关标签即失），请求头 `X-Edit-Password` 提交。
- 前端配置：生成 HTML 时注入 `API_BASE`（Worker URL）；无配置时保持现有纯本地模式（降级），避免未部署 Worker 时整站不可用。

## 4. 数据文档

```json
{
  "schemaVersion": 1,
  "version": 1,
  "updatedAt": "ISO-8601",
  "title": "武汉 → 山东 9日旅行计划",
  "points": [ /* 与现有 Point 模型一致，经 ItineraryCore.normalizePoints */ ]
}
```

- `version`：整数，每次成功 PUT/reset +1；PUT 必须带客户端读到的 `version`，服务端不一致则 `409 Conflict`。
- Seed：Worker 内嵌或首次 GET 时若不存在则用与 `BASE_POIS` 同源的初始文档（`version: 1`）。为免双份真相漂移，生成器可导出 `seed-itinerary.json` 供 Worker 构建时拷贝，或 PUT 管理初始化一次。

校验：写路径用与前端相同的规则（可由 Worker 内精简校验，或信任前端但仍做 schemaVersion、points 数组、version 类型检查）。

## 5. API

### `GET /api/itinerary`

- 无鉴权。
- 200：文档 JSON。
- 若 KV 空：写入 seed 后返回。

### `PUT /api/itinerary`

- 头：`X-Edit-Password`、`Content-Type: application/json`
- Body：`{ version, title?, points }`（或完整文档）；服务端 `normalize`/校验后，若 `version` 匹配则保存并 `version++`。
- 401：口令错误。
- 409：版本冲突（body 含当前 `version` / `updatedAt` 提示刷新）。
- 400：校验失败。

### `POST /api/itinerary/reset`

- 头：`X-Edit-Password`
- 将文档重置为 seed，`version` 在当前基础上 +1（或重置为 1 并强制客户端刷新——**采用：重置为 seed 且 `version = oldVersion + 1`**，便于冲突检测）。
- 401 / 200 同上。

限流（可选最小）：同 IP 写接口粗限，防扫口令；规格要求「尽力」，不阻塞 MVP。

## 6. 前端行为变化

| 动作 | 行为 |
|------|------|
| 启动 | `GET` 云端 → 成功则 `POIS = points` 并写缓存；失败则读缓存只读提示，再不行用 `BASE_POIS` |
| 保存点/导入 | 先本地算出 candidate → `PUT`（带口令与 version）→ 成功更新 POIS/version/缓存；409 提示刷新 |
| 轮询 | 有 `API_BASE` 时每 5s `GET`；若 `version` 变大则静默替换 POIS 并重绘（编辑弹窗打开时可跳过或仅提示） |
| 恢复初始 | 文案明确「将覆盖云端、所有人的修改」→ 确认 → `POST reset` |
| 导出 | 仍可导出当前 POIS |
| 无 `API_BASE` | 保持现有 localStorage-only 行为 |

口令 UI：首次写操作前弹出口令框；「记住至关闭标签页」。

## 7. 仓库结构（拟增）

```text
workers/itinerary-api/
  wrangler.toml
  src/index.js
  src/seed.json          # 由 generate_html.py 或脚本从 coords 生成
  package.json
```

前端仍由 `generate_html.py` 生成；增加 `API_BASE` 占位与云端同步脚本逻辑。

## 8. 安全与运维

- 口令不是高强度多用户方案；链接+口令泄露即可被改。出行小团队可接受。
- 定期导出 JSON 备份仍建议。
- Worker 部署：`wrangler secret put EDIT_PASSWORD`；Pages 与 Worker 分开部署。
- 不把口令、Account Token 写入 git。

## 9. 测试

- Worker：口令对错、version 冲突、reset、CORS 预检（可用 vitest/miniflare 或手工 curl 清单）。
- 前端生成物测试：存在 `API_BASE` / `fetchItinerary` / `X-Edit-Password` / 409 处理等字符串与关键分支（延续 `tests/test_generate_html.py` 风格）。
- 手动：两浏览器，A 保存后 B 在 5s 内看到；冲突时 409。

## 10. 实施顺序

1. Worker + KV + seed + 三路由  
2. 生成器注入 API 客户端与口令/轮询/冲突 UI  
3. README / AGENTS 更新部署步骤  
4. 部署 Worker，配置 `API_BASE`，回归地图与编辑

## 11. 规格自检

- [x] 无 TBD/占位符决策  
- [x] 与 grilling 一致（含恢复云端、导入保留）  
- [x] 范围单系统：共享行程 API + 前端接线  
- [x] 明确降级：无 API_BASE / GET 失败  
- [x] 双份 seed 风险：注明需与 coords 同步机制  
