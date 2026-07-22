const fs = require('fs');
const path = require('path');
const express = require('express');

const PORT = Number(process.env.PORT || 8787);
const EDIT_PASSWORD = process.env.EDIT_PASSWORD || '';
const DATA_DIR = process.env.DATA_DIR || path.join(__dirname, '..', 'data');
const DOC_PATH = path.join(DATA_DIR, 'itinerary.json');
const SEED_PATH = path.join(__dirname, 'seed.json');

const ALLOWED_ORIGINS = [
  'https://harmony666.github.io',
  'http://localhost:8000',
  'http://127.0.0.1:8000',
];

function corsMiddleware(req, res, next) {
  const origin = req.headers.origin || '';
  const allow = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  res.setHeader('Access-Control-Allow-Origin', allow);
  res.setHeader('Access-Control-Allow-Methods', 'GET,PUT,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type,X-Edit-Password');
  res.setHeader('Access-Control-Max-Age', '86400');
  res.setHeader('Vary', 'Origin');
  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }
  return next();
}

function readSeed() {
  return JSON.parse(fs.readFileSync(SEED_PATH, 'utf8'));
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

function ensureDataDir() {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

function readDoc() {
  ensureDataDir();
  if (!fs.existsSync(DOC_PATH)) {
    const seed = basicValidateDoc(readSeed());
    seed.updatedAt = new Date().toISOString();
    fs.writeFileSync(DOC_PATH, JSON.stringify(seed), 'utf8');
    return seed;
  }
  return basicValidateDoc(JSON.parse(fs.readFileSync(DOC_PATH, 'utf8')));
}

function writeDoc(doc) {
  ensureDataDir();
  const tmp = DOC_PATH + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(doc), 'utf8');
  fs.renameSync(tmp, DOC_PATH);
}

function checkPassword(req) {
  const got = req.get('X-Edit-Password') || '';
  return !!(EDIT_PASSWORD && got === EDIT_PASSWORD);
}

const app = express();
app.disable('x-powered-by');
app.use(corsMiddleware);
app.use(express.json({ limit: '2mb' }));

app.get('/api/itinerary', (_req, res) => {
  try {
    res.json(readDoc());
  } catch (e) {
    res.status(500).json({ error: e.message || String(e) });
  }
});

app.put('/api/itinerary', (req, res) => {
  if (!checkPassword(req)) {
    return res.status(401).json({ error: '口令错误或未配置' });
  }
  try {
    const body = req.body || {};
    const current = readDoc();
    const clientVersion = Number(body.version);
    if (!Number.isInteger(clientVersion)) {
      return res.status(400).json({ error: '缺少 version' });
    }
    if (clientVersion !== current.version) {
      return res.status(409).json({
        error: '版本冲突，请刷新后重试',
        version: current.version,
        updatedAt: current.updatedAt,
      });
    }
    if (!Array.isArray(body.points)) {
      return res.status(400).json({ error: 'points 必须是数组' });
    }
    const next = {
      schemaVersion: 1,
      version: current.version + 1,
      updatedAt: new Date().toISOString(),
      title: typeof body.title === 'string' ? body.title : current.title,
      points: body.points,
    };
    basicValidateDoc(next);
    writeDoc(next);
    return res.json(next);
  } catch (e) {
    return res.status(400).json({ error: e.message || String(e) });
  }
});

app.post('/api/itinerary/reset', (req, res) => {
  if (!checkPassword(req)) {
    return res.status(401).json({ error: '口令错误或未配置' });
  }
  try {
    const current = readDoc();
    const seed = basicValidateDoc(readSeed());
    const next = {
      ...seed,
      version: current.version + 1,
      updatedAt: new Date().toISOString(),
    };
    writeDoc(next);
    return res.json(next);
  } catch (e) {
    return res.status(500).json({ error: e.message || String(e) });
  }
});

app.get('/healthz', (_req, res) => {
  res.json({ ok: true });
});

app.use((_req, res) => {
  res.status(404).json({ error: 'Not Found' });
});

app.listen(PORT, '0.0.0.0', () => {
  // eslint-disable-next-line no-console
  console.log(`itinerary-api listening on ${PORT}`);
});
