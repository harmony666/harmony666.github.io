# 添加预览 + 叠点错位 Implementation Plan

> **状态：已完成（历史计划，可删）** — 实现已进主代码与 `2026-07-23-add-preview-and-marker-offset-design.md`。

> **For agentic workers:** 按任务顺序；纯逻辑优先 TDD。

**Goal:** 编辑时地图可见并显示临时钉/虚线插入预览；同坐标编号像素错开。

**Tech Stack:** `src/itinerary-core.js`、`generate_html.py`、现有 Node/Python 测试、VPS deploy。

## 文件

| 文件 | 职责 |
|------|------|
| `src/itinerary-core.js` | `computeMarkerPixelOffsets`、`findTimeNeighbors` |
| `tests/itinerary-core.test.js` | 上述单测 |
| `generate_html.py` | 左/半屏表单、预览叠加、renderMap 应用 offset |
| `tests/test_generate_html.py` | 关键 CSS/文案断言 |
| 规格 | 已写 `docs/superpowers/specs/2026-07-23-add-preview-and-marker-offset-design.md` |

## Task 1: Core 偏移与邻居（TDD）

- [ ] 测试：单点 offset 0；两点同坐标左右错开；不同坐标互不影响
- [ ] 测试：`findTimeNeighbors` 插在中间 / 最早 / 最晚；编辑时排除自身
- [ ] 实现并导出；`node --test tests/itinerary-core.test.js` 通过

## Task 2: renderMap 应用错位

- [ ] `renderMap` 用 `computeMarkerPixelOffsets` 设置 `BMap.Marker` 的 `offset`
- [ ] 路线仍用真实 lat/lng

## Task 3: 编辑器布局

- [ ] 桌面：overlay `justify-content:flex-start`，透明底，面板可点、地图可点
- [ ] 手机：底部半屏抽屉；打开编辑时切 `mobile-map`

## Task 4: 预览钉 + 虚线

- [ ] 监听 day/time/lat/lng/category；更新临时 Marker + 虚线 Polyline
- [ ] `closePointEditor` 清除预览；可选插入位置文案
- [ ] generate + unittest + 部署

## 验证

```powershell
node --test tests/itinerary-core.test.js
python -m unittest discover -s tests -v
python generate_html.py
```
