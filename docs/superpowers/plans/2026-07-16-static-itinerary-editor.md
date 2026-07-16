# Static Itinerary Editor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有行程页改成支持编号箭头路线、新增点、拖拽排序、本地自动保存及 JSON 导入导出的单文件应用。

**Architecture:** 把可测试的状态处理放入 `src/itinerary-core.js`，由 `generate_html.py` 内联到最终 HTML；浏览器交互仍由生成器中的应用脚本负责。`localStorage` 保存完整快照，JSON 文件负责备份和跨设备分享。

**Tech Stack:** Python 3.14、原生 JavaScript、Node.js 24 内置测试器、腾讯地图 JSAPI GL、HTML5 Drag and Drop、localStorage。

## Global Constraints

- 最终交付给普通使用者的运行文件只有 `itinerary.html`；分享修改结果时另附导出的 JSON。
- 不引入前端框架、构建工具、数据库或后端服务。
- 每日标记固定像素大小、不聚合；缩小时允许相互遮挡。
- 用户拖拽后的顺序优先于时间；新点首次按时间插入。
- 导入失败不得改变现有内存数据或 localStorage。
- 当前目录不是 Git 仓库，不创建提交；每个任务以测试通过作为检查点。

---

### Task 1: 可测试的行程状态核心

**Files:**
- Create: `src/itinerary-core.js`
- Create: `tests/itinerary-core.test.js`

**Interfaces:**
- Produces: `ItineraryCore.normalizePoints(points) -> Point[]`
- Produces: `ItineraryCore.insertPointByTime(points, point) -> Point[]`
- Produces: `ItineraryCore.reorderDay(points, day, orderedIds) -> Point[]`
- Produces: `ItineraryCore.createExport(points, title, now) -> ExportDocument`
- Produces: `ItineraryCore.parseImport(text) -> ExportDocument`
- Produces: `ItineraryCore.buildNumberedPinSvg(number, color) -> string`

- [ ] **Step 1: 写状态核心的失败测试**

使用 `node:test` 覆盖稳定 ID、按时间插入、拖拽重排、导入校验和 SVG 编号：

