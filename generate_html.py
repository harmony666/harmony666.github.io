#!/usr/bin/env python3
# 读取 coords.json（完整行程含酒店）→ 生成内联 HTML
import json
from pathlib import Path

ROOT = Path(__file__).parent

KEY = "bzv7nHMM4yqiTtyQfsxAU6u8m2RutOkB"
# 云端 API 根 URL（无尾斜杠）。留空则纯本地 localStorage 模式。
# 腾讯云 Nginx 反代 /api 时用站点根，例如 http://124.222.108.66
API_BASE = "http://124.222.108.66"
data = json.loads((ROOT / "coords.json").read_text(encoding="utf-8"))
core_js = (ROOT / "src" / "itinerary-core.js").read_text(encoding="utf-8")

budgets = {
    "交通": 1117 + 346 + 577,
    "住宿": 370 + 601.65 + 108,
    "租车": 1126,
    "吃饭门票": 1500,
}
total = round(sum(budgets.values()), 2)

# 住宿细分（右侧住宿卡片展示）
hotel_meta = {
    "威海住宿·山大路": {
        "addr": "环翠区高技术产业开发区山大路15-6号(建设银行旁，山大南门对面)",
        "price": "¥370/2晚",
        "status": "已预订",
    },
    "威海住宿·山大路(出发)": {"addr": "山大路15-6号", "price": "—", "status": "酒店出发"},
    "威海住宿·山大路(回宿)": {"addr": "山大路15-6号", "price": "—", "status": "回宿"},
    "威海住宿·山大路(退房)": {"addr": "山大路15-6号", "price": "—", "status": "退房"},
    "烟台住宿·青年南路": {
        "addr": "烟台市芝罘区世回尧街道青年南路169号",
        "price": "¥601.65/3晚",
        "status": "已预订",
    },
    "烟台住宿·青年南路(出发)": {"addr": "青年南路169号", "price": "—", "status": "酒店出发"},
    "烟台住宿·青年南路(回宿)": {"addr": "青年南路169号", "price": "—", "status": "回宿"},
    "烟台住宿·青年南路(退房)": {"addr": "青年南路169号", "price": "—", "status": "退房"},
    "早起出发赴蓬莱": {"addr": "青年南路169号", "price": "—", "status": "赶船出发"},
    "返程回烟台": {"addr": "青年南路169号", "price": "—", "status": "回宿"},
    "威海住宿·时代小驿": {
        "addr": "时代小驿民宿(馨海家苑)",
        "price": "¥108",
        "status": "已预订",
    },
    "威海住宿·时代小驿(出发)": {
        "addr": "时代小驿民宿(馨海家苑)",
        "price": "—",
        "status": "赶车出发",
    },
}
hotels_js = json.dumps(hotel_meta, ensure_ascii=False)

day_meta = {
    1: ("8月1日", "济南 · 一日泉城夜赶火车"),
    2: ("8月2日", "威海 · 到站取车登岛入住"),
    3: ("8月3日", "威海 · 东线海角少回头"),
    4: ("8月4日", "威海→烟台 · 跨城入住"),
    5: ("8月5日", "烟台 · 大黑山岛+蓬莱阁"),
    6: ("8月6日", "烟台 · 养马岛+市区海滨"),
    7: ("8月7日", "烟台补景点→威海还车"),
    8: ("8月8日", "威海 · 站旁启程"),
    9: ("8月9日", "武汉 · 平安到家"),
}
days = sorted(day_meta.keys())

groups = {}
for p in data:
    groups.setdefault(p["day"], []).append(p)
for d, lst in groups.items():
    for i, p in enumerate(lst, 1):
        p["position"] = i
        p["id"] = f"seed-{d}-{i}"

cats = {
    "scenic":  {"label": "景点", "color": "#0aa3ff", "soft": "#e6f6ff"},
    "food":    {"label": "美食", "color": "#ff6b6b", "soft": "#ffecec"},
    "culture": {"label": "文化", "color": "#7b61ff", "soft": "#f0ebff"},
    "shop":    {"label": "购物", "color": "#20c997", "soft": "#e7fbf4"},
    "transit": {"label": "交通", "color": "#8898aa", "soft": "#eef1f5"},
    "hotel":   {"label": "住宿", "color": "#f59e0b", "soft": "#fff4dc"},
}

