# AGENTS.md

## 项目定位

武汉→山东 9 日旅行：静态前端 + 共享 API，**同机部署在腾讯云轻量**（Nginx + Node）。不以 GitHub Pages / Cloudflare 为线上方案。

## 怎么跑

```powershell
C:/Python314/python.exe scripts/export_seed.py
C:/Python314/python.exe generate_html.py
# 部署：
#   $env:ITINERARY_SSH_PASSWORD='...'
#   python scripts/deploy_vps.py
# 改 seed 后若要覆盖线上共享文档：
#   curl.exe -X POST http://124.222.108.66/api/itinerary/reset -H "X-Edit-Password: ..."
C:/Python314/python.exe -m http.server 8000
node --test tests/itinerary-core.test.js
C:/Python314/python.exe -m unittest discover -s tests -v
```

线上：http://124.222.108.66/  
代码：`server/itinerary-api/`；Nginx：`server/nginx-itinerary.conf`

## 技术栈

- 生成器：`generate_html.py` ← `coords.json` + `src/itinerary-core.js`
- 前端：`index.html` → 服务器 `/var/www/itinerary`
- API：Express + 文件存储；`/etc/itinerary-api.env`
- 部署：`scripts/deploy_vps.py`（**不**自动覆盖服务器 `itinerary.json`，需 reset/恢复初始）
- 写接口头：`X-Edit-Password`
- 地图：百度 JS API（AK 在 `generate_html.py`）；同坐标编号错位；编辑预览钉/虚线；路线箭头

## 目录与约定

- **现役数据**：`coords.json`；seed：`server/itinerary-api/src/seed.json`
- **生成物**：`index.html`（须 generate 后再 deploy）
- **规格入口**：`docs/superpowers/specs/2026-07-22-cloud-shared-itinerary-design.md`（云端）；UI 基线见 `2026-07-16-static-itinerary-editor-design.md`
- 手机地图：禁止对地图容器 `display:none`（`far <= 0`）
- **不要**提交 SSH 密码、口令明文到 git
- **已废弃**：Cloudflare Workers（目录勿再引入）

## 当前状态

- 现役：`124.222.108.66`；`API_BASE=http://124.222.108.66`
- 预算约 ¥5745.65；**49** 个行程点（以 `coords.json` 为准）；DAY1 济南不过夜
- DAY5：大黑山岛早班 + 蓬莱阁；DAY6：养马岛 + 市区；DAY7：南山/西炮台后回威海还车
