# 武汉 → 山东 · 山海九日行

单文件静态行程可视化/编辑器，部署于 GitHub Pages；共享行程 API 跑在腾讯云轻量（大陆可访问）。

## 线上地址

- 前端：https://harmony666.github.io/
- 仓库：https://github.com/harmony666/harmony666.github.io
- API：`http://124.222.108.66:8787`（`GET/PUT /api/itinerary`，写需口令）

## 当前能力（2026-07-22）

- DAY1–9 时间轴 + 编号标记 + 驾车导航路线（失败回退直线）
- 添加/编辑行程点；按时间自动排序
- localStorage 缓存；导出/导入 JSON；恢复初始行程
- 云端共享：腾讯云 VPS 上的 Node API，写操作需共享口令，约 5 秒轮询同步
- 初始行程预算约 **¥5745.65**（43 个行程点）

## 本地开发（纯前端）

```powershell
C:/Python314/python.exe generate_html.py
C:/Python314/python.exe -m http.server 8000
# http://localhost:8000/itinerary.html
```

`generate_html.py` 顶部 `API_BASE = ""` 时为纯本机模式。

测试：

```powershell
node --test tests/itinerary-core.test.js tests/worker-itinerary-api.test.js
C:/Python314/python.exe -m unittest discover -s tests -v
```

## 云端共享（腾讯云轻量）

1. 服务器代码：`server/itinerary-api/`（Express + 本地 JSON 文件）
2. 部署：设置环境变量后运行 `python scripts/deploy_vps.py`
3. 在 `generate_html.py` 设 `API_BASE = "http://<公网IP>:8787"`，再跑 `generate_html.py`，推送 Pages
4. 腾讯云轻量控制台 → 防火墙 → 放行 **TCP 8787**（若外网不通）
5. 打开站点：读无需口令；首次保存提示口令；「恢复初始」会重置云端

历史备选：`workers/itinerary-api/`（Cloudflare Workers）在大陆常不可用，已不作为默认方案。

## 重要说明

1. **权威行程数据是 `coords.json`**；改完后运行 `generate_html.py`，并更新 `server/itinerary-api/src/seed.json`（可用 `scripts/export_seed.py` 再拷贝）。
2. 「恢复初始」在配置了 `API_BASE` 时重置云端；未配置时只清本机。
3. 推送 Pages 后等 Actions 完成；可用源码搜索 `5745.65` 验收。
4. 腾讯地图 Key 需 JSAPI / 搜索 / 驾车路线；域名白名单含 `harmony666.github.io`。

## 普通人怎么用

1. 打开 https://harmony666.github.io/
2. DAY 切换日期；手机可切「行程 / 地图」
3. 添加/编辑后若已开云端，会提示口令并同步
4. 导出 JSON 仍可作备份
