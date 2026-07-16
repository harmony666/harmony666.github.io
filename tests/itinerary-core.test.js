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

test('normalizePoints sorts each day by time', () => {
  const result = Core.normalizePoints([
    point('b', 2, '11:00', 1),
    point('a', 2, '09:00', 2),
    point('c', 2, '09:30', 3),
  ]);
  assert.deepEqual(result.map((p) => p.id), ['a', 'c', 'b']);
  assert.deepEqual(result.map((p) => p.position), [1, 2, 3]);
});

test('updatePoint edits fields and reorders by time', () => {
  const points = [
    point('a', 1, '09:00', 1),
    point('b', 1, '11:00', 2),
    point('c', 2, '10:00', 1),
  ];
  const result = Core.updatePoint(points, {
    ...point('b', 1, '08:30', 2),
    title: '早到',
    name: '早到',
    desc: '改时间',
  });
  assert.deepEqual(
    result.filter((p) => p.day === 1).map((p) => p.id),
    ['b', 'a'],
  );
  assert.equal(result.find((p) => p.id === 'b').title, '早到');
  assert.throws(
    () => Core.updatePoint(points, point('missing', 1, '12:00', 9)),
    /不存在/,
  );
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

test('normalizePoints rejects non-string ids and trims valid string ids', () => {
  for (const invalidId of [123, {}, []]) {
    assert.throws(
      () => Core.normalizePoints([point(invalidId, 1, '09:00', 1)]),
      /ID/,
    );
  }
  assert.equal(
    Core.normalizePoints([point('  valid-id  ', 1, '09:00', 1)])[0].id,
    'valid-id',
  );
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

test('reorderDay keeps other days and time sort wins within a day', () => {
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
    ['d2a', 'd2b'],
  );
});
