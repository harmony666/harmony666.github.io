# 最终审查修复报告

## 修复范围

- 将分享入口改为静态托管 URL，并补充本地 HTTP 测试命令；`file://` 页面会明确提示腾讯 JSAPI GL 不受支持。
- 将时间轴与地图渲染解耦。地图脚本、Key 或初始化失败时仍选择首日并保留 DAY 标签、时间轴、新增表单、localStorage、导入、导出和恢复；地图选点会禁用或提示。
- Suggestion 保留 `pageSize: 8`，每次搜索先调用 `setRegion(city)`，再调用 `getSuggestions({ keyword })`。
- 点 ID 只接受非空字符串并保存 trim 后的值；数字、对象和数组均拒绝。
- 未改变损坏 localStorage 快照的保留策略。

## TDD RED 证据

先修改测试，再运行当前实现：

- `node --test tests/itinerary-core.test.js`
  - 退出码：1
  - 结果：7 项中 6 通过、1 失败。
  - 预期失败：`normalizePoints rejects non-string ids and trims valid string ids`，当前实现未拒绝数字 ID。
- `C:/Python314/python.exe -m unittest discover -s tests -v`
  - 退出码：1
  - 结果：25 项中 21 通过、4 失败。
  - 预期失败：缺少 `file://` 提示、Suggestion `setRegion` 调用、地图不可用时的时间轴解耦，以及时间轴卡片点击的地图 guard。

## 最终命令输出

- `node --test tests/itinerary-core.test.js`
  - 退出码：0
  - `tests 7`，`pass 7`，`fail 0`。
- `C:/Python314/python.exe -m unittest discover -s tests -v`
  - 退出码：0
  - `Ran 25 tests`，`OK`。
- `C:/Python314/python.exe generate_html.py`
  - 退出码：0
  - `OK v3 itinerary.html  total=¥5507  pois=43 days=9`。
- `git diff --check`
  - 退出码：0
  - 无输出。

## 文件

- `src/itinerary-core.js`
- `tests/itinerary-core.test.js`
- `tests/test_generate_html.py`
- `generate_html.py`
- `itinerary.html`
- `分享使用教程.md`
- `docs/superpowers/specs/2026-07-16-static-itinerary-editor-design.md`
- `.superpowers/sdd/final-fix-report.md`

## 提交

- 分支：`feature/static-itinerary-editor`
- 修复前基线：`f409f63`
- 新提交信息：`fix: harden itinerary map fallback`
- 本报告与全部修复由同一个新本地提交保存；该提交的最终哈希在提交完成后的最终回复中记录。未 amend，未 push。

## Concerns

- 自动化测试覆盖生成内容和关键控制流，未进行真实腾讯 Key、域名白名单及浏览器网络环境的端到端调用。
