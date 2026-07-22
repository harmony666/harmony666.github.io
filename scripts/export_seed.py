#!/usr/bin/env python3
"""从 coords.json 导出 Worker 用 seed.json（与 generate_html 的 id/position 规则一致）。"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "coords.json").read_text(encoding="utf-8"))

groups = {}
for p in data:
    groups.setdefault(p["day"], []).append(p)

points = []
for d in sorted(groups):
    for i, p in enumerate(groups[d], 1):
        points.append({
            "id": f"seed-{d}-{i}",
            "day": p["day"],
            "cat": p["cat"],
            "time": p["time"],
            "title": p["title"],
            "desc": p.get("desc", ""),
            "city": p["city"],
            "name": p["name"],
            "lat": p["lat"],
            "lng": p["lng"],
            "position": i,
        })

doc = {
    "schemaVersion": 1,
    "version": 1,
    "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
    "title": "武汉 → 山东 9日旅行计划",
    "points": points,
}

out = ROOT / "workers" / "itinerary-api" / "src" / "seed.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"OK wrote {out} points={len(points)}")
