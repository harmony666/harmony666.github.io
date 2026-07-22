# 武汉 → 山东 · 山海九日行

单文件静态行程可视化/编辑器；**前端 + 共享 API 均部署在腾讯云轻量**。

## 线上地址

- 站点：http://124.222.108.66/
- API：http://124.222.108.66/api/itinerary（写需共享口令）
- 源码：https://github.com/harmony666/harmony666.github.io（仅存代码，非线上入口）

## 当前能力（2026-07-22）

- DAY1–9 时间轴 + 编号标记 + 驾车导航路线（失败回退直线）
- 添加/编辑行程点；按时间自动排序
- localStorage 缓存；导出/导入 JSON；恢复初始行程
- 云端共享：同机 Nginx 静态页 + Node API，约 5 秒轮询同步
- 初始行程预算约 **¥5745.65**（43 个行程点）

## 本地开发

```powershell
C:/Python314/python.exe generate_html.py
C:/Python314/python.exe -m http.server 8000
# http://localhost:8000/
```

`generate_html.py` 顶部 `API_BASE = ""` 时为纯本机模式；线上为 `http://124.222.108.66`。

测试：

```powershell
node --test tests/itinerary-core.test.js
C:/Python314/python.exe -m unittest discover -s tests -v
```

## 部署到腾讯云轻量

1. 改 `coords.json` 后：`python scripts/export_seed.py`，再 `python generate_html.py`
2. 设置 `$env:ITINERARY_SSH_PASSWORD`，运行 `python scripts/deploy_vps.py`
3. 脚本更新：Node API（systemd）、Nginx（静态页 + `/api` 反代）
4. 控制台防火墙放行 **TCP 80**
5. 打开 http://124.222.108.66/ ：读公开；保存时输入共享口令

规格详见 `docs/superpowers/specs/2026-07-22-cloud-shared-itinerary-design.md`。

## 重要说明

1. **权威行程数据是 `coords.json`**；改完后更新 seed 并 generate，再 deploy。
2. 「恢复初始」在配置了 `API_BASE` 时重置云端。
3. 腾讯地图 Key 域名白名单需含 `124.222.108.66`。
4. 不要把 SSH 密码或编辑口令提交进 git。

## 普通人怎么用

1. 打开 http://124.222.108.66/
2. DAY 切换日期；手机可切「行程 / 地图」
3. 添加/编辑后输入共享口令即可云端同步
4. 导出 JSON 仍可作备份
