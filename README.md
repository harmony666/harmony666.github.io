# 武汉 → 山东 · 山海九日行

单文件静态行程可视化/编辑器，部署于 GitHub Pages；可选 Cloudflare Worker 做**一份共享行程**的云端同步。

## 线上地址

- 前端：https://harmony666.github.io/
- 仓库：https://github.com/harmony666/harmony666.github.io

## 当前能力（2026-07-22）

- DAY1–9 时间轴 + 编号标记 + 驾车导航路线（失败回退直线）
- 添加/编辑行程点；按时间自动排序
- localStorage 缓存；导出/导入 JSON；恢复初始行程
- 可选云端：Workers + KV，写操作需共享口令，约 5 秒轮询同步
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

## 云端共享（Cloudflare，免费）

1. 安装并登录 wrangler，在 `workers/itinerary-api` 下创建 KV，把 id 填进 `wrangler.toml`。
2. 更新 seed：`C:/Python314/python.exe scripts/export_seed.py`
3. 设置口令：`npx wrangler secret put EDIT_PASSWORD`
4. 部署：`npx wrangler deploy`，得到 `https://itinerary-api.<subdomain>.workers.dev`
5. 在 `generate_html.py` 设 `API_BASE = "https://....workers.dev"`（无尾斜杠），再跑 `generate_html.py`，提交并推送 Pages。
6. 打开站点：读无需口令；首次保存会提示口令；「恢复初始」会**重置云端**（全员生效）。

大陆访问 Workers 可能偶发不稳；前端仍在 GitHub Pages。

## 重要说明

1. **权威行程数据是 `coords.json`**；改完后运行 `generate_html.py`，云端还需 `scripts/export_seed.py`。
2. 「恢复初始」在配置了 `API_BASE` 时重置云端；未配置时只清本机。
3. 推送 Pages 后等 Actions 完成；可用源码搜索 `5745.65` 验收。
4. 腾讯地图 Key 需 JSAPI / 搜索 / 驾车路线；域名白名单含 `harmony666.github.io`。

## 普通人怎么用

1. 打开 https://harmony666.github.io/
2. DAY 切换日期；手机可切「行程 / 地图」
3. 添加/编辑后若已开云端，会提示口令并同步
4. 导出 JSON 仍可作备份
