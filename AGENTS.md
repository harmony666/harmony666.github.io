# AGENTS.md

## 项目定位

武汉→山东 9 日旅行的静态页面（GitHub Pages）+ 腾讯云轻量上的共享行程 API。

## 怎么跑

```powershell
C:/Python314/python.exe scripts/export_seed.py
# 如需更新 VPS seed：把 workers/.../seed.json 拷到 server/itinerary-api/src/seed.json
C:/Python314/python.exe generate_html.py
C:/Python314/python.exe -m http.server 8000
node --test tests/itinerary-core.test.js tests/worker-itinerary-api.test.js
C:/Python314/python.exe -m unittest discover -s tests -v
```

线上前端：https://harmony666.github.io/  
API：`server/itinerary-api/`（默认 `API_BASE=http://124.222.108.66:8787`）

## 技术栈

- Python 生成器：`generate_html.py` ← `coords.json` + `src/itinerary-core.js`
- 共享 API：Express（`server/itinerary-api/src/server.js`），数据文件 `data/itinerary.json`
- 写接口头：`X-Edit-Password`；服务端 `/etc/itinerary-api.env`
- 部署：`scripts/deploy_vps.py`（SSH + systemd）
- 存储键：`itinerary-editor-state-v1`（缓存）；口令：`sessionStorage`

## 目录与约定

- **现役数据**：`coords.json`；seed：`server/itinerary-api/src/seed.json`
- **生成物**：`itinerary.html`、`index.html`（须同步）
- **规格**：`docs/superpowers/specs/2026-07-22-cloud-shared-itinerary-design.md`（实现已从 CF 迁到 VPS，接口不变）
- 手机地图：禁止对地图容器 `display:none`（`far <= 0`）
- **不要**提交 SSH 密码、Master Key、口令明文到 git

## 当前状态 / 下一步

- VPS API 已部署；前端 `API_BASE` 指向 `http://124.222.108.66:8787`
- 预算 ¥5745.65；DAY1 济南不过夜
- 若外网不通：轻量控制台防火墙放行 TCP 8787