```javascript
const test = require('node:test');
const assert = require('node:assert/strict');
const Core = require('../src/itinerary-core.js');

const point = (id, day, time, position) => ({
  id, day, time, position, title: id, name: id, desc: '',
  city: '威海', cat: 'scenic', lat: 37.5, lng: 122.1, source: 'seed'
});

test('insertPointByTime inserts after equal times and normalizes positions', () => {
  const result = Core.insertPointByTime(
    [point('a', 3, '09:00', 1), point('b', 3, '11:00', 2)],
    point('c', 3, '09:00', 99)
  );
  assert.deepEqual(result.map(p => p.id), ['a', 'c', 'b']);
  assert.deepEqual(result.map(p => p.position), [1, 2, 3]);
});

test('reorderDay rejects incomplete id lists', () => {
  assert.throws(
    () => Core.reorderDay([point('a', 2, '09:00', 1), point('b', 2, '10:00', 2)], 2, ['a']),
    /完整/
  );
});

test('parseImport rejects invalid coordinates without returning partial data', () => {
  const data = Core.createExport([point('a', 1, '09:00', 1)], '旅行', new Date(0));
  data.points[0].lat = 100;
  assert.throws(() => Core.parseImport(JSON.stringify(data)), /纬度/);
});

test('buildNumberedPinSvg contains visible sequence number', () => {
  assert.match(Core.buildNumberedPinSvg(12, '#0aa3ff'), />12</);
});
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `node --test tests/itinerary-core.test.js`  
Expected: FAIL，提示 `src/itinerary-core.js` 不存在。

- [ ] **Step 3: 实现最小状态核心**

使用 UMD 风格导出，浏览器挂载 `window.ItineraryCore`，Node 使用 `module.exports`。实现：

```javascript
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.ItineraryCore = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  const CATEGORIES = new Set(['scenic', 'food', 'culture', 'shop', 'transit', 'hotel']);
  const TIME_RE = /^([01]\d|2[0-3]):[0-5]\d$/;

  function validatePoint(raw) {
    const p = { ...raw, day: Number(raw.day), position: Number(raw.position),
      lat: Number(raw.lat), lng: Number(raw.lng) };
    if (!p.id || !String(p.id).trim()) throw new Error('点 ID 不能为空');
    if (!Number.isInteger(p.day) || p.day < 1 || p.day > 9) throw new Error('日期无效');
    if (!TIME_RE.test(p.time)) throw new Error('时间格式无效');
    if (!CATEGORIES.has(p.cat)) throw new Error('类别无效');
    if (!Number.isFinite(p.lat) || p.lat < -90 || p.lat > 90) throw new Error('纬度无效');
    if (!Number.isFinite(p.lng) || p.lng < -180 || p.lng > 180) throw new Error('经度无效');
    return p;
  }

  function normalizePoints(points) {
    const valid = points.map(validatePoint);
    if (new Set(valid.map(p => p.id)).size !== valid.length) throw new Error('点 ID 必须唯一');
    const output = [];
    for (let day = 1; day <= 9; day++) {
      valid.filter(p => p.day === day)
        .sort((a, b) => a.position - b.position || a.time.localeCompare(b.time))
        .forEach((p, index) => output.push({ ...p, position: index + 1 }));
    }
    return output;
  }

  function insertPointByTime(points, rawPoint) {
    const point = validatePoint(rawPoint);
    const other = points.filter(p => p.day !== point.day);
    const day = points.filter(p => p.day === point.day);
    let index = day.length;
    for (let i = day.length - 1; i >= 0; i--) {
      if (day[i].time <= point.time) { index = i + 1; break; }
      index = 0;
    }
    day.splice(index, 0, point);
    return normalizePoints(other.concat(day.map((p, i) => ({ ...p, position: i + 1 }))));
  }

  function reorderDay(points, day, ids) {
    const selected = points.filter(p => p.day === day);
    if (ids.length !== selected.length || new Set(ids).size !== ids.length ||
        ids.some(id => !selected.some(p => p.id === id))) throw new Error('排序 ID 必须完整且唯一');
    const byId = new Map(selected.map(p => [p.id, p]));
    return normalizePoints(points.filter(p => p.day !== day)
      .concat(ids.map((id, i) => ({ ...byId.get(id), position: i + 1 }))));
  }

  function createExport(points, title, now) {
    return { schemaVersion: 1, exportedAt: now.toISOString(), title, points: normalizePoints(points) };
  }

  function parseImport(text) {
    const doc = JSON.parse(text);
    if (!doc || doc.schemaVersion !== 1 || !Array.isArray(doc.points)) throw new Error('不支持的行程文件格式');
    return { ...doc, points: normalizePoints(doc.points) };
  }

  function buildNumberedPinSvg(number, color) {
    return `<svg xmlns="http://www.w3.org/2000/svg" width="36" height="42"><path fill="${color}" stroke="#fff" stroke-width="2" d="M18 1C8.6 1 2 8 2 17c0 12 16 24 16 24s16-12 16-24C34 8 27.4 1 18 1z"/><text x="18" y="22" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">${number}</text></svg>`;
  }

  return { normalizePoints, insertPointByTime, reorderDay, createExport, parseImport, buildNumberedPinSvg };
});
```

- [ ] **Step 4: 运行核心测试**

Run: `node --test tests/itinerary-core.test.js`  
Expected: 全部 PASS。

---

### Task 2: 生成器接入状态核心、编号标记和箭头路线

**Files:**
- Modify: `generate_html.py`
- Create: `tests/test_generate_html.py`
- Regenerate: `itinerary.html`

**Interfaces:**
- Consumes: `src/itinerary-core.js`
- Produces: HTML 常量 `BASE_POIS`，每个点含稳定 `id` 和 `position`
- Produces: `renderMap(day, list)` 使用编号 SVG 和 `showArrow`

- [ ] **Step 1: 写生成结果的失败测试**

```python
import pathlib
import subprocess
import unittest

ROOT = pathlib.Path(__file__).parents[1]

class GeneratedHtmlTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(["C:/Python314/python.exe", "generate_html.py"], cwd=ROOT, check=True)
        cls.html = (ROOT / "itinerary.html").read_text(encoding="utf-8")

    def test_inlines_core_and_service_library(self):
        self.assertIn("root.ItineraryCore", self.html)
        self.assertIn("libraries=service", self.html)

    def test_route_has_arrows_and_numbered_pins(self):
        self.assertIn("showArrow: true", self.html)
        self.assertIn("buildNumberedPinSvg", self.html)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `C:/Python314/python.exe -m unittest tests/test_generate_html.py -v`  
Expected: FAIL，缺少核心脚本、service 库和箭头设置。

- [ ] **Step 3: 修改生成器**

- 用 `pathlib.Path(__file__).parent` 读取 `coords.json` 和 `src/itinerary-core.js`，避免依赖启动目录。
- 为基础点生成 `seed-{day}-{num}` ID，并把 `num` 改为 `position`。
- 将地图脚本改为 `...gljs?v=1&key=__KEY__&libraries=service`。
- 在应用脚本前内联核心脚本。
- `renderMap` 为每个点创建 `data:image/svg+xml` 编号样式；重新创建或更新 `MultiMarker` 样式和 geometries。
- 使用 `new TMap.PolylineStyle({ width: 7, color: '#ff5a5f', borderWidth: 3, borderColor: '#ffffff', showArrow: true, arrowOptions: { width: 8, height: 5, space: 60 } })`。
- `selectDay` 每次都从当前状态按 `position` 取点、重画标记和路线并执行 `fitBounds`。
- 0 个点清空图层，1 个点只绘制标记并居中，不绘制路线。

- [ ] **Step 4: 运行生成器测试**

Run: `C:/Python314/python.exe -m unittest tests/test_generate_html.py -v`  
Expected: 全部 PASS。

---

### Task 3: localStorage、导入导出和恢复初始行程

**Files:**
- Modify: `generate_html.py`
- Modify: `tests/test_generate_html.py`
- Regenerate: `itinerary.html`

**Interfaces:**
- Produces: `loadState() -> Point[]`
- Produces: `saveState(points) -> boolean`
- Produces: `exportJson()`
- Produces: `importJson(file)`
- Produces: `resetToBase()`

- [ ] **Step 1: 扩充失败测试**

断言生成 HTML 包含：

```python
self.assertIn("itinerary-editor-state-v1", self.html)
self.assertIn('id="exportBtn"', self.html)
self.assertIn('id="importInput"', self.html)
self.assertIn('id="resetBtn"', self.html)
self.assertIn("ItineraryCore.parseImport", self.html)
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `C:/Python314/python.exe -m unittest tests/test_generate_html.py -v`  
Expected: FAIL，缺少保存和导入导出控件。

- [ ] **Step 3: 实现持久化和文件交互**

- 顶部操作区增加“添加点”“导出 JSON”“导入 JSON”“恢复初始行程”和保存状态。
- `loadState` 解析 localStorage；无数据或数据无效时回退到 `BASE_POIS` 并提示。
- `saveState` 写入 `{ schemaVersion: 1, savedAt, points }`；捕获配额和安全异常。
- 导出使用 `Blob`、`URL.createObjectURL` 和临时 `<a download>`。
- 导入先读取文本并调用 `ItineraryCore.parseImport`，确认替换后才更新状态和 localStorage。
- 恢复操作二次确认后深拷贝 `BASE_POIS`、清除存储并重画。

- [ ] **Step 4: 运行自动测试**

Run: `node --test tests/itinerary-core.test.js`  
Expected: 全部 PASS。  
Run: `C:/Python314/python.exe -m unittest tests/test_generate_html.py -v`  
Expected: 全部 PASS。

---

### Task 4: 新增点和拖拽排序交互

**Files:**
- Modify: `generate_html.py`
- Modify: `tests/test_generate_html.py`
- Regenerate: `itinerary.html`

**Interfaces:**
- Consumes: `ItineraryCore.insertPointByTime`
- Consumes: `ItineraryCore.reorderDay`
- Produces: `openPointEditor()`
- Produces: `beginMapPick()`
- Produces: `searchPlaces(keyword, city)`
- Produces: `submitPoint(formData)`

- [ ] **Step 1: 扩充失败测试**

```python
self.assertIn('id="pointEditor"', self.html)
self.assertIn("new TMap.service.Suggestion", self.html)
self.assertIn("crypto.randomUUID", self.html)
self.assertIn("dragstart", self.html)
self.assertIn("ItineraryCore.reorderDay", self.html)
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `C:/Python314/python.exe -m unittest tests/test_generate_html.py -v`  
Expected: FAIL，缺少新增点和拖拽交互。

