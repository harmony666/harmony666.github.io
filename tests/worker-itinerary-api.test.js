const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const path = require('path');
const {
  handleRequest,
  createMemoryKv,
} = require('../workers/itinerary-api/src/app.cjs');
const seed = require('../workers/itinerary-api/src/seed.json');

function env(password) {
  return {
    EDIT_PASSWORD: password,
    ITINERARY_KV: createMemoryKv(),
    SEED_DOC: seed,
  };
}

function req(method, urlPath, { password, body } = {}) {
  const headers = new Headers();
  if (password != null) headers.set('X-Edit-Password', password);
  if (body !== undefined) headers.set('Content-Type', 'application/json');
  headers.set('Origin', 'https://harmony666.github.io');
  return new Request('https://example.com' + urlPath, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
}

describe('itinerary worker api', () => {
  it('GET seeds empty KV', async () => {
    const e = env('secret');
    const res = await handleRequest(req('GET', '/api/itinerary'), e);
    assert.equal(res.status, 200);
    const doc = await res.json();
    assert.equal(doc.schemaVersion, 1);
    assert.equal(doc.version, 1);
    assert.equal(doc.points.length, 43);
  });

  it('PUT without password returns 401', async () => {
    const e = env('secret');
    await handleRequest(req('GET', '/api/itinerary'), e);
    const res = await handleRequest(
      req('PUT', '/api/itinerary', { body: { version: 1, points: seed.points } }),
      e,
    );
    assert.equal(res.status, 401);
  });

  it('PUT with wrong password returns 401', async () => {
    const e = env('secret');
    await handleRequest(req('GET', '/api/itinerary'), e);
    const res = await handleRequest(
      req('PUT', '/api/itinerary', {
        password: 'nope',
        body: { version: 1, points: seed.points },
      }),
      e,
    );
    assert.equal(res.status, 401);
  });

  it('PUT success bumps version', async () => {
    const e = env('secret');
    await handleRequest(req('GET', '/api/itinerary'), e);
    const points = seed.points.map((p) => ({ ...p }));
    points[0] = { ...points[0], title: '改过的标题' };
    const res = await handleRequest(
      req('PUT', '/api/itinerary', {
        password: 'secret',
        body: { version: 1, title: seed.title, points },
      }),
      e,
    );
    assert.equal(res.status, 200);
    const doc = await res.json();
    assert.equal(doc.version, 2);
    assert.equal(doc.points[0].title, '改过的标题');
  });

  it('PUT stale version returns 409', async () => {
    const e = env('secret');
    await handleRequest(req('GET', '/api/itinerary'), e);
    await handleRequest(
      req('PUT', '/api/itinerary', {
        password: 'secret',
        body: { version: 1, points: seed.points },
      }),
      e,
    );
    const res = await handleRequest(
      req('PUT', '/api/itinerary', {
        password: 'secret',
        body: { version: 1, points: seed.points },
      }),
      e,
    );
    assert.equal(res.status, 409);
    const body = await res.json();
    assert.equal(body.version, 2);
  });

  it('POST reset restores seed and bumps version', async () => {
    const e = env('secret');
    await handleRequest(req('GET', '/api/itinerary'), e);
    const points = seed.points.map((p) => ({ ...p, title: p.title + 'x' }));
    await handleRequest(
      req('PUT', '/api/itinerary', {
        password: 'secret',
        body: { version: 1, points },
      }),
      e,
    );
    const res = await handleRequest(
      req('POST', '/api/itinerary/reset', { password: 'secret' }),
      e,
    );
    assert.equal(res.status, 200);
    const doc = await res.json();
    assert.equal(doc.version, 3);
    assert.equal(doc.points[0].title, seed.points[0].title);
  });

  it('OPTIONS returns CORS headers', async () => {
    const e = env('secret');
    const res = await handleRequest(req('OPTIONS', '/api/itinerary'), e);
    assert.equal(res.status, 204);
    assert.equal(
      res.headers.get('Access-Control-Allow-Origin'),
      'https://harmony666.github.io',
    );
  });
});