pois_js = json.dumps(
    [{k: p.get(k) for k in ("id", "day", "cat", "time", "title", "desc", "city", "name", "lat", "lng", "position")} for p in data],
    ensure_ascii=False,
)
day_meta_js = json.dumps(
    {str(k): {"date": v[0], "sub": v[1], "count": len(groups[k])} for k, v in day_meta.items()},
    ensure_ascii=False,
)
cats_js = json.dumps(cats, ensure_ascii=False)
budgets_js = json.dumps(budgets, ensure_ascii=False)

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>武汉 → 山东 9日旅行计划</title>
<script src="https://api.map.baidu.com/api?v=3.0&ak=__KEY__"></script>
<style>
:root{
  --ink:#0a2540; --sub:#425466; --muted:#8898aa; --line:#e6eaf2;
  --bg1:#f6f9fc; --bg2:#eef2ff; --card:#ffffff;
  --shadow:0 8px 30px rgba(38,60,120,.10);
}
*{box-sizing:border-box}
html,body{height:100%;margin:0}
body{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  color:var(--ink); background:linear-gradient(135deg,var(--bg1) 0%,var(--bg2) 100%);
  display:flex; flex-direction:column; overflow:hidden;
}
.banner{position:relative; overflow:hidden; padding:22px 40px 18px; flex:0 0 auto;
  background:linear-gradient(120deg,#635bff 0%,#7b61ff 40%,#0aa3ff 100%); color:#fff;}
.banner::before,.banner::after{content:""; position:absolute; border-radius:50%; filter:blur(40px); opacity:.55;}
.banner::before{width:320px;height:320px;background:#9ad0ff;top:-160px;right:18%}
.banner::after{width:260px;height:260px;background:#b9a6ff;bottom:-170px;left:8%}
.banner-inner{position:relative; display:flex; align-items:center; justify-content:space-between; gap:24px; flex-wrap:wrap}
.banner h1{margin:0; font-size:28px; font-weight:800; letter-spacing:.5px; text-align:center; flex:1 1 auto}
.banner .sub{text-align:center; margin-top:5px; font-size:12px; opacity:.9; letter-spacing:3px}
.actions{display:flex; gap:8px; align-items:center; flex:0 1 auto; flex-wrap:wrap; justify-content:center}
.action-btn{border:1px solid rgba(255,255,255,.4); border-radius:9px; padding:8px 11px;
  background:rgba(255,255,255,.16); color:#fff; cursor:pointer; font:inherit; font-size:12px}
.action-btn:hover{background:rgba(255,255,255,.28)}
.save-status{width:100%; min-height:16px; font-size:11px; text-align:center; opacity:.92}
.badges{display:flex; gap:10px; flex:0 0 auto}
.badge{background:rgba(255,255,255,.16); backdrop-filter:blur(8px); border:1px solid rgba(255,255,255,.28);
  border-radius:14px; padding:10px 14px; min-width:84px; text-align:center;}
.badge .v{font-size:22px; font-weight:800; line-height:1}
.badge .l{font-size:11px; opacity:.92; margin-top:4px; letter-spacing:1px}
.tabs{display:flex; gap:8px; padding:10px 24px; overflow-x:auto; flex:0 0 auto;
  background:rgba(255,255,255,.75); backdrop-filter:blur(6px); border-bottom:1px solid var(--line)}
.tab{flex:0 0 auto; cursor:pointer; border:1px solid var(--line); background:#fff;
  color:var(--sub); padding:8px 16px; border-radius:11px; font-size:14px; font-weight:600;
  transition:.18s; white-space:nowrap; user-select:none;}
.tab:hover{border-color:#c3ccff; color:var(--ink); transform:translateY(-1px)}
.tab.active{background:linear-gradient(120deg,#635bff,#0aa3ff); color:#fff; border-color:transparent;
  box-shadow:0 6px 16px rgba(99,91,255,.35)}
.layout{flex:1 1 auto; display:grid; grid-template-columns:minmax(440px,1fr) 1fr; min-height:0; width:100%}
.timeline{overflow-y:auto; padding:18px 22px 60px; min-width:0; min-height:0}
.map-wrap{position:relative; min-height:0; min-width:0; border-left:1px solid var(--line); overflow:hidden}
#map{position:absolute; inset:0}
.map-title{position:absolute; left:14px; top:14px; z-index:10; background:rgba(255,255,255,.95);
  border:1px solid var(--line); border-radius:12px; padding:8px 14px; box-shadow:var(--shadow);
  font-weight:700; font-size:14px; color:var(--ink); pointer-events:none;}
.map-title small{display:block; font-weight:500; color:var(--muted); font-size:12px; margin-top:2px}
.map-legend{position:absolute; left:14px; bottom:14px; z-index:10; background:rgba(255,255,255,.95);
  border:1px solid var(--line); border-radius:12px; padding:9px 12px; box-shadow:var(--shadow); font-size:12px;}
.map-legend .row{display:flex; align-items:center; gap:7px; color:var(--sub); padding:2px 0}
.map-legend .dot{width:11px;height:11px;border-radius:50%;display:inline-block; border:2px solid #fff; box-shadow:0 0 0 1px rgba(0,0,0,.1)}
.day-head{display:flex; align-items:baseline; gap:10px; margin:2px 0 14px; flex-wrap:wrap}
.day-head .d{font-size:20px; font-weight:800}
.day-head .sub{color:var(--muted); font-size:13px}
.day-head .cnt{margin-left:auto; font-size:12px; color:var(--sub); background:#fff; border:1px solid var(--line); border-radius:20px; padding:3px 11px}
.card{position:relative; display:flex; gap:12px; background:var(--card); border:1px solid var(--line);
  border-radius:14px; padding:12px 14px; margin-bottom:10px; box-shadow:0 2px 10px rgba(38,60,120,.05);
  cursor:pointer; transition:.18s;}
.card:hover{transform:translateY(-2px); box-shadow:var(--shadow); border-color:#c3ccff}
.card.active{border-color:#635bff; box-shadow:0 8px 22px rgba(99,91,255,.22)}
.card .rail{position:absolute; left:0; top:12px; bottom:12px; width:4px; border-radius:4px; background:var(--c)}
.card .time{flex:0 0 50px; font-weight:700; color:var(--ink); font-size:13px; padding-top:2px}
.card .body{flex:1; min-width:0}
.card .tt{font-size:15px; font-weight:700; display:flex; align-items:center; gap:7px; flex-wrap:wrap}
.card .ds{color:var(--sub); font-size:12.5px; margin-top:4px; line-height:1.5; word-break:break-word}
.tag{font-size:10.5px; font-weight:700; color:#fff; background:var(--c); border-radius:7px; padding:2px 7px; letter-spacing:.5px}
.card .num{position:absolute; right:12px; top:12px; width:24px; height:24px; border-radius:50%;
  display:flex; align-items:center; justify-content:center; font-weight:800; font-size:12px; color:#fff; background:var(--c); z-index:1}
.card .card-actions{position:absolute; right:44px; top:12px; display:flex; flex-direction:row; align-items:center;
  gap:8px; z-index:2}
.card .edit-btn,.card .del-btn{position:static; flex:0 0 auto; border:1px solid var(--line); background:#fff;
  color:var(--sub); border-radius:8px; padding:4px 10px; font-size:11px; line-height:1.2; cursor:pointer;
  white-space:nowrap; box-shadow:none}
.card .edit-btn:hover{border-color:#635bff; color:var(--ink)}
.card .del-btn:hover{border-color:#ff5a5f; color:#c33}
.card.hotel-card{background:linear-gradient(135deg, #fff8e6 0%, #ffffff 60%);}
.card.hotel-card .hotel-meta{font-size:12px; color:var(--sub); margin-top:6px; display:flex; gap:10px; flex-wrap:wrap}
.card.hotel-card .hotel-meta b{color:var(--ink)}
.card.hotel-card .status{font-size:11px; padding:1px 7px; border-radius:6px; background:var(--c); color:#fff; font-weight:700}
.inf{background:#fff;border-radius:14px;padding:12px 14px;min-width:210px;max-width:280px;box-shadow:var(--shadow);
  border-left:5px solid var(--c); font-family:inherit}
.inf .it{font-size:15px;font-weight:800;color:var(--ink);display:flex;align-items:center;gap:8px}
.inf .im{font-size:12px;color:var(--muted);margin-top:6px}
.inf .id{font-size:12.5px;color:var(--sub);margin-top:7px;line-height:1.55}
.editor-overlay{position:fixed;inset:0;z-index:1000;background:transparent;display:none;justify-content:flex-start;align-items:stretch;pointer-events:none}
.editor-overlay.open{display:flex}
.point-editor{pointer-events:auto;width:min(420px,100%);height:100%;overflow-y:auto;background:#fff;padding:24px;box-shadow:10px 0 35px rgba(10,37,64,.22)}
.point-editor h2{margin:0 0 12px}
.preview-hint{min-height:18px;font-size:12px;color:var(--sub);margin:0 0 10px;line-height:1.4}
.editor-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.editor-field{display:flex;flex-direction:column;gap:5px;font-size:12px;color:var(--sub)}
.editor-field.wide{grid-column:1/-1}
.editor-field input,.editor-field select,.editor-field textarea{width:100%;border:1px solid var(--line);border-radius:8px;padding:9px;font:inherit;color:var(--ink)}
.editor-actions,.search-row{display:flex;gap:8px;margin-top:14px}
.editor-actions{justify-content:flex-end;flex-wrap:wrap}
.editor-actions button,.search-row button{border:1px solid var(--line);border-radius:8px;padding:9px 13px;background:#fff;cursor:pointer}
.editor-actions .primary{background:#635bff;color:#fff;border-color:#635bff}
.place-results{margin-top:10px;display:grid;gap:7px}
.place-result{border:1px solid var(--line);border-radius:8px;background:#fff;padding:9px;text-align:left;cursor:pointer}
.place-result small{display:block;color:var(--muted);margin-top:3px}
.editor-message{min-height:20px;color:#c33;font-size:12px;margin-top:10px}
.mobile-bar{display:none}
.mobile-more{display:none}
.more-wrap{display:none; position:relative}
.actions-menu{display:none}
@media (max-width:900px){
  .banner{padding:14px 14px 12px; overflow:visible; z-index:50}
  .banner-inner{gap:10px; align-items:flex-start; overflow:visible}
  .banner h1{font-size:18px; letter-spacing:0; text-align:left}
  .banner .sub{text-align:left; letter-spacing:1px; font-size:11px}
  .badges{width:100%; justify-content:space-between}
  .badge{min-width:0; flex:1; padding:8px 6px}
  .badge .v{font-size:16px}
  .badge .l{font-size:10px; letter-spacing:0}
  .actions{width:100%; justify-content:flex-start; gap:6px; position:relative; overflow:visible}
  .actions .action-btn.desktop-only{display:none}
  .more-wrap{display:inline-flex; position:relative; z-index:60}
  .mobile-more{display:inline-flex}
  .actions-menu{position:absolute; left:0; right:auto; top:calc(100% + 6px); z-index:70;
    background:#fff; color:var(--ink); border:1px solid var(--line); border-radius:12px;
    box-shadow:0 10px 28px rgba(10,37,64,.22); min-width:168px; padding:6px; display:none}
  .actions-menu.open{display:grid}
  .actions-menu button{border:0; background:transparent; text-align:left; padding:10px 12px;
    border-radius:8px; font:inherit; font-size:13px; color:var(--ink); cursor:pointer}
  .actions-menu button:hover{background:var(--bg1)}
  .tabs{padding:8px 12px; gap:6px; -webkit-overflow-scrolling:touch; position:relative; z-index:1}
  .tab{padding:7px 12px; font-size:13px}
  .mobile-bar{display:flex; gap:8px; padding:8px 12px; flex:0 0 auto;
    background:#fff; border-bottom:1px solid var(--line)}
  .mobile-bar button{flex:1; border:1px solid var(--line); background:#fff; color:var(--sub);
    border-radius:10px; padding:10px 12px; font:inherit; font-size:14px; font-weight:700; cursor:pointer}
  .mobile-bar button.active{background:linear-gradient(120deg,#635bff,#0aa3ff); color:#fff; border-color:transparent}
  .layout{position:relative; grid-template-columns:1fr; grid-template-rows:1fr}
  /* 不可对地图容器用 display:none，否则 init 时宽高为 0 会报 far <= 0 */
  .layout.mobile-list .map-wrap{
    position:absolute; inset:0; visibility:hidden; pointer-events:none; z-index:0;
  }
  .layout.mobile-list .timeline{
    position:relative; z-index:1; min-height:0; height:100%;
  }
  .layout.mobile-map .timeline{display:none}
  .layout.mobile-map .map-wrap{
    position:relative; visibility:visible; pointer-events:auto;
    min-height:0; height:100%;
  }
  .map-wrap{border-left:none}
  .timeline{padding:14px 12px 80px}
  .card{padding:11px 12px 48px; padding-right:40px}
  .card .card-actions{
    left:62px; right:12px; top:auto; bottom:10px;
    justify-content:flex-end; gap:10px;
  }
  .card .edit-btn,.card .del-btn{padding:8px 14px; font-size:13px; min-height:36px}
  .card .time{flex:0 0 44px; font-size:12px}
  .day-head .d{font-size:18px}
  .editor-overlay.open{align-items:flex-end;justify-content:stretch}
  .point-editor{width:100%; height:min(52vh, 560px); max-height:70vh; border-radius:16px 16px 0 0;
    padding:14px 14px calc(14px + env(safe-area-inset-bottom,0px));
    box-shadow:0 -12px 36px rgba(10,37,64,.28)}
}
@media (min-width:901px){
  .mobile-bar{display:none !important}
  .layout.mobile-list .map-wrap,
  .layout.mobile-map .map-wrap{
    position:relative; inset:auto; visibility:visible; pointer-events:auto; z-index:auto;
  }
  .layout.mobile-map .timeline{display:block}
}
</style>
</head>
<body>
<header class="banner">
  <div class="banner-inner">
    <div class="center" style="flex:1">
      <h1>武汉 → 山东 · 山海九日行</h1>
      <div class="sub">WUHAN · JINAN · WEIHAI · YANTAI</div>
    </div>
    <div class="actions">
      <button class="action-btn" id="addPointBtn" type="button">添加点</button>
      <button class="action-btn desktop-only" id="exportBtn" type="button">导出 JSON</button>
      <button class="action-btn desktop-only" id="importBtn" type="button">导入 JSON</button>
      <button class="action-btn desktop-only" id="resetBtn" type="button">恢复初始行程</button>
      <div class="more-wrap">
        <button class="action-btn mobile-more" id="moreBtn" type="button" aria-expanded="false" aria-controls="actionsMenu">更多</button>
        <div class="actions-menu" id="actionsMenu" role="menu">
          <button type="button" id="exportBtnMobile" role="menuitem">导出 JSON</button>
          <button type="button" id="importBtnMobile" role="menuitem">导入 JSON</button>
          <button type="button" id="resetBtnMobile" role="menuitem">恢复初始行程</button>
        </div>
      </div>
      <input id="importInput" type="file" accept=".json,application/json" hidden>
      <div id="saveStatus" class="save-status" role="status" aria-live="polite"></div>
    </div>
    <div class="badges">
      <div class="badge"><div class="v" id="bDays">9</div><div class="l">天数 DAYS</div></div>
      <div class="badge"><div class="v" id="bPoi">0</div><div class="l">行程点 POI</div></div>
      <div class="badge"><div class="v" id="bCost">¥0</div><div class="l">总预算</div></div>
    </div>
  </div>
</header>
<nav class="tabs" id="tabs"></nav>
<div class="mobile-bar" id="mobileBar" role="tablist" aria-label="手机视图切换">
  <button type="button" id="viewListBtn" class="active" role="tab" aria-selected="true">行程</button>
  <button type="button" id="viewMapBtn" role="tab" aria-selected="false">地图</button>
</div>
<main class="layout mobile-list" id="mainLayout">
  <section class="timeline" id="timeline">
    <div style="color:var(--muted);padding:40px;text-align:center">加载中…</div>
  </section>
  <aside class="map-wrap">
    <div class="map-title" id="mapTitle">行程地图</div>
    <div id="map"></div>
    <div class="map-legend" id="legend"></div>
  </aside>
</main>
<div class="editor-overlay" id="pointEditor" role="dialog" aria-modal="true" aria-labelledby="pointEditorTitle">
  <section class="point-editor">
    <h2 id="pointEditorTitle">添加行程点</h2>
    <form id="pointForm">
      <input id="pointId" name="pointId" type="hidden">
      <div class="editor-grid">
        <label class="editor-field">DAY
          <input id="pointDay" name="day" type="number" min="1" max="9" required>
        </label>
        <label class="editor-field">时间
          <input id="pointTime" name="time" type="time" required>
        </label>
        <label class="editor-field wide">标题
          <input id="pointTitle" name="title" type="text" required>
        </label>
        <label class="editor-field wide">描述
          <textarea id="pointDescription" name="description" rows="3"></textarea>
        </label>
        <label class="editor-field">城市
          <input id="pointCity" name="city" type="text" required>
        </label>
        <label class="editor-field">类别
          <select id="pointCategory" name="category" required>
            <option value="scenic">景点</option><option value="food">美食</option>
            <option value="culture">文化</option><option value="shop">购物</option>
            <option value="transit">交通</option><option value="hotel">住宿</option>
          </select>
        </label>
        <label class="editor-field">纬度
          <input id="pointLat" name="lat" type="number" step="any" required>
        </label>
        <label class="editor-field">经度
          <input id="pointLng" name="lng" type="number" step="any" required>
        </label>
        <label class="editor-field wide">搜索地点
          <div class="search-row">
            <input id="placeKeyword" type="search" autocomplete="off">
            <button id="placeSearchBtn" type="button">搜索</button>
          </div>
        </label>
      </div>
      <div class="place-results" id="placeResults"></div>
      <div class="preview-hint" id="previewHint" role="status"></div>
      <div class="editor-message" id="pointEditorMessage" role="status"></div>
      <div class="editor-actions">
        <button id="mapPickBtn" type="button">地图选点</button>
        <button id="pointCancelBtn" type="button">取消</button>
        <button class="primary" type="submit">保存</button>
      </div>
    </form>
  </section>
</div>
<script>__CORE_JS__</script>
<script>
const KEY = "__KEY__";
const BASE_POIS = __POIS__;
const DAY_META = __DAYMETA__;
const CATS = __CATS__;
const BUDGETS = __BUDGETS__;
const TOTAL = __TOTAL__;
const HOTELS = __HOTELS__;
const DAYS = Object.keys(DAY_META).map(Number).sort(function(a,b){return a-b});
const STORAGE_KEY = 'itinerary-editor-state-v1';
const PASSWORD_KEY = 'itinerary-edit-password';
const API_BASE = "__API_BASE__";
let remoteVersion = 1;
let remoteTitle = '武汉 → 山东 9日旅行计划';
let pollTimer = null;

function escapeHtml(value) {
  return String(value == null ? '' : value).replace(/[&<>"']/g, function(ch) {
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch];
  });
}

function setSaveStatus(message, isError) {
  const el = document.getElementById('saveStatus');
  el.textContent = message || '';
  el.style.color = isError ? '#ffe0e0' : '#ffffff';
}

function cloudEnabled() {
  return !!(API_BASE && String(API_BASE).trim());
}

function apiUrl(path) {
  return String(API_BASE).replace(/\/+$/, '') + path;
}

function basePoints() {
  return ItineraryCore.normalizePoints(BASE_POIS.map(function(p){ return Object.assign({}, p); }));
}

function loadCachedOrBase() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return basePoints();
    const snapshot = JSON.parse(raw);
    if (!snapshot || snapshot.schemaVersion !== 1 || !Array.isArray(snapshot.points)) {
      throw new Error('保存的行程格式无效');
    }
    if (Number.isInteger(snapshot.version)) remoteVersion = snapshot.version;
    if (typeof snapshot.title === 'string') remoteTitle = snapshot.title;
    return ItineraryCore.normalizePoints(snapshot.points);
  } catch (e) {
    setSaveStatus('本地缓存读取失败，已使用初始行程', true);
    return basePoints();
  }
}

function cacheLocal(points, meta) {
  try {
    const normalizedPoints = ItineraryCore.normalizePoints(points);
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      schemaVersion: 1,
      savedAt: new Date().toISOString(),
      version: meta && meta.version != null ? meta.version : remoteVersion,
      title: meta && meta.title ? meta.title : remoteTitle,
      points: normalizedPoints
    }));
    return true;
  } catch (e) {
    setSaveStatus('本地缓存写入失败，请立即导出 JSON', true);
    return false;
  }
}

function getEditPassword() {
  try { return sessionStorage.getItem(PASSWORD_KEY) || ''; } catch (_) { return ''; }
}

function setEditPassword(value) {
  try {
    if (value) sessionStorage.setItem(PASSWORD_KEY, value);
    else sessionStorage.removeItem(PASSWORD_KEY);
  } catch (_) {}
}

function ensureEditPassword() {
  let pwd = getEditPassword();
  if (pwd) return pwd;
  pwd = window.prompt('请输入编辑口令（仅保存在本标签页）');
  if (pwd == null || !String(pwd).trim()) return '';
  pwd = String(pwd).trim();
  setEditPassword(pwd);
  return pwd;
}

async function fetchRemoteItinerary() {
  const res = await fetch(apiUrl('/api/itinerary'), { method: 'GET' });
  if (!res.ok) throw new Error('拉取失败 HTTP ' + res.status);
  const doc = await res.json();
  if (!doc || doc.schemaVersion !== 1 || !Array.isArray(doc.points)) {
    throw new Error('云端行程格式无效');
  }
  return {
    version: doc.version,
    title: doc.title || remoteTitle,
    points: ItineraryCore.normalizePoints(doc.points),
    updatedAt: doc.updatedAt
  };
}

async function pushRemoteItinerary(points, title) {
  const pwd = ensureEditPassword();
  if (!pwd) throw new Error('未提供编辑口令');
  const res = await fetch(apiUrl('/api/itinerary'), {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'X-Edit-Password': pwd
    },
    body: JSON.stringify({
      version: remoteVersion,
      title: title || remoteTitle,
      points: points
    })
  });
  if (res.status === 401) {
    setEditPassword('');
    throw new Error('口令错误');
  }
  if (res.status === 409) {
    const body = await res.json().catch(function(){ return {}; });
    throw new Error('版本冲突：云端已被他人更新（version=' + (body.version || '?') + '），请刷新后重试');
  }
  if (!res.ok) {
    const body = await res.json().catch(function(){ return {}; });
    throw new Error(body.error || ('保存失败 HTTP ' + res.status));
  }
  return res.json();
}

async function resetRemoteItinerary() {
  const pwd = ensureEditPassword();
  if (!pwd) throw new Error('未提供编辑口令');
  const res = await fetch(apiUrl('/api/itinerary/reset'), {
    method: 'POST',
    headers: { 'X-Edit-Password': pwd }
  });
  if (res.status === 401) {
    setEditPassword('');
    throw new Error('口令错误');
  }
  if (!res.ok) {
    const body = await res.json().catch(function(){ return {}; });
    throw new Error(body.error || ('重置失败 HTTP ' + res.status));
  }
  return res.json();
}

function applyRemoteDoc(doc, statusMsg) {
  remoteVersion = doc.version;
  remoteTitle = doc.title || remoteTitle;
  POIS = doc.points;
  cacheLocal(POIS, { version: remoteVersion, title: remoteTitle });
  document.getElementById('bPoi').textContent = POIS.length;
  if (curDay !== null) selectDay(curDay);
  if (statusMsg) setSaveStatus(statusMsg, false);
}

async function persistPoints(points) {
  const normalized = ItineraryCore.normalizePoints(points);
  if (!cloudEnabled()) {
    if (!cacheLocal(normalized)) return false;
    setSaveStatus('已自动保存（仅本机）', false);
    return true;
  }
  try {
    const doc = await pushRemoteItinerary(normalized, remoteTitle);
    remoteVersion = doc.version;
    remoteTitle = doc.title || remoteTitle;
    if (!cacheLocal(doc.points, { version: remoteVersion, title: remoteTitle })) return false;
    setSaveStatus('已同步到云端 v' + remoteVersion, false);
    return true;
  } catch (e) {
    setSaveStatus('云端保存失败：' + (e && e.message || e), true);
    return false;
  }
}

function saveState(points) {
  // 同步路径仅写本地；云端模式请用 persistPoints
  if (!cacheLocal(points)) return false;
  setSaveStatus(cloudEnabled() ? '已写入本地缓存（待云端确认）' : '已自动保存', false);
  return true;
}

function startPolling() {
  if (!cloudEnabled() || pollTimer) return;
  pollTimer = setInterval(async function() {
    if (document.getElementById('pointEditor').classList.contains('open')) return;
    try {
      const doc = await fetchRemoteItinerary();
      if (doc.version > remoteVersion) {
        applyRemoteDoc(doc, '已同步他人更新 v' + doc.version);
      }
    } catch (_) {}
  }, 5000);
}

function exportJson() {
  let url = null;
  try {
    const doc = ItineraryCore.createExport(POIS, '武汉 → 山东 9日旅行计划', new Date());
    const blob = new Blob([JSON.stringify(doc, null, 2)], {type: 'application/json;charset=utf-8'});
    url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    const date = new Date().toISOString().slice(0, 10);
    link.href = url;
    link.download = 'shandong-itinerary-' + date + '.json';
    document.body.appendChild(link);
    link.click();
    link.remove();
    setSaveStatus('JSON 已导出', false);
  } catch (e) {
    setSaveStatus('导出失败，请稍后重试', true);
  } finally {
    if (url !== null) URL.revokeObjectURL(url);
  }
}

function restoreStoredState(raw) {
  if (raw === null) localStorage.removeItem(STORAGE_KEY);
  else localStorage.setItem(STORAGE_KEY, raw);
}

async function importJson(file) {
  const previous = POIS;
  const previousVersion = remoteVersion;
  let previousStored;
  let storageMayHaveChanged = false;
  try {
    const text = await file.text();
    const imported = ItineraryCore.parseImport(text);
    const tip = cloudEnabled()
      ? '导入会替换当前行程并写入云端（所有人可见），是否继续？'
      : '导入会替换当前行程，是否继续？';
    if (!confirm(tip)) return;
    previousStored = localStorage.getItem(STORAGE_KEY);
    storageMayHaveChanged = true;
    POIS = imported.points;
    if (!(await persistPoints(POIS))) {
      throw new Error('无法保存导入的行程');
    }
    document.getElementById('bPoi').textContent = POIS.length;
    if (curDay !== null) selectDay(curDay);
    setSaveStatus(cloudEnabled() ? 'JSON 已导入并同步云端' : 'JSON 已导入', false);
  } catch (e) {
    POIS = previous;
    remoteVersion = previousVersion;
    let rollbackError = null;
    if (storageMayHaveChanged) {
      try { restoreStoredState(previousStored); } catch (restoreError) { rollbackError = restoreError; }
    }
    try {
      document.getElementById('bPoi').textContent = POIS.length;
      if (curDay !== null) selectDay(curDay);
    } catch (_) {}
    const suffix = rollbackError ? '；原保存状态恢复失败，请立即导出' : '';
    setSaveStatus('导入失败：' + (e && e.message || e) + suffix, true);
  }
}

async function resetToBase() {
  const tip = cloudEnabled()
    ? '确定恢复初始行程吗？将覆盖云端共享数据，所有人的修改都会丢失。'
    : '确定恢复初始行程吗？当前本机修改将被覆盖。';
  if (!confirm(tip)) return;
  if (!confirm('再次确认：此操作不可撤销（可用导出 JSON 备份）。')) return;
  if (cloudEnabled()) {
    try {
      const doc = await resetRemoteItinerary();
      applyRemoteDoc({
        version: doc.version,
        title: doc.title,
        points: ItineraryCore.normalizePoints(doc.points)
      }, '已恢复云端初始行程 v' + doc.version);
    } catch (e) {
      setSaveStatus('恢复失败：' + (e && e.message || e), true);
    }
    return;
  }
  const base = basePoints();
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (e) {
    setSaveStatus('恢复失败：无法清除自动保存，当前行程未改变', true);
    return;
  }
  POIS = base;
  remoteVersion = 1;
  document.getElementById('bPoi').textContent = POIS.length;
  setSaveStatus('已恢复初始行程', false);
  if (curDay !== null) selectDay(curDay);
}

let POIS = loadCachedOrBase();

document.getElementById('bDays').textContent = DAYS.length;
document.getElementById('bPoi').textContent = POIS.length;
document.getElementById('bCost').textContent = '¥' + Number(TOTAL).toLocaleString('zh-CN', {
  minimumFractionDigits: Number(TOTAL) % 1 ? 2 : 0,
  maximumFractionDigits: 2
});
document.getElementById('addPointBtn').addEventListener('click', openPointEditor);
document.getElementById('exportBtn').addEventListener('click', exportJson);
document.getElementById('importBtn').addEventListener('click', function(){
  document.getElementById('importInput').click();
});
document.getElementById('importInput').addEventListener('change', function(e){
  const file = e.target.files && e.target.files[0];
  if (file) importJson(file);
  e.target.value = '';
});
document.getElementById('resetBtn').addEventListener('click', resetToBase);

function closeActionsMenu() {
  const menu = document.getElementById('actionsMenu');
  const more = document.getElementById('moreBtn');
  menu.classList.remove('open');
  more.setAttribute('aria-expanded', 'false');
}
document.getElementById('moreBtn').addEventListener('click', function(e){
  e.stopPropagation();
  const menu = document.getElementById('actionsMenu');
  const open = !menu.classList.contains('open');
  menu.classList.toggle('open', open);
  document.getElementById('moreBtn').setAttribute('aria-expanded', open ? 'true' : 'false');
});
document.getElementById('actionsMenu').addEventListener('click', function(e){
  e.stopPropagation();
});
document.getElementById('exportBtnMobile').addEventListener('click', function(){
  closeActionsMenu();
  exportJson();
});
document.getElementById('importBtnMobile').addEventListener('click', function(){
  closeActionsMenu();
  document.getElementById('importInput').click();
});
document.getElementById('resetBtnMobile').addEventListener('click', function(){
  closeActionsMenu();
  resetToBase();
});
document.addEventListener('click', function(){ closeActionsMenu(); });

function isMobileLayout() {
  return window.matchMedia('(max-width: 900px)').matches;
}

function setMobileView(mode) {
  const layout = document.getElementById('mainLayout');
  const listBtn = document.getElementById('viewListBtn');
  const mapBtn = document.getElementById('viewMapBtn');
  const showMap = mode === 'map';
  layout.classList.toggle('mobile-map', showMap);
  layout.classList.toggle('mobile-list', !showMap);
  listBtn.classList.toggle('active', !showMap);
  mapBtn.classList.toggle('active', showMap);
  listBtn.setAttribute('aria-selected', !showMap ? 'true' : 'false');
  mapBtn.setAttribute('aria-selected', showMap ? 'true' : 'false');
  if (!showMap || curDay === null) return;
  const list = POIS.filter(function(p){ return p.day === curDay; })
    .sort(function(a,b){ return a.time.localeCompare(b.time); });
  requestAnimationFrame(function() {
    if (!isMapAvailable()) return;
    try { if (map && map.resize) map.resize(); } catch (_) {}
    renderMap(curDay, list);
  });
}
document.getElementById('viewListBtn').addEventListener('click', function(){ setMobileView('list'); });
document.getElementById('viewMapBtn').addEventListener('click', function(){ setMobileView('map'); });
window.addEventListener('resize', function(){
  if (!isMobileLayout()) {
    document.getElementById('mainLayout').classList.add('mobile-list');
    document.getElementById('mainLayout').classList.remove('mobile-map');
  }
});

document.getElementById('legend').innerHTML = Object.keys(CATS).map(function(k){
  const c = CATS[k];
  return '<div class="row"><span class="dot" style="background:'+c.color+'"></span>'+c.label+'</div>';
}).join('');

const tabsEl = document.getElementById('tabs');
DAYS.forEach(function(d){
  const t = document.createElement('div');
  t.className = 'tab';
  t.dataset.day = d;
  t.textContent = 'DAY ' + d;
  t.addEventListener('click', function(){ selectDay(d); });
  tabsEl.appendChild(t);
});

let map, infoWin;
let mapMarkers = [];
let previewMarker = null;
let previewPolyline = null;
let mapPolyline = null;
let mapReady = false;
let curDay = null;
let mapPickHandler = null;
let pointSource = 'map_click';
let editingPointId = null;

function setEditorMessage(message) {
  document.getElementById('pointEditorMessage').textContent = message || '';
}

function isMapAvailable() {
  return mapReady && typeof BMap !== 'undefined' && !!map;
}

function updateMapControls() {
  const button = document.getElementById('mapPickBtn');
  button.disabled = !isMapAvailable();
  button.title = isMapAvailable() ? '' : '地图不可用，请手动输入经纬度';
}

function showMapUnavailable(message) {
  document.getElementById('mapTitle').textContent = '地图不可用：' + message;
  updateMapControls();
}

function gcj02ToBd09(lng, lat) {
  const x = Number(lng);
  const y = Number(lat);
  const z = Math.sqrt(x * x + y * y) + 0.00002 * Math.sin(y * Math.PI * 3000.0 / 180.0);
  const theta = Math.atan2(y, x) + 0.000003 * Math.cos(x * Math.PI * 3000.0 / 180.0);
  return { lng: z * Math.cos(theta) + 0.0065, lat: z * Math.sin(theta) + 0.006 };
}

function bd09ToGcj02(lng, lat) {
  const x = Number(lng) - 0.0065;
  const y = Number(lat) - 0.006;
  const z = Math.sqrt(x * x + y * y) - 0.00002 * Math.sin(y * Math.PI * 3000.0 / 180.0);
  const theta = Math.atan2(y, x) - 0.000003 * Math.cos(x * Math.PI * 3000.0 / 180.0);
  return { lng: z * Math.cos(theta), lat: z * Math.sin(theta) };
}

function toBdPoint(lat, lng) {
  const bd = gcj02ToBd09(lng, lat);
  return new BMap.Point(bd.lng, bd.lat);
}

function removeMapPickHandler() {
  if (mapPickHandler && map && typeof map.removeEventListener === 'function') {
    map.removeEventListener('click', mapPickHandler);
  }
  mapPickHandler = null;
}

function openPointEditor() {
  editingPointId = null;
  const form = document.getElementById('pointForm');
  form.reset();
  document.getElementById('pointId').value = '';
  document.getElementById('pointEditorTitle').textContent = '添加行程点';
  const day = curDay || DAYS[0];
  const first = POIS.filter(function(p){ return p.day === day; })
    .sort(function(a,b){ return a.time.localeCompare(b.time); })[0];
  document.getElementById('pointDay').value = day;
  document.getElementById('pointCity').value = first ? first.city : '';
  document.getElementById('placeResults').replaceChildren();
  setEditorMessage('');
  setPreviewHint('');
  pointSource = 'map_click';
  document.getElementById('pointEditor').classList.add('open');
  if (isMobileLayout()) setMobileView('map');
  refreshEditorPreview();
  document.getElementById('pointTime').focus();
}

function openPointEditorForEdit(pointId) {
  const p = POIS.find(function(item){ return item.id === pointId; });
  if (!p) return;
  editingPointId = p.id;
  document.getElementById('pointEditorTitle').textContent = '编辑行程点';
  document.getElementById('pointId').value = p.id;
  document.getElementById('pointDay').value = p.day;
  document.getElementById('pointTime').value = p.time;
  document.getElementById('pointTitle').value = p.title;
  document.getElementById('pointDescription').value = p.desc || '';
  document.getElementById('pointCity').value = p.city;
  document.getElementById('pointCategory').value = p.cat;
  document.getElementById('pointLat').value = p.lat;
  document.getElementById('pointLng').value = p.lng;
  document.getElementById('placeKeyword').value = '';
  document.getElementById('placeResults').replaceChildren();
  pointSource = p.source || 'map_click';
  setEditorMessage('');
  document.getElementById('pointEditor').classList.add('open');
  if (isMobileLayout()) setMobileView('map');
  refreshEditorPreview();
  document.getElementById('pointTime').focus();
}

function closePointEditor() {
  editingPointId = null;
  removeMapPickHandler();
  clearPreviewOverlays();
  setPreviewHint('');
  document.getElementById('pointEditor').classList.remove('open');
  document.getElementById('pointId').value = '';
  setEditorMessage('');
}

function refreshDayView(day) {
  selectDay(day);
}

async function deletePointById(pointId) {
  const p = POIS.find(function(item){ return item.id === pointId; });
  if (!p) return;
  if (!window.confirm('确定删除：' + p.title + '？')) return;
  const previousPoints = POIS;
  const previousVersion = remoteVersion;
  try {
    const candidate = ItineraryCore.deletePoint(previousPoints, p.id);
    if (!(await persistPoints(candidate))) {
      POIS = previousPoints;
      remoteVersion = previousVersion;
      setSaveStatus('删除失败，变更未提交，请重试或导出 JSON', true);
      return;
    }
    POIS = candidate;
    document.getElementById('bPoi').textContent = POIS.length;
    refreshDayView(p.day);
  } catch (e) {
    POIS = previousPoints;
    remoteVersion = previousVersion;
    setSaveStatus('删除失败：' + (e && e.message || e), true);
  }
}

function beginMapPick() {
  removeMapPickHandler();
  if (!isMapAvailable()) {
    setEditorMessage('地图不可用，请手动输入经纬度');
    return;
  }
  mapPickHandler = function(e) {
    if (!e || !e.point) {
      setEditorMessage('未能取得地图坐标，请重试');
      return;
    }
    const gcj = bd09ToGcj02(e.point.lng, e.point.lat);
    document.getElementById('pointLat').value = gcj.lat;
    document.getElementById('pointLng').value = gcj.lng;
    pointSource = 'map_click';
    map.removeEventListener('click', mapPickHandler);
    mapPickHandler = null;
    setEditorMessage('已选择地图坐标');
    refreshEditorPreview();
  };
  map.addEventListener('click', mapPickHandler);
  setEditorMessage('请在地图上点击位置');
}

function searchPlaces(keyword, city) {
  const results = document.getElementById('placeResults');
  results.replaceChildren();
  keyword = String(keyword || '').trim();
  city = String(city || '').trim();
  if (!keyword) {
    setEditorMessage('请输入搜索关键词');
    return;
  }
  if (typeof BMap === 'undefined' || typeof BMap.LocalSearch !== 'function') {
    setEditorMessage('地点搜索暂不可用');
    return;
  }
  setEditorMessage('正在搜索…');
  const local = new BMap.LocalSearch(city || map || '全国', {
    onSearchComplete: function(res) {
      if (local.getStatus() !== BMAP_STATUS_SUCCESS) {
        setEditorMessage('未找到地点，请更换关键词');
        return;
      }
      const n = Math.min(res.getCurrentNumPois(), 8);
      if (!n) {
        setEditorMessage('未找到地点，请更换关键词');
        return;
      }
      for (let i = 0; i < n; i++) {
        const item = res.getPoi(i);
        if (!item || !item.point) continue;
        const gcj = bd09ToGcj02(item.point.lng, item.point.lat);
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'place-result';
        const title = document.createElement('strong');
        title.textContent = item.title || '';
        const address = document.createElement('small');
        address.textContent = item.address || '';
        button.append(title, address);
        button.addEventListener('click', function() {
          document.getElementById('pointTitle').value = item.title || '';
          document.getElementById('pointCity').value = item.city || city;
          document.getElementById('pointLat').value = gcj.lat;
          document.getElementById('pointLng').value = gcj.lng;
          pointSource = 'place_search';
          if (map) {
            map.centerAndZoom(item.point, 15);
          }
          setEditorMessage('已选择搜索结果');
          refreshEditorPreview();
        });
        results.appendChild(button);
      }
      setEditorMessage('');
    }
  });
  local.setPageCapacity(8);
  local.search(keyword);
}

async function submitPoint(formData) {
  const day = Number(formData.get('day'));
  let time = String(formData.get('time') || '');
  if (time.length > 5) time = time.slice(0, 5);
  const title = String(formData.get('title') || '').trim();
  const desc = String(formData.get('description') || '').trim();
  const city = String(formData.get('city') || '').trim();
  const cat = String(formData.get('category') || '');
  const latText = String(formData.get('lat') || '').trim();
  const lngText = String(formData.get('lng') || '').trim();
  const lat = Number(latText);
  const lng = Number(lngText);
  const existingId = String(formData.get('pointId') || editingPointId || '').trim();
  if (!DAYS.includes(day) || !/^([01]\d|2[0-3]):[0-5]\d$/.test(time) || !title || !city
      || !Object.prototype.hasOwnProperty.call(CATS, cat)
      || !latText || !lngText || !Number.isFinite(lat) || !Number.isFinite(lng)
      || lat < -90 || lat > 90 || lng < -180 || lng > 180) {
    setEditorMessage('请完整填写有效的必填信息');
    return false;
  }
  const previousPoints = POIS;
  const previousVersion = remoteVersion;
  const previousDay = existingId
    ? (POIS.find(function(item){ return item.id === existingId; }) || {}).day
    : null;
  const id = existingId || ((typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function')
    ? crypto.randomUUID()
    : 'point-' + Date.now() + '-' + Math.random().toString(16).slice(2));
  const point = {
    id: id, day: day, cat: cat, time: time, title: title, desc: desc,
    city: city, name: title, lat: lat, lng: lng, source: pointSource
  };
  let candidate;
  try {
    candidate = existingId
      ? ItineraryCore.updatePoint(previousPoints, point)
      : ItineraryCore.insertPointByTime(previousPoints, point);
    if (!(await persistPoints(candidate))) {
      POIS = previousPoints;
      remoteVersion = previousVersion;
      setEditorMessage('保存失败，变更未提交，请重试或导出 JSON');
      return false;
    }
  } catch (e) {
    POIS = previousPoints;
    remoteVersion = previousVersion;
    setEditorMessage((existingId ? '编辑' : '新增') + '失败：' + (e && e.message || e));
    return false;
  }
  POIS = candidate;
  document.getElementById('bPoi').textContent = POIS.length;
  closePointEditor();
  refreshDayView(day);
  if (previousDay && previousDay !== day) refreshDayView(previousDay);
  return true;
}

document.getElementById('pointCancelBtn').addEventListener('click', closePointEditor);
document.getElementById('mapPickBtn').addEventListener('click', beginMapPick);
document.getElementById('placeSearchBtn').addEventListener('click', function() {
  searchPlaces(
    document.getElementById('placeKeyword').value,
    document.getElementById('pointCity').value
  );
});
document.getElementById('pointForm').addEventListener('submit', function(e) {
  e.preventDefault();
  submitPoint(new FormData(e.currentTarget));
});
['pointDay', 'pointTime', 'pointLat', 'pointLng', 'pointCategory', 'pointTitle'].forEach(function(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.addEventListener('input', refreshEditorPreview);
  el.addEventListener('change', refreshEditorPreview);
});

function polylineWithArrows(path, options) {
  options = options || {};
  const opts = {
    strokeColor: options.strokeColor || '#ff5a5f',
    strokeWeight: options.strokeWeight || 6,
    strokeOpacity: options.strokeOpacity != null ? options.strokeOpacity : 0.9,
    strokeStyle: options.strokeStyle || 'solid'
  };
  if (typeof BMap !== 'undefined'
      && typeof BMap.Symbol === 'function'
      && typeof BMap.IconSequence === 'function'
      && typeof BMap_Symbol_SHAPE_FORWARD_OPEN_ARROW !== 'undefined') {
    try {
      const symbol = new BMap.Symbol(BMap_Symbol_SHAPE_FORWARD_OPEN_ARROW, {
        scale: 0.55,
        strokeColor: '#ffffff',
        strokeWeight: 2,
        strokeOpacity: 0.95
      });
      opts.icons = [new BMap.IconSequence(symbol, '8', '42')];
    } catch (_) {}
  }
  return new BMap.Polyline(path, opts);
}

function straightSegment(from, to) {
  return [toBdPoint(from.lat, from.lng), toBdPoint(to.lat, to.lng)];
}

function pointsRouteKey(list) {
  return list.map(function(p) {
    return String(p.id) + ':' + Number(p.lat).toFixed(6) + ',' + Number(p.lng).toFixed(6);
  }).join('|');
}

const drivingRouteCache = Object.create(null);
let routeRequestSeq = 0;

function fetchDrivingSegment(from, to) {
  const span = Math.abs(Number(from.lat) - Number(to.lat))
    + Math.abs(Number(from.lng) - Number(to.lng));
  if (span < 0.0002 || !isMapAvailable() || typeof BMap.DrivingRoute !== 'function') {
    return Promise.resolve(straightSegment(from, to));
  }
  return new Promise(function(resolve) {
    const driving = new BMap.DrivingRoute(map, {
      onSearchComplete: function(results) {
        if (driving.getStatus() !== BMAP_STATUS_SUCCESS) {
          resolve(straightSegment(from, to));
          return;
        }
        const plan = results && results.getPlan(0);
        if (!plan) {
          resolve(straightSegment(from, to));
          return;
        }
        const path = [];
        for (let i = 0; i < plan.getNumRoutes(); i++) {
          const route = plan.getRoute(i);
          const pts = route.getPath();
          for (let j = 0; j < pts.length; j++) path.push(pts[j]);
        }
        resolve(path.length >= 2 ? path : straightSegment(from, to));
      }
    });
    try {
      driving.search(toBdPoint(from.lat, from.lng), toBdPoint(to.lat, to.lng));
    } catch (_) {
      resolve(straightSegment(from, to));
    }
  });
}

async function buildDrivingRoutePath(list) {
  if (!list || list.length < 2) return [];
  const key = pointsRouteKey(list);
  if (drivingRouteCache[key]) return drivingRouteCache[key].slice();
  const path = [];
  for (let i = 0; i < list.length - 1; i++) {
    const seg = await fetchDrivingSegment(list[i], list[i + 1]);
    for (let j = 0; j < seg.length; j++) {
      if (i > 0 && j === 0) continue;
      path.push(seg[j]);
    }
  }
  drivingRouteCache[key] = path.slice();
  return path;
}

function setMapRouteTitle(d, list, suffix) {
  const meta = DAY_META[d];
  document.getElementById('mapTitle').innerHTML = meta.date
    + '<small>' + meta.sub + ' · ' + list.length + '点'
    + (suffix ? ' · ' + suffix : '')
    + '</small>';
}

function fitMapToPoints(list) {
  if (!isMapAvailable() || !list || list.length === 0) return;
  const pts = list.map(function(p){ return toBdPoint(p.lat, p.lng); });
  if (list.length === 1) {
    map.centerAndZoom(pts[0], 14);
    return;
  }
  try {
    map.setViewport(pts, { margins: [80, 80, 80, 80] });
  } catch (e) {
    map.centerAndZoom(pts[0], 12);
  }
}

function scheduleFitMapToPoints(list) {
  requestAnimationFrame(function() {
    requestAnimationFrame(function() {
      fitMapToPoints(list);
    });
  });
}

function clearMapOverlays() {
  if (!map) return;
  map.clearOverlays();
  mapMarkers = [];
  mapPolyline = null;
  infoWin = null;
  previewMarker = null;
  previewPolyline = null;
}

function clearPreviewOverlays() {
  if (!map) {
    previewMarker = null;
    previewPolyline = null;
    return;
  }
  if (previewMarker) {
    try { map.removeOverlay(previewMarker); } catch (_) {}
    previewMarker = null;
  }
  if (previewPolyline) {
    try { map.removeOverlay(previewPolyline); } catch (_) {}
    previewPolyline = null;
  }
}

function setPreviewHint(text) {
  const el = document.getElementById('previewHint');
  if (el) el.textContent = text || '';
}

function readDraftFromForm() {
  const day = Number(document.getElementById('pointDay').value);
  let time = String(document.getElementById('pointTime').value || '');
  if (time.length > 5) time = time.slice(0, 5);
  const lat = Number(document.getElementById('pointLat').value);
  const lng = Number(document.getElementById('pointLng').value);
  const cat = String(document.getElementById('pointCategory').value || 'scenic');
  const title = String(document.getElementById('pointTitle').value || '').trim();
  return {
    id: editingPointId || '',
    day: day,
    time: time,
    lat: lat,
    lng: lng,
    cat: cat,
    title: title
  };
}

function refreshEditorPreview() {
  if (!document.getElementById('pointEditor').classList.contains('open')) {
    clearPreviewOverlays();
    setPreviewHint('');
    return;
  }
  if (!isMapAvailable()) return;
  const draft = readDraftFromForm();
  const hasCoord = Number.isFinite(draft.lat) && Number.isFinite(draft.lng)
    && draft.lat >= -90 && draft.lat <= 90 && draft.lng >= -180 && draft.lng <= 180;
  const hasTime = /^([01]\d|2[0-3]):[0-5]\d$/.test(draft.time);
  const dayOk = DAYS.includes(draft.day);

  clearPreviewOverlays();

  if (dayOk && draft.day !== curDay) {
    selectDay(draft.day);
    return;
  }

  let hint = '';
  if (dayOk && hasTime) {
    const dayPoints = POIS.filter(function(p){ return p.day === draft.day; });
    const neighbors = ItineraryCore.findTimeNeighbors(dayPoints, draft, editingPointId || undefined);
    if (neighbors.prev && neighbors.next) {
      hint = '按时间将插在「' + neighbors.prev.title + '」与「' + neighbors.next.title + '」之间';
    } else if (!neighbors.prev && neighbors.next) {
      hint = '按时间将作为当天第一个点（在「' + neighbors.next.title + '」之前）';
    } else if (neighbors.prev && !neighbors.next) {
      hint = '按时间将作为当天最后一个点（在「' + neighbors.prev.title + '」之后）';
    } else {
      hint = '当天尚无其他行程点';
    }
    if (hasCoord) {
      const path = [];
      if (neighbors.prev) path.push(toBdPoint(neighbors.prev.lat, neighbors.prev.lng));
      path.push(toBdPoint(draft.lat, draft.lng));
      if (neighbors.next) path.push(toBdPoint(neighbors.next.lat, neighbors.next.lng));
      if (path.length >= 2) {
        previewPolyline = polylineWithArrows(path, {
          strokeColor: '#635bff',
          strokeWeight: 5,
          strokeOpacity: 0.85,
          strokeStyle: 'dashed'
        });
        map.addOverlay(previewPolyline);
      }
    }
  } else if (hasCoord) {
    hint = '已定位；填写时间后可预览插入顺序';
  } else {
    hint = '选择坐标后显示预览钉；填写时间后显示虚线插入位置';
  }
  setPreviewHint(hint);

  if (hasCoord) {
    const color = (CATS[draft.cat] && CATS[draft.cat].color) || '#635bff';
    const svg = ItineraryCore.buildNumberedPinSvg('+', color);
    const icon = new BMap.Icon(
      'data:image/svg+xml,' + encodeURIComponent(svg),
      new BMap.Size(36, 42),
      { anchor: new BMap.Size(18, 41) }
    );
    previewMarker = new BMap.Marker(toBdPoint(draft.lat, draft.lng), { icon: icon });
    map.addOverlay(previewMarker);
  }
}

function initMap(){
  mapReady = false;
  const c0 = POIS[0] || {lat: 30.5928, lng: 114.3055};
  map = new BMap.Map('map');
  map.centerAndZoom(toBdPoint(c0.lat, c0.lng), 12);
  map.enableScrollWheelZoom(true);
  map.addControl(new BMap.NavigationControl());
  map.addControl(new BMap.ScaleControl());
  window.addEventListener('resize', function(){
    try { map.checkResize && map.checkResize(); } catch(_) {}
  });
  mapReady = true;
  updateMapControls();
  return true;
}

function renderTimeline(d, list){
  const t = document.getElementById('timeline');
  const meta = DAY_META[d];
  let html = '<div class="day-head">'
    + '<div class="d">DAY ' + d + '</div>'
    + '<div class="sub">' + meta.date + ' · ' + meta.sub + '</div>'
    + '<div class="cnt">' + list.length + ' 个行程点</div></div>';
  list.forEach(function(p){
    const c = CATS[p.cat];
    const isHotel = p.cat === 'hotel';
    const cardCls = isHotel ? 'card hotel-card' : 'card';
    html += '<div class="'+cardCls+'" data-id="'+escapeHtml(p.id)+'" style="--c:'+c.color+'">'
      + '<div class="rail"></div>'
      + '<div class="time">'+escapeHtml(p.time)+'</div>'
      + '<div class="body">'
      +   '<div class="tt">'+escapeHtml(p.title)+'<span class="tag">'+c.label+'</span></div>'
      +   '<div class="ds">'+escapeHtml(p.desc)+'</div>';
    if (isHotel){
      const h = HOTELS[p.title];
      if (h){
        html += '<div class="hotel-meta">'
          + '<span>📍 <b>'+escapeHtml(h.addr)+'</b></span>'
          + '<span>💰 <b>'+escapeHtml(h.price)+'</b></span>'
          + '<span class="status">'+escapeHtml(h.status)+'</span>'
          + '</div>';
      }
    }
    html += '</div><div class="card-actions">'
      + '<button type="button" class="edit-btn" data-id="'+escapeHtml(p.id)+'">编辑</button>'
      + '<button type="button" class="del-btn" data-id="'+escapeHtml(p.id)+'">删除</button>'
      + '</div><div class="num">'+p.position+'</div></div>';
  });
  t.innerHTML = html;
  t.scrollTop = 0;
  Array.from(t.querySelectorAll('.card')).forEach(function(el){
    el.addEventListener('click', function(){
      const point = POIS.find(function(p){ return p.id === el.dataset.id; });
      if (point) flyTo(d, point.position);
    });
  });
  Array.from(t.querySelectorAll('.edit-btn')).forEach(function(btn){
    btn.addEventListener('click', function(e){
      e.stopPropagation();
      openPointEditorForEdit(btn.dataset.id);
    });
  });
  Array.from(t.querySelectorAll('.del-btn')).forEach(function(btn){
    btn.addEventListener('click', function(e){
      e.stopPropagation();
      deletePointById(btn.dataset.id);
    });
  });
}

function renderMap(d, list){
  if (!isMapAvailable()) {
    showMapUnavailable('地图脚本或初始化失败；时间轴与数据功能仍可使用');
    return;
  }
  setMapRouteTitle(d, list, '');
  clearMapOverlays();

  try {
    const offsetList = ItineraryCore.computeMarkerPixelOffsets(list);
    const offsetById = {};
    offsetList.forEach(function(o){ offsetById[o.id] = o; });
    list.forEach(function(p) {
      const svg = ItineraryCore.buildNumberedPinSvg(p.position, CATS[p.cat].color);
      const icon = new BMap.Icon(
        'data:image/svg+xml,' + encodeURIComponent(svg),
        new BMap.Size(36, 42),
        { anchor: new BMap.Size(18, 41) }
      );
      const off = offsetById[p.id] || { offsetX: 0, offsetY: 0 };
      const marker = new BMap.Marker(toBdPoint(p.lat, p.lng), {
        icon: icon,
        offset: new BMap.Size(off.offsetX, off.offsetY)
      });
      marker.addEventListener('click', function(){ flyTo(p.day, p.position); });
      map.addOverlay(marker);
      mapMarkers.push(marker);
    });
    if (list.length >= 2) {
      const straight = list.map(function(p){ return toBdPoint(p.lat, p.lng); });
      mapPolyline = polylineWithArrows(straight, {
        strokeColor: '#ff5a5f',
        strokeWeight: 6,
        strokeOpacity: 0.9
      });
      map.addOverlay(mapPolyline);
    }
  } catch(e){
    document.getElementById('mapTitle').innerHTML +=
      ' · ❌渲染失败: ' + escapeHtml(e && e.message || e);
    return;
  }

  scheduleFitMapToPoints(list);
  if (document.getElementById('pointEditor').classList.contains('open')) {
    refreshEditorPreview();
  }
  if (list.length < 2) return;

  const requestId = ++routeRequestSeq;
  setMapRouteTitle(d, list, '路线计算中…');
  buildDrivingRoutePath(list).then(function(path) {
    if (requestId !== routeRequestSeq || curDay !== d || !isMapAvailable()) return;
    if (path && path.length >= 2) {
      if (mapPolyline) map.removeOverlay(mapPolyline);
      mapPolyline = polylineWithArrows(path, {
        strokeColor: '#ff5a5f',
        strokeWeight: 6,
        strokeOpacity: 0.9
      });
      map.addOverlay(mapPolyline);
      scheduleFitMapToPoints(list);
    }
    setMapRouteTitle(d, list, '驾车路线');
  }).catch(function() {
    if (requestId !== routeRequestSeq || curDay !== d) return;
    setMapRouteTitle(d, list, '直线备用');
  });
}

function selectDay(d){
  curDay = d;
  Array.prototype.forEach.call(document.querySelectorAll('.tab'), function(t){
    t.classList.toggle('active', parseInt(t.dataset.day,10) === d);
  });
  const list = POIS.filter(function(p){ return p.day === d; })
    .sort(function(a,b){ return a.time.localeCompare(b.time); });
  renderTimeline(d, list);
  if (isMapAvailable()) renderMap(d, list);
}

function flyTo(d, num){
  if (curDay !== d) selectDay(d);
  const p = POIS.find(function(x){ return x.day === d && x.position === num; });
  if (!p) return;
  Array.prototype.forEach.call(document.querySelectorAll('.card'), function(el){
    el.classList.toggle('active', el.dataset.id === p.id);
  });
  if (isMobileLayout()) setMobileView('map');
  if (!isMapAvailable()) return;
  const pt = toBdPoint(p.lat, p.lng);
  map.centerAndZoom(pt, 15);
  const c = CATS[p.cat];
  let extra = '';
  if (p.cat === 'hotel'){
    const h = HOTELS[p.title];
    if (h) extra = '<div class="id">📍 '+escapeHtml(h.addr)+'<br>💰 '
      +escapeHtml(h.price)+' · '+escapeHtml(h.status)+'</div>';
  } else {
    extra = '<div class="id">'+escapeHtml(p.desc)+'</div>';
  }
  const html = '<div class="inf" style="--c:'+c.color+'">'
    + '<div class="it">'+escapeHtml(p.title)+'<span class="tag" style="background:'+c.color+'">'+c.label+'</span></div>'
    + '<div class="im">'+DAY_META[d].date+' · '+escapeHtml(p.time)+' · '+escapeHtml(p.city)+'</div>'
    + extra + '</div>';
  if (infoWin) map.closeInfoWindow();
  infoWin = new BMap.InfoWindow(html, { width: 280, offset: new BMap.Size(0, -32) });
  map.openInfoWindow(infoWin, pt);
}

async function boot(){
  if (location.protocol === 'file:') {
    showMapUnavailable(
      '百度地图 JS API 不支持直接双击打开。请运行本地 HTTP 服务并访问 '
      + 'http://localhost:8000/'
    );
  } else if (typeof BMap === 'undefined') {
    showMapUnavailable('百度地图脚本未加载，请检查网络或 Key 配置');
  } else {
    try {
      initMap();
    } catch(e) {
      mapReady = false;
      showMapUnavailable('地图初始化失败：' + (e && e.message || e));
    }
  }
  if (cloudEnabled()) {
    try {
      const doc = await fetchRemoteItinerary();
      applyRemoteDoc(doc, '已从云端加载 v' + doc.version);
    } catch (e) {
      setSaveStatus('云端暂不可用，已使用本地缓存：' + (e && e.message || e), true);
    }
    startPolling();
  }
  selectDay(DAYS[0]);
}

if (typeof BMap !== 'undefined') {
  boot();
} else {
  window.addEventListener('load', function(){
    boot();
  });
}
</script>
</body>
</html>"""


HTML = (HTML
    .replace("__KEY__", KEY)
    .replace("__API_BASE__", API_BASE)
    .replace("__CORE_JS__", core_js)
    .replace("__POIS__", pois_js)
    .replace("__DAYMETA__", day_meta_js)
    .replace("__CATS__", cats_js)
    .replace("__BUDGETS__", budgets_js)
    .replace("__TOTAL__", str(total))
    .replace("__HOTELS__", hotels_js))

(ROOT / "index.html").write_text(HTML, encoding="utf-8")
print("OK v3 index.html  total=¥%s  pois=%d days=%d api=%s" % (
    total, len(data), len(days), API_BASE or "(local-only)"))
