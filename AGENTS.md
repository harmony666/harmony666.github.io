# AGENTS.md

## 项目定位

武汉→山东 9 日旅行的**无后端单文件静态页面**（GitHub Pages），可选 **Cloudflare Worker + KV** 做一份共享行程的云端同步。

## 怎么跑

```powershell
C:/Python314/python.exe scripts/export_seed.py
C:/Python314/python.exe generate_html.py
C:/Python314/python.exe -m http.server 8000
node --test tests/itinerary-core.test.js tests/worker-itinerary-api.test.js
C:/Python314/python.exe -m unittest discover -s tests -v
```

线上前端：https://harmony666.github.io/  
Worker：`workers/itinerary-api/`（`API_BASE` 留空则纯本地）

## 技术栈

- Python 生成器：`generate_html.py` ← `coords.json` + `src/itinerary-core.js`
- 可选 API：Workers（`src/app.js` + `src/index.js`），KV key `itinerary:v1`
- 写接口头：`X-Edit-Password`；secret：`EDIT_PASSWORD`
- 存储键：`itinerary-editor-state-v1`（缓存）；口令：`sessionStorage`

## 目录与约定

- **现役数据**：`coords.json`；云端 seed：`scripts/export_seed.py` → `workers/.../seed.json`
- **生成物**：`itinerary.html`、`index.html`（须同步）
- **规格**：`docs/superpowers/specs/2026-07-22-cloud-shared-itinerary-design.md`
- 手机地图：禁止对地图容器 `display:none`（`far <= 0`）
- 口令与 wrangler token **不要**提交进 git

## 当前状态 / 下一步

- 代码已支持云端接线；需你在 Cloudflare 创建 KV、设 secret、填 `API_BASE` 后 deploy
- 预算 ¥5745.65；DAY1 济南不过夜
