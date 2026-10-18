import sqlite3
from pathlib import Path

from db.db_counter import DB_PATH
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

BASE = Path(__file__).resolve().parents[4]

router = APIRouter()


def query(sql: str, params: tuple = ()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]
    finally:
        conn.close()


def run_exists(run_id: int) -> bool:
    return bool(query("SELECT 1 FROM runs WHERE id = ?", (run_id,)))


@router.get("/")
def dashboard():
    return FileResponse(BASE / "static" / "index.html")


@router.get("/api/runs")
def list_runs():
    return query("SELECT * FROM runs ORDER BY id DESC")


@router.get("/api/runs/{run_id}/summary")
def run_summary(run_id: int):

    if not run_exists(run_id):
        raise HTTPException(404, "Run not found")
    rows = query(
        "SELECT direction, COUNT(*) AS n FROM crossings "
        "WHERE run_id = ? GROUP BY direction",
        (run_id,),
    )
    counts = {r["direction"]: r["n"] for r in rows}
    up = counts.get("up", 0)
    down = counts.get("down", 0)
    return {
        "run_id": run_id,
        "up_count": up,
        "down_count": down,
        "total_count": up - down,   
    }


@router.get("/api/runs/{run_id}/crossings")
def run_crossings(run_id: int, limit: int = 20):

    if not run_exists(run_id):
        raise HTTPException(404, "Run not found")
    return query(
        "SELECT track_id, direction, video_time_s, recorded_at "
        "FROM crossings WHERE run_id = ? ORDER BY id DESC LIMIT ?",
        (run_id, limit),
    )


@router.get("/api/runs/{run_id}/timeline")
def run_timeline(run_id: int, bucket: int = 10):

    if not run_exists(run_id):
        raise HTTPException(404, "Run not found")
    rows = query(
        "SELECT CAST(video_time_s / ? AS INTEGER) * ? AS t, direction, COUNT(*) AS n "
        "FROM crossings WHERE run_id = ? GROUP BY t, direction ORDER BY t",
        (bucket, bucket, run_id),
    )
    buckets = {}
    for r in rows:
        b = buckets.setdefault(r["t"], {"t": r["t"], "up": 0, "down": 0})
        b[r["direction"]] = r["n"]

    result, running = [], 0
    for t in sorted(buckets):
        b = buckets[t]
        running += b["up"] - b["down"]
        b["net_cumulative"] = running
        result.append(b)
    return result