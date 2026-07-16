# Task 2 报告

## 状态

已完成，未推送。

## 修改文件

- `generate_html.py`
- `tests/test_generate_html.py`
- `itinerary.html`

## RED 证据

先运行 `C:/Python314/python.exe -m unittest tests/test_generate_html.py -v`。
测试结果为 `FAILED (failures=4, errors=1)`；缺失核心脚本、service 参数、BASE_POIS/稳定 ID、编号箭头逻辑及父目录运行支持，符合预期。

## 最终测试结果

- `C:/Python314/python.exe -m unittest tests/test_generate_html.py -v`：5 tests，全部通过。
- `node --test tests/itinerary-core.test.js`：6 tests，全部通过。
- `ReadLints`：无 lint 错误。

## 提交哈希

实现提交：`13ec71d`（`feat: add numbered map routes`）。

## 自检

- 使用 `Path(__file__).parent` 读取输入和核心脚本，并将 HTML 输出到项目根目录。
- 基础点生成稳定 ID 和 `position`，运行时经 `ItineraryCore.normalizePoints` 初始化。
- 核心脚本位于应用脚本之前，地图 URL 包含 `libraries=service`。
- DAY 切换按 position 排序，重建时间轴、固定 36×42 编号标记和箭头路线。
- 0 点清空覆盖物，1 点仅标记并居中，2 点及以上绘制完整路线并 fitBounds。
- 保留卡片点击、信息窗、类别图例和住宿信息。

## concerns

- 未进行联网腾讯地图浏览器手工验收；静态代码和自动化生成测试已覆盖本任务要求。

## 审查修复（2026-07-16）

修复提交：`42367fb`（`fix: instantiate map marker styles`）。

### 修复说明

- 动态编号样式改为逐个通过 `new TMap.MarkerStyle({...})` 实例化，再传给 `TMap.MultiMarker`。
- `renderMap` 在 0 点和 1 点分支提前返回前统一关闭旧信息窗，并将 `infoWin` 清空。
- 生成测试增加 MarkerStyle 实例断言，以及信息窗清理必须早于 0 点分支的顺序断言。
- 重新生成 `itinerary.html`。

### RED 证据

命令：

`C:/Python314/python.exe -m unittest tests/test_generate_html.py -v`

完整结果：

```text
test_base_points_have_stable_ids_and_positions ... ok
test_generator_works_from_project_parent_directory ... ok
test_inlines_core_and_service_library ... ok
test_render_map_closes_info_window_before_empty_day_returns ... FAIL
test_render_map_handles_zero_and_one_point_days ... ok
test_route_has_numbered_pins_and_arrows ... FAIL

Ran 6 tests in 0.278s
FAILED (failures=2)
```

两个新增断言分别因信息窗清理位于 0 点提前返回之后，以及编号样式仍为普通对象而失败，符合预期。

### 修复后测试

命令：

`C:/Python314/python.exe -m unittest tests/test_generate_html.py -v`

完整结果：

```text
test_base_points_have_stable_ids_and_positions ... ok
test_generator_works_from_project_parent_directory ... ok
test_inlines_core_and_service_library ... ok
test_render_map_closes_info_window_before_empty_day_returns ... ok
test_render_map_handles_zero_and_one_point_days ... ok
test_route_has_numbered_pins_and_arrows ... ok

Ran 6 tests in 0.307s
OK
```

命令：

`node --test tests/itinerary-core.test.js`

完整结果：

```text
✔ insertPointByTime inserts after equal times and normalizes positions
✔ reorderDay rejects incomplete id lists
✔ parseImport rejects invalid coordinates without returning partial data
✔ buildNumberedPinSvg contains visible sequence number
✔ parseImport rejects duplicate ids, invalid day, time, cat, and lng
✔ reorderDay does not change order of other days
ℹ tests 6
ℹ suites 0
ℹ pass 6
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 241.4049
```
