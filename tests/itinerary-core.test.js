const test = require('node:test');
const assert = require('node:assert/strict');
const Core = require('../src/itinerary-core.js');

const point = (id, day, time, position, overrides = {}) => ({
  id,
  day,
  time,
  position,
  title: id,
  name: id,
  desc: '',
  city: '威海',
  cat: 'scenic',
  lat: 37.5,
  lng: 122.1,
  source: 'seed',
  ...overrides,
});

test('insertPointByTime inserts after equal times and normalizes positions', () => {
  const result = Core.insertPointByTime(
    [point('a', 3, '09:00', 1), point('b', 3, '11:00', 2)],
    point('c', 3, '09:00', 99),
  );
  assert.deepEqual(result.map((p) => p.id), ['a', 'c', 'b']);
  assert.deepEqual(result.map((p) => p.position), [1, 2, 3]);
});

test('reorderDay rejects incomplete id lists', () => {
  assert.throws(
    () => Core.reorderDay([point('a', 2, '09:00', 1), point('b', 2, '10:00', 2)], 2, ['a']),
    /完整/,
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

test('parseImport rejects duplicate ids, invalid day, time, cat, and lng', () => {
  const base = Core.createExport([point('a', 1, '09:00', 1)], '旅行', new Date(0));

  const duplicate = structuredClone(base);
  duplicate.points.push(point('a', 1, '10:00', 2));
  assert.throws(() => Core.parseImport(JSON.stringify(duplicate)), /唯一/);

  const badDay = structuredClone(base);
  badDay.points[0].day = 10;
  assert.throws(() => Core.parseImport(JSON.stringify(badDay)), /日期/);

  const badTime = structuredClone(base);
  badTime.points[0].time = '25:00';
  assert.throws(() => Core.parseImport(JSON.stringify(badTime)), /时间/);

  const badCat = structuredClone(base);
  badCat.points[0].cat = 'invalid';
  assert.throws(() => Core.parseImport(JSON.stringify(badCat)), /类别/);

  const badLng = structuredClone(base);
  badLng.points[0].lng = 200;
  assert.throws(() => Core.parseImport(JSON.stringify(badLng)), /经度/);
});

test('reorderDay does not change order of other days', () => {
  const points = [
    point('d1a', 1, '09:00', 1),
    point('d1b', 1, '10:00', 2),
    point('d2a', 2, '09:00', 1),
    point('d2b', 2, '10:00', 2),
  ];
  const result = Core.reorderDay(points, 2, ['d2b', 'd2a']);
  assert.deepEqual(
    result.filter((p) => p.day === 1).map((p) => p.id),
    ['d1a', 'd1b'],
  );
  assert.deepEqual(
    result.filter((p) => p.day === 2).map((p) => p.id),
    ['d2b', 'd2a'],
  );
});
