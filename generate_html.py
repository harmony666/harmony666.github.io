#!/usr/bin/env python3
# 读取 coords.json（完整行程含酒店）→ 生成内联 HTML
import json
from pathlib import Path

ROOT = Path(__file__).parent

KEY = "B6VBZ-V75KG-HBEQP-IRLIB-ANBLZ-W6BD5"
data = json.loads((ROOT / "coords.json").read_text(encoding="utf-8"))
core_js = (ROOT / "src" / "itinerary-core.js").read_text(encoding="utf-8")

budgets = {"交通": 1117+336+577, "住宿": 138+352+400+150, "租车": 937, "吃饭门票": 1500}
total = sum(budgets.values())

# 住宿细分（右侧住宿卡片展示）
hotel_meta = {
    "济南住宿·天桥区": {"addr": "天桥区小清河北路恒大滨河左岸D9公寓1号楼119号商铺", "price": "¥138", "status": "已预订"},
    "威海住宿·山大路": {"addr": "环翠区高技术产业开发区山大路15-6号(建设银行旁，山大南门对面)", "price": "¥352/2晚", "status": "已预订"},
    "威海住宿·山大路(继续住)": {"addr": "山大路15-6号", "price": "—", "status": "续住"},
    "烟台住宿·金海湾": {"addr": "烟台山旁海景(芝罘区)", "price": "约¥400/晚", "status": "推荐·未订"},
    "烟台住宿·金海湾(继续住)": {"addr": "烟台山旁海景", "price": "—", "status": "续住"},
    "威海站住宿·汉庭": {"addr": "汉庭酒店威海火车站店", "price": "约¥150/晚", "status": "推荐·未订"},
}
hotels_js = json.dumps(hotel_meta, ensure_ascii=False)

