# 删除行程点 + 百度地图（设计）

> 日期：2026-07-22  
> 状态：已确认执行（用户 ok）  
> 范围：编辑器 UI / `ItineraryCore` / `generate_html.py`；云端 API 契约不变

## 决策

| 项 | 选择 |
|----|------|
| 删除 | 卡片「删除」+ `confirm` 二次确认后删除并 `persistPoints` |
| 地图 | 百度 JS API；AK 注入生成物；替换腾讯 TMap |
| 坐标 | 存储仍为现有 GCJ-02 数值；展示/检索/驾车时转 BD-09 |

## 核心

- `ItineraryCore.deletePoint(points, id)`：不存在则抛错；否则过滤后 `normalizePoints`
- 时间轴：编辑旁删除按钮；确认文案含 title

## 百度能力映射

- Map / Marker / Polyline / InfoWindow / 点击选点
- 驾车：`DrivingRoute`（失败直线）
- 搜索：`Autocomplete` 或 `LocalSearch`
- Key 白名单：`124.222.108.66`、`localhost:8000`