- [ ] **Step 3: 实现新增点面板**

- 表单字段：DAY、时间、标题、描述、城市、类别、纬度、经度。
- 地图点击选点时只注册一个临时点击处理器，选中后立即退出选点模式。
- 搜索使用 `TMap.service.Suggestion({ pageSize: 8 })`，按城市限定；选择候选项后填入名称、城市和坐标。
- 提交时生成 UUID，调用 `insertPointByTime`，保存成功后关闭面板并切换到目标 DAY。
- 地图或搜索失败时保留已填写内容。

- [ ] **Step 4: 实现拖拽排序**

- 每张卡片设置 `draggable="true"` 和稳定 `data-id`。
- `dragstart` 记录点 ID；`dragover` 计算前后落点；`drop` 读取当前 DOM ID 顺序。
- 调用 `reorderDay` 后保存并重新执行 `selectDay(curDay)`。
- 移动端不支持原生拖拽时保持查看和新增功能，不额外引入拖拽库。

- [ ] **Step 5: 运行全部自动测试**

Run: `node --test tests/itinerary-core.test.js`  
Expected: 全部 PASS。  
Run: `C:/Python314/python.exe -m unittest tests/test_generate_html.py -v`  
Expected: 全部 PASS。

---

### Task 5: 浏览器验收和分享教程

**Files:**
- Create: `分享使用教程.md`
- Regenerate: `itinerary.html`

**Interfaces:**
- Produces: 最终可分享的 `itinerary.html`
- Produces: 面向普通使用者的分享、导入、备份和腾讯 Key 配置说明

- [ ] **Step 1: 生成最终 HTML 并运行全套测试**

Run: `C:/Python314/python.exe generate_html.py`  
Expected: 输出 `OK`，包含点数和天数。  
Run: `node --test tests/itinerary-core.test.js`  
Expected: 全部 PASS。  
Run: `C:/Python314/python.exe -m unittest discover -s tests -v`  
Expected: 全部 PASS。

- [ ] **Step 2: 浏览器手动验收**

- 依次点击 DAY 1、DAY 2、DAY 3，确认地图显示对应日期的全部编号点和箭头路线。
- 放大、缩小地图，确认标记尺寸固定且不聚合。
- 用地图点击新增点，刷新后确认仍存在。
- 用地点搜索新增点，确认候选位置和保存结果正确。
- 拖拽卡片，确认编号、路线和刷新后的顺序一致。
- 导出 JSON，恢复初始行程，再导入 JSON，确认完整恢复。
- 导入损坏 JSON，确认当前行程不变。

- [ ] **Step 3: 编写分享教程**

教程明确说明：

1. 分享初始行程只需发送 `itinerary.html`。
2. 分享修改结果需同时发送 `itinerary.html` 和导出的 JSON。
3. 接收者打开 HTML 后点击“导入 JSON”。
4. 每位使用者的数据默认互不同步。
5. 浏览器数据清理或换设备前应先导出 JSON。
6. 腾讯地图需要联网；正式静态托管需使用长期 Key 并配置域名白名单。
7. 可将 `itinerary.html` 改名为 `index.html` 上传到静态托管服务。

- [ ] **Step 4: 最终检查产物**

确认根目录存在并可读：

- `itinerary.html`
- `分享使用教程.md`

确认 `itinerary.html` 不依赖本地 `src`、`tests`、`coords.json` 或 Python 文件即可运行。
