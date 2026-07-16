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
