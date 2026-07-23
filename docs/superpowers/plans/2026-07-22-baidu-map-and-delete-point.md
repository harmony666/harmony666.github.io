# 删除点 + 百度地图 Implementation Plan

> **状态：已完成（历史计划，可删）** — 实现已进主代码与 `2026-07-22-baidu-map-and-delete-point-design.md`。

> **For agentic workers:** 按任务顺序 TDD；每任务可独立验证。

**Goal:** 行程卡片可确认删除；地图从腾讯换成百度 JS API（AK 已提供）。

**Tech Stack:** 现有 `src/itinerary-core.js`、`generate_html.py`、Node/Python 测试、VPS deploy。

## 文件

| 文件 | 职责 |
|------|------|
| `src/itinerary-core.js` | `deletePoint` |
| `tests/itinerary-core.test.js` | 删除单测 |
| `generate_html.py` | UI 删除 + 百度地图 |
| `tests/test_generate_html.py` | 断言删除按钮与百度脚本 |
| `README.md` / `AGENTS.md` / 静态规格 | 腾讯→百度 |

## Task 1: deletePoint（TDD）

- [ ] 写失败测试：删存在点、删不存在抛错、重算 position
- [ ] 实现 `deletePoint` 并导出
- [ ] `node --test tests/itinerary-core.test.js` 通过

## Task 2: HTML 删除按钮

- [ ] 时间轴加删除；confirm 后调用 core + persist
- [ ] 生成 HTML；unittest 含删除相关字符串

## Task 3: 百度地图

- [ ] 替换 KEY 与 script URL
- [ ] 重写 mapReady / init / render / driving / search / pick / fit
- [ ] GCJ→BD 转换辅助函数
- [ ] 更新文档；generate；deploy VPS

## 验证

```powershell
node --test tests/itinerary-core.test.js
python -m unittest discover -s tests -v
python generate_html.py
# 浏览器打开站点：删点确认；地图加载
```
