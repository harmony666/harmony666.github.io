const KV_KEY = 'itinerary:v1';
const ALLOWED_ORIGINS = [
  'https://harmony666.github.io',
  'http://localhost:8000',
  'http://127.0.0.1:8000',
];

function corsHeaders(request) {
  const origin = request.headers.get('Origin') || '';
  const allow = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': allow,
    'Access-Control-Allow-Methods': 'GET,PUT,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type,X-Edit-Password',
    'Access-Control-Max-Age': '86400',
    Vary: 'Origin',
  };
}

function jsonResponse(body, status, request) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      ...corsHeaders(request),
    },
  });
}

function readSeed(env) {
  if (env.SEED_DOC && typeof env.SEED_DOC === 'object') {
    return JSON.parse(JSON.stringify(env.SEED_DOC));
  }
  throw new Error('SEED_DOC missing');
}

function basicValidateDoc(doc) {
  if (!doc || doc.schemaVersion !== 1 || !Array.isArray(doc.points)) {
    throw new Error('文档格式无效');
  }
  if (!Number.isInteger(doc.version) || doc.version < 1) {
    throw new Error('version 无效');
  }
  for (const p of doc.points) {
    if (typeof p.id !== 'string' || !p.id.trim()) throw new Error('点 ID 无效');
    if (!Number.isInteger(p.day) || p.day < 1 || p.day > 9) throw new Error('日期无效');
  }
  return doc;
}

async function readDoc(env) {
  const raw = await env.ITINERARY_KV.get(KV_KEY);
  if (!raw) {
    const seed = basicValidateDoc(readSeed(env));
    seed.updatedAt = new Date().toISOString();
    await env.ITINERARY_KV.put(KV_KEY, JSON.stringify(seed));
    return seed;
  }
  return basicValidateDoc(JSON.parse(raw));
}

function checkPassword(request, env) {
  const got = request.headers.get('X-Edit-Password') || '';
  const expect = env.EDIT_PASSWORD || '';
  if (!expect || got !== expect) return false;
  return true;
}

async function handleRequest(request, env) {
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: corsHeaders(request) });
  }

  const url = new URL(request.url);
  const path = url.pathname.replace(/\/+$/, '') || '/';

  if (request.method === 'GET' && path === '/api/itinerary') {
    const doc = await readDoc(env);
    return jsonResponse(doc, 200, request);
  }

  if (request.method === 'PUT' && path === '/api/itinerary') {
    if (!checkPassword(request, env)) {
      return jsonResponse({ error: '口令错误或未配置' }, 401, request);
    }
    let body;
    try {
      body = await request.json();
    } catch (_) {
      return jsonResponse({ error: 'JSON 无效' }, 400, request);
    }
    const current = await readDoc(env);
    const clientVersion = Number(body.version);
    if (!Number.isInteger(clientVersion)) {
      return jsonResponse({ error: '缺少 version' }, 400, request);
    }
    if (clientVersion !== current.version) {
      return jsonResponse(
        {
          error: '版本冲突，请刷新后重试',
          version: current.version,
          updatedAt: current.updatedAt,
        },
        409,
        request,
      );
    }
    if (!Array.isArray(body.points)) {
      return jsonResponse({ error: 'points 必须是数组' }, 400, request);
    }
    const next = {
      schemaVersion: 1,
      version: current.version + 1,
      updatedAt: new Date().toISOString(),
      title: typeof body.title === 'string' ? body.title : current.title,
      points: body.points,
    };
    try {
      basicValidateDoc(next);
    } catch (e) {
      return jsonResponse({ error: e.message || String(e) }, 400, request);
    }
    await env.ITINERARY_KV.put(KV_KEY, JSON.stringify(next));
    return jsonResponse(next, 200, request);
  }

  if (request.method === 'POST' && path === '/api/itinerary/reset') {
    if (!checkPassword(request, env)) {
      return jsonResponse({ error: '口令错误或未配置' }, 401, request);
    }
    const current = await readDoc(env);
    const seed = basicValidateDoc(readSeed(env));
    const next = {
      ...seed,
      version: current.version + 1,
      updatedAt: new Date().toISOString(),
    };
    await env.ITINERARY_KV.put(KV_KEY, JSON.stringify(next));
    return jsonResponse(next, 200, request);
  }

  return jsonResponse({ error: 'Not Found' }, 404, request);
}

function createMemoryKv() {
  const store = new Map();
  return {
    async get(key) {
      return store.has(key) ? store.get(key) : null;
    },
    async put(key, value) {
      store.set(key, value);
    },
  };
}

module.exports = {
  KV_KEY,
  ALLOWED_ORIGINS,
  handleRequest,
  createMemoryKv,
  basicValidateDoc,
};
