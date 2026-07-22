# Cloud Shared Itinerary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让一份共享行程经 Cloudflare Worker + KV 读写，GitHub Pages 前端带口令保存并短时间同步，替代日常 JSON 互传。

**Architecture:** Worker 提供 GET/PUT/reset；KV 存单份 JSON（含 version）；前端在有 `API_BASE` 时云端为准、localStorage 缓存；无 `API_BASE` 时保持纯本地。

**Tech Stack:** Cloudflare Workers (JS)、KV、现有 `generate_html.py` + `ItineraryCore`、Python/Node 测试。

## Global Constraints

- 读公开、写需 `X-Edit-Password`（Worker secret `EDIT_PASSWORD`）
- 文档：`schemaVersion: 1`、`version` 整数、`points` 经 normalize
- PUT 版本冲突返回 409
- CORS：`https://harmony666.github.io`、`http://localhost:8000`
- 口令不进 git；`API_BASE` 可空以降级
- 恢复初始：口令 + 二次确认后 `POST /api/itinerary/reset` 重置云端
- 导入导出保留；导入成功后 PUT 云端

## File map

| 文件 | 职责 |
|------|------|
| `workers/itinerary-api/wrangler.toml` | Worker 名、KV binding |
| `workers/itinerary-api/src/index.js` | 路由与鉴权 |
| `workers/itinerary-api/src/seed.json` | 初始文档（由生成脚本写出） |
| `workers/itinerary-api/package.json` | wrangler 依赖 |
| `scripts/export_seed.py` | 从 coords.json 导出 seed.json |
| `generate_html.py` | 注入 API_BASE 与云端同步逻辑 |
| `tests/test_generate_html.py` | 前端云端接线断言 |
| `tests/worker-itinerary-api.test.js` | Worker 纯函数/处理逻辑单测（不依赖真 KV 时用 mock） |
| `README.md` / `AGENTS.md` | 部署与口令说明 |

---

### Task 1: Seed 导出脚本 + Worker 脚手架与 API

**Files:**
- Create: `scripts/export_seed.py`
- Create: `workers/itinerary-api/package.json`
- Create: `workers/itinerary-api/wrangler.toml`
- Create: `workers/itinerary-api/src/index.js`
- Create: `workers/itinerary-api/src/seed.json`（由脚本生成）
- Create: `tests/worker-itinerary-api.test.js`

**Interfaces:**
- Produces: `handleRequest(request, env)` 行为：`GET/PUT /api/itinerary`、`POST /api/itinerary/reset`；KV key `itinerary:v1`；文档字段 `schemaVersion,version,updatedAt,title,points`

- [ ] **Step 1: 写 export_seed.py**

从 `coords.json` 生成与前端一致的 points（含 id/position），写出：

```json
{
  "schemaVersion": 1,
  "version": 1,
  "updatedAt": "<iso>",
  "title": "武汉 → 山东 9日旅行计划",
  "points": [ ... ]
}
```

到 `workers/itinerary-api/src/seed.json`。

- [ ] **Step 2: 写 Worker 测试（mock env.ITINERARY_KV）**

覆盖：无口令 PUT→401；错误口令→401；PUT 成功 version+1；错误 version→409；GET 空 KV 灌 seed；reset 恢复 seed 且 version+1；OPTIONS CORS。

- [ ] **Step 3: 实现 Worker `src/index.js`**

实现 CORS、三路由、口令比较（`env.EDIT_PASSWORD`）、JSON 读写 KV。

- [ ] **Step 4: 跑通 node 测试**

Run: `node --test tests/worker-itinerary-api.test.js`  
Expected: PASS

- [ ] **Step 5: Commit**（若用户要求再提交；默认可与后续任务合并提交）

---

### Task 2: 前端云端同步接入 generate_html.py

**Files:**
- Modify: `generate_html.py`（常量 `API_BASE`、存储/boot/reset/import/save 路径）
- Modify: `tests/test_generate_html.py`

**Interfaces:**
- Consumes: Worker API 如上
- Produces: 页面内 `cloudEnabled()`、`fetchRemoteItinerary()`、`pushRemoteItinerary(points)`、`ensureEditPassword()`、轮询、`remoteVersion`

- [ ] **Step 1: 失败测试断言**

断言 HTML 含：`API_BASE`、`X-Edit-Password`、`/api/itinerary`、`409`、`路线` 无关；含「将覆盖云端」类重置文案、`sessionStorage` 口令。

- [ ] **Step 2: 实现**

- 文件顶 `API_BASE = ""`（部署时填 Worker URL，无尾斜杠）
- `loadState` 改为缓存读取辅助；`boot` 异步：有 API 则 GET
- 所有原 `saveState` 成功路径：若 cloud → PUT；401 清口令重试；409 提示刷新
- `resetToBase` → POST reset
- `importJson` 成功后 PUT
- 5s 轮询 GET，version 变则重绘（编辑器打开时跳过替换）
- 口令：`sessionStorage` key `itinerary-edit-password`

- [ ] **Step 3: generate + unittest**

Run: `C:/Python314/python.exe generate_html.py`  
Run: `C:/Python314/python.exe -m unittest discover -s tests -v`  
Expected: OK

---

### Task 3: 文档

**Files:**
- Modify: `README.md`、`AGENTS.md`

- [ ] 写清：创建 KV、`wrangler deploy`、`wrangler secret put EDIT_PASSWORD`、填写 `API_BASE` 后重新 generate、两设备验证、大陆访问风险

---

## Spec coverage

| 规格项 | 任务 |
|--------|------|
| GET/PUT/reset | T1 |
| KV JSON + version | T1 |
| 口令头 | T1/T2 |
| CORS | T1 |
| 缓存兜底 | T2 |
| 轮询 | T2 |
| 恢复云端 | T2 |
| 导入导出 | T2 |
| 无 API_BASE 降级 | T2 |
| 部署说明 | T3 |

## Execution

用户已确认规格并要求开干 → **Inline Execution**（本会话直接做 Task 1–3）。
