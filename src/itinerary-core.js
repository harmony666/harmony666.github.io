(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.ItineraryCore = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  const CATEGORIES = new Set(['scenic', 'food', 'culture', 'shop', 'transit', 'hotel']);
  const TIME_RE = /^([01]\d|2[0-3]):[0-5]\d$/;

  function validatePoint(raw) {
    if (typeof raw.id !== 'string' || !raw.id.trim()) throw new Error('点 ID 必须是非空字符串');
    const p = {
      ...raw,
      id: raw.id.trim(),
      day: Number(raw.day),
      position: Number(raw.position),
      lat: Number(raw.lat),
      lng: Number(raw.lng),
    };
    if (!Number.isInteger(p.day) || p.day < 1 || p.day > 9) throw new Error('日期无效');
    if (!TIME_RE.test(p.time)) throw new Error('时间格式无效');
    if (!CATEGORIES.has(p.cat)) throw new Error('类别无效');
    if (!Number.isFinite(p.lat) || p.lat < -90 || p.lat > 90) throw new Error('纬度无效');
    if (!Number.isFinite(p.lng) || p.lng < -180 || p.lng > 180) throw new Error('经度无效');
    return p;
  }

  function normalizePoints(points) {
    const valid = points.map(validatePoint);
    if (new Set(valid.map((p) => p.id)).size !== valid.length) throw new Error('点 ID 必须唯一');
    const output = [];
    for (let day = 1; day <= 9; day++) {
      valid
        .filter((p) => p.day === day)
        .sort((a, b) => a.position - b.position || a.time.localeCompare(b.time))
        .forEach((p, index) => output.push({ ...p, position: index + 1 }));
    }
    return output;
  }

  function insertPointByTime(points, rawPoint) {
    const point = validatePoint(rawPoint);
    const other = points.filter((p) => p.day !== point.day);
    const day = points.filter((p) => p.day === point.day);
    let index = day.length;
    for (let i = day.length - 1; i >= 0; i--) {
      if (day[i].time <= point.time) {
        index = i + 1;
        break;
      }
      index = 0;
    }
    day.splice(index, 0, point);
    return normalizePoints(other.concat(day.map((p, i) => ({ ...p, position: i + 1 }))));
  }

  function reorderDay(points, day, ids) {
    const selected = points.filter((p) => p.day === day);
    if (
      ids.length !== selected.length ||
      new Set(ids).size !== ids.length ||
      ids.some((id) => !selected.some((p) => p.id === id))
    ) {
      throw new Error('排序 ID 必须完整且唯一');
    }
    const byId = new Map(selected.map((p) => [p.id, p]));
    return normalizePoints(
      points
        .filter((p) => p.day !== day)
        .concat(ids.map((id, i) => ({ ...byId.get(id), position: i + 1 }))),
    );
  }

  function createExport(points, title, now) {
    return {
      schemaVersion: 1,
      exportedAt: now.toISOString(),
      title,
      points: normalizePoints(points),
    };
  }

  function parseImport(text) {
    const doc = JSON.parse(text);
    if (!doc || doc.schemaVersion !== 1 || !Array.isArray(doc.points)) {
      throw new Error('不支持的行程文件格式');
    }
    return { ...doc, points: normalizePoints(doc.points) };
  }

  function buildNumberedPinSvg(number, color) {
    return `<svg xmlns="http://www.w3.org/2000/svg" width="36" height="42"><path fill="${color}" stroke="#fff" stroke-width="2" d="M18 1C8.6 1 2 8 2 17c0 12 16 24 16 24s16-12 16-24C34 8 27.4 1 18 1z"/><text x="18" y="22" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">${number}</text></svg>`;
  }

  return {
    normalizePoints,
    insertPointByTime,
    reorderDay,
    createExport,
    parseImport,
    buildNumberedPinSvg,
  };
});