day_meta = {
    1: ("8月1日", "济南 · 初见泉城"),
    2: ("8月2日", "济南 · 山湖与博物馆"),
    3: ("8月3日", "威海 · 抵岸登岛"),
    4: ("8月4日", "威海 · 海角天涯"),
    5: ("8月5日", "威海→烟台 · 跨城自驾"),
    6: ("8月6日", "烟台 · 蓬莱仙境"),
    7: ("8月7日", "烟台→威海 · 归途夜市"),
    8: ("8月8日", "威海 · 收官启程"),
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
<script src="https://map.qq.com/api/gljs?v=1&key=__KEY__&libraries=service"></script>
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
  display:flex; align-items:center; justify-content:center; font-weight:800; font-size:12px; color:#fff; background:var(--c)}
.card.hotel-card{background:linear-gradient(135deg, #fff8e6 0%, #ffffff 60%);}
.card.hotel-card .hotel-meta{font-size:12px; color:var(--sub); margin-top:6px; display:flex; gap:10px; flex-wrap:wrap}
.card.hotel-card .hotel-meta b{color:var(--ink)}
.card.hotel-card .status{font-size:11px; padding:1px 7px; border-radius:6px; background:var(--c); color:#fff; font-weight:700}
.inf{background:#fff;border-radius:14px;padding:12px 14px;min-width:210px;max-width:280px;box-shadow:var(--shadow);
  border-left:5px solid var(--c); font-family:inherit}
.inf .it{font-size:15px;font-weight:800;color:var(--ink);display:flex;align-items:center;gap:8px}
.inf .im{font-size:12px;color:var(--muted);margin-top:6px}
.inf .id{font-size:12.5px;color:var(--sub);margin-top:7px;line-height:1.55}
@media (max-width:900px){
  .layout{grid-template-columns:1fr; grid-template-rows:50% 50%}
  .map-wrap{border-left:none; border-top:1px solid var(--line)}
  .banner h1{font-size:22px}
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
      <button class="action-btn" id="exportBtn" type="button">导出 JSON</button>
      <button class="action-btn" id="importBtn" type="button">导入 JSON</button>
      <button class="action-btn" id="resetBtn" type="button">恢复初始行程</button>
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
<main class="layout">
  <section class="timeline" id="timeline">
    <div style="color:var(--muted);padding:40px;text-align:center">加载中…</div>
  </section>
  <aside class="map-wrap">
    <div class="map-title" id="mapTitle">行程地图</div>
    <div id="map"></div>
    <div class="map-legend" id="legend"></div>
  </aside>
</main>
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

function setSaveStatus(message, isError) {
  const el = document.getElementById('saveStatus');
  el.textContent = message || '';
  el.style.color = isError ? '#ffe0e0' : '#ffffff';
}

function loadState() {
  const base = ItineraryCore.normalizePoints(BASE_POIS.map(function(p){ return Object.assign({}, p); }));
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return base;
    const snapshot = JSON.parse(raw);
    if (!snapshot || snapshot.schemaVersion !== 1 || !Array.isArray(snapshot.points)) {
      throw new Error('保存的行程格式无效');
    }
    return ItineraryCore.normalizePoints(snapshot.points);
  } catch (e) {
    setSaveStatus('自动保存读取失败，已使用初始行程', true);
    return base;
  }
}

function saveState(points) {
  try {
    const normalizedPoints = ItineraryCore.normalizePoints(points);
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      schemaVersion: 1,
      savedAt: new Date().toISOString(),
      points: normalizedPoints
    }));
    setSaveStatus('已自动保存', false);
    return true;
  } catch (e) {
    setSaveStatus('自动保存失败，请立即导出 JSON', true);
    return false;
  }
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
  let previousStored;
  let storageMayHaveChanged = false;
  try {
    const text = await file.text();
    const imported = ItineraryCore.parseImport(text);
    if (!confirm('导入会替换当前行程，是否继续？')) return;
    previousStored = localStorage.getItem(STORAGE_KEY);
    storageMayHaveChanged = true;
    POIS = imported.points;
    if (!saveState(POIS)) {
      throw new Error('无法保存导入的行程');
    }
    document.getElementById('bPoi').textContent = POIS.length;
    if (curDay !== null) selectDay(curDay);
    setSaveStatus('JSON 已导入', false);
  } catch (e) {
    POIS = previous;
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

function resetToBase() {
  if (!confirm('确定恢复初始行程吗？当前修改将被覆盖。')) return;
  const base = ItineraryCore.normalizePoints(BASE_POIS.map(function(p){ return Object.assign({}, p); }));
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (e) {
    setSaveStatus('恢复失败：无法清除自动保存，当前行程未改变', true);
    return;
  }
  POIS = base;
  document.getElementById('bPoi').textContent = POIS.length;
  setSaveStatus('已恢复初始行程', false);
  if (curDay !== null) selectDay(curDay);
}

let POIS = loadState();

document.getElementById('bDays').textContent = DAYS.length;
document.getElementById('bPoi').textContent = POIS.length;
document.getElementById('bCost').textContent = '¥' + Number(TOTAL).toLocaleString();
document.getElementById('addPointBtn').addEventListener('click', function(){
  setSaveStatus('编辑功能将在后续版本提供', false);
});
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

let map, multiMarker, multiPoly, infoWin;
let curDay = null;

function markerStyles(points) {
  const styles = {};
  points.forEach(function(p) {
    const svg = ItineraryCore.buildNumberedPinSvg(p.position, CATS[p.cat].color);
    styles[p.id] = new TMap.MarkerStyle({
      src: 'data:image/svg+xml,' + encodeURIComponent(svg),
      width: 36, height: 42, anchor: { x: 18, y: 41 }
    });
  });
  return styles;
}

function polylineStyle() {
  return new TMap.PolylineStyle({
    width: 7,
    color: '#ff5a5f',
    borderWidth: 3,
    borderColor: '#ffffff',
    showArrow: true,
    arrowOptions: { width: 8, height: 5, space: 60 },
    lineCap: 'round',
    lineJoin: 'round'
  });
}

function initMap(){
  const c0 = POIS[0] || {lat: 30.5928, lng: 114.3055};
  map = new TMap.Map('map', { center: new TMap.LatLng(c0.lat, c0.lng), zoom: 12 });
  multiMarker = new TMap.MultiMarker({ map: map, styles: markerStyles(POIS), geometries: [] });
  multiPoly = new TMap.MultiPolyline({ map: map, styles: { route: polylineStyle() }, geometries: [] });
  try { multiPoly.setZIndex(100); } catch(_) {}
  try { multiMarker.setZIndex(200); } catch(_) {}
  multiMarker.on('click', function(e){
    const p = e.geometry && e.geometry.properties;
    if (p) flyTo(p.day, p.position);
  });
  window.addEventListener('resize', function(){ try{ map.invalidateSize && map.invalidateSize(); }catch(_){} });
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
    html += '<div class="'+cardCls+'" data-id="'+p.id+'" style="--c:'+c.color+'">'
      + '<div class="rail"></div>'
      + '<div class="time">'+p.time+'</div>'
      + '<div class="body">'
      +   '<div class="tt">'+p.title+'<span class="tag">'+c.label+'</span></div>'
      +   '<div class="ds">'+p.desc+'</div>';
    if (isHotel){
      const h = HOTELS[p.title];
      if (h){
        html += '<div class="hotel-meta">'
          + '<span>📍 <b>'+h.addr+'</b></span>'
          + '<span>💰 <b>'+h.price+'</b></span>'
          + '<span class="status">'+h.status+'</span>'
          + '</div>';
      }
    }
    html += '</div><div class="num">'+p.position+'</div></div>';
  });
  t.innerHTML = html;
  t.scrollTop = 0;
  Array.from(t.querySelectorAll('.card')).forEach(function(el){
    el.addEventListener('click', function(){
      const point = POIS.find(function(p){ return p.id === el.dataset.id; });
      if (point) flyTo(d, point.position);
    });
  });
}

function renderMap(d, list){
  const meta = DAY_META[d];
  document.getElementById('mapTitle').innerHTML = meta.date + '<small>'+meta.sub+' · '+list.length+'点</small>';

  const geoms = list.map(function(p){
    return {
      id: p.id,
      styleId: p.id,
      position: new TMap.LatLng(p.lat, p.lng),
      properties: p
    };
  });
  const polyPaths = list.map(function(p){ return new TMap.LatLng(p.lat, p.lng); });

  // 渲染覆盖物（marker + polyline），setGeometries 内部清空旧的再加新的
  try {
    if (!multiMarker || !multiPoly) throw new Error('覆盖物未初始化');
    multiMarker.setStyles(markerStyles(list));
    multiMarker.setGeometries(geoms);
    multiPoly.setGeometries(list.length >= 2 ? [{
      id: 'route_' + d,
      paths: polyPaths,
      styleId: 'route'
    }] : []);
  } catch(e){
    document.getElementById('mapTitle').innerHTML += ' · ❌渲染失败: ' + e.message;
    return;
  }

  if (infoWin) { infoWin.close(); infoWin = null; }
  if (list.length === 0) return;
  if (list.length === 1) {
    map.setCenter(new TMap.LatLng(list[0].lat, list[0].lng));
    map.setZoom(15);
    return;
  }

  // 用 fitBounds 强制 fit 全部 POI（无论单城/跨城都正确）
  try {
    const lats = list.map(function(p){return Number(p.lat);});
    const lngs = list.map(function(p){return Number(p.lng);});
    const sw = new TMap.LatLng(Math.min.apply(null,lats), Math.min.apply(null,lngs));
    const ne = new TMap.LatLng(Math.max.apply(null,lats), Math.max.apply(null,lngs));
    map.fitBounds(new TMap.LatLngBounds(sw, ne), { padding: [70, 70, 70, 70] });
  } catch(e){
    // 兜底：setCenter + setZoom
    const lats = list.map(function(p){return Number(p.lat);});
    const lngs = list.map(function(p){return Number(p.lng);});
    const clat = (Math.min.apply(null,lats) + Math.max.apply(null,lats)) / 2;
    const clng = (Math.min.apply(null,lngs) + Math.max.apply(null,lngs)) / 2;
    const span = Math.max(Math.max.apply(null,lats)-Math.min.apply(null,lats),
                          Math.max.apply(null,lngs)-Math.min.apply(null,lngs));
    const zoom = span<0.04?14 : span<0.09?13 : span<0.25?12 : span<0.8?10 : span<2?8 : 7;
    map.setCenter(new TMap.LatLng(clat, clng));
    map.setZoom(zoom);
  }

}

function selectDay(d){
  curDay = d;
  Array.prototype.forEach.call(document.querySelectorAll('.tab'), function(t){
    t.classList.toggle('active', parseInt(t.dataset.day,10) === d);
  });
  const list = POIS.filter(function(p){ return p.day === d; })
    .sort(function(a,b){ return a.position - b.position; });
  renderTimeline(d, list);
  renderMap(d, list);
}

function flyTo(d, num){
  if (curDay !== d) selectDay(d);
  const p = POIS.find(function(x){ return x.day === d && x.position === num; });
  if (!p) return;
  Array.prototype.forEach.call(document.querySelectorAll('.card'), function(el){
    el.classList.toggle('active', el.dataset.id === p.id);
  });
  map.setCenter(new TMap.LatLng(p.lat, p.lng));
  map.setZoom(15);
  const c = CATS[p.cat];
  let extra = '';
  if (p.cat === 'hotel'){
    const h = HOTELS[p.title];
    if (h) extra = '<div class="id">📍 '+h.addr+'<br>💰 '+h.price+' · '+h.status+'</div>';
  } else {
    extra = '<div class="id">'+p.desc+'</div>';
  }
  const html = '<div class="inf" style="--c:'+c.color+'">'
    + '<div class="it">'+p.title+'<span class="tag" style="background:'+c.color+'">'+c.label+'</span></div>'
    + '<div class="im">'+DAY_META[d].date+' · '+p.time+' · '+p.city+'</div>'
    + extra + '</div>';
  if (infoWin) infoWin.close();
  infoWin = new TMap.InfoWindow({
    map: map, position: new TMap.LatLng(p.lat, p.lng),
    content: html, offset: {x:0, y:-32}
  });
  infoWin.open();
}

function boot(){
  let ok = false;
  try { ok = initMap(); } catch(e){
    document.getElementById('mapTitle').textContent = '❌地图初始化失败：' + (e && e.message || e);
  }
  if (ok) selectDay(DAYS[0]);
}

if (typeof TMap !== 'undefined') {
  boot();
} else {
  window.addEventListener('load', function(){
    if (typeof TMap !== 'undefined') boot();
    else document.getElementById('mapTitle').textContent = '腾讯地图脚本未加载，请检查网络';
  });
}
</script>
</body>
</html>"""

HTML = (HTML
    .replace("__KEY__", KEY)
    .replace("__CORE_JS__", core_js)
    .replace("__POIS__", pois_js)
    .replace("__DAYMETA__", day_meta_js)
    .replace("__CATS__", cats_js)
    .replace("__BUDGETS__", budgets_js)
    .replace("__TOTAL__", str(total))
    .replace("__HOTELS__", hotels_js))

(ROOT / "itinerary.html").write_text(HTML, encoding="utf-8")
print("OK v3 itinerary.html  total=¥%d  pois=%d days=%d" % (total, len(data), len(days)))
