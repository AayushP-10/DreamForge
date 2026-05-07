import os
import sqlite3
from datetime import datetime, timezone
from typing import List
from flask import Flask, jsonify, request, send_file

from main import build_user_request, generate_story_payload


app = Flask(__name__)
DB_PATH = "dreamforge.db"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db()
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                story TEXT NOT NULL,
                score_total INTEGER,
                passed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_memory (
                user_id INTEGER PRIMARY KEY,
                memory_json TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_stories_user_id ON stories(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_stories_created_at ON stories(created_at DESC)")
        conn.commit()
    finally:
        conn.close()

init_db()


@app.get("/")
def index():
    return send_file("code.html")


@app.post("/api/auth/signup")
def signup():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    if not name or not email:
        return jsonify({"error": "Name and email are required."}), 400

    now = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO users(name, email, created_at) VALUES (?, ?, ?)",
            (name, email, now),
        )
        conn.commit()
        row = conn.execute("SELECT id, name, email FROM users WHERE email = ?", (email,)).fetchone()
        if not row:
            return jsonify({"error": "Could not create account."}), 500
        return jsonify({"id": row["id"], "name": row["name"], "email": row["email"]})
    finally:
        conn.close()


@app.get("/api/library/<int:user_id>")
def get_library(user_id: int):
    conn = get_db()
    try:
        rows = conn.execute(
            """
            SELECT id, title, story, score_total, passed, created_at
            FROM stories
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 30
            """,
            (user_id,),
        ).fetchall()
        payload = [
            {
                "id": row["id"],
                "title": row["title"],
                "preview": (row["story"][:220] + "...") if len(row["story"]) > 220 else row["story"],
                "score_total": row["score_total"],
                "passed": bool(row["passed"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]
        return jsonify({"stories": payload})
    finally:
        conn.close()


@app.get("/api/performance/<int:user_id>")
def get_performance(user_id: int):
    conn = get_db()
    try:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS total_stories,
                COALESCE(AVG(score_total), 0) AS avg_score,
                COALESCE(SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END), 0) AS passed_count
            FROM stories
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()
        recent_rows = conn.execute(
            """
            SELECT title, score_total, passed, created_at
            FROM stories
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 8
            """,
            (user_id,),
        ).fetchall()

        total_stories = int(row["total_stories"] or 0)
        passed_count = int(row["passed_count"] or 0)
        pass_rate = (passed_count / total_stories * 100.0) if total_stories else 0.0

        return jsonify(
            {
                "total_stories": total_stories,
                "avg_score": round(float(row["avg_score"] or 0.0), 1),
                "passed_count": passed_count,
                "pass_rate": round(pass_rate, 1),
                "recent": [
                    {
                        "title": r["title"],
                        "score_total": r["score_total"],
                        "passed": bool(r["passed"]),
                        "created_at": r["created_at"],
                    }
                    for r in recent_rows
                ],
            }
        )
    finally:
        conn.close()


@app.get("/api/suggestions/<int:user_id>")
def get_suggestions(user_id: int):
    conn = get_db()
    try:
        user_row = conn.execute("SELECT name FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user_row:
            return jsonify({"suggestions": []})

        memory_row = conn.execute("SELECT memory_json FROM user_memory WHERE user_id = ?", (user_id,)).fetchone()
        memory = {}
        if memory_row and memory_row["memory_json"]:
            import json

            memory = json.loads(memory_row["memory_json"])

        recent_titles = conn.execute(
            """
            SELECT title
            FROM stories
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 6
            """,
            (user_id,),
        ).fetchall()
        title_text = [str(r["title"]) for r in recent_titles]
        themes = memory.get("recent_themes", [])
        if not isinstance(themes, list):
            themes = []
        top_themes = [str(t) for t in themes[:3] if str(t).strip()]

        name = str(user_row["name"]).strip() or "your child"
        base_ideas = [
            f"A gentle bedtime story starring {name} and a moon librarian who lends dreams safely.",
            f"A new {top_themes[0] if top_themes else 'friendship'} adventure where a tiny guide helps sleepy stars get home.",
            f"A calm sequel to '{title_text[0]}' with one new character and a softer ending.",
            f"A bedtime quest in a floating garden where worries turn into glowing paper cranes.",
        ]

        # Deduplicate while preserving order.
        deduped: List[str] = []
        seen = set()
        for item in base_ideas:
            key = item.strip().lower()
            if key and key not in seen:
                seen.add(key)
                deduped.append(item)

        return jsonify({"suggestions": deduped[:4]})
    finally:
        conn.close()


@app.post("/api/generate")
def generate_story():
    data = request.get_json(silent=True) or {}
    prompt = str(data.get("prompt", "")).strip()
    user_id = int(data.get("user_id", 0) or 0)
    if not prompt:
        return jsonify({"error": "Prompt is required."}), 400
    if user_id <= 0:
        return jsonify({"error": "Please sign in first."}), 400

    if not os.getenv("OPENAI_API_KEY"):
        return jsonify({"error": "Missing OPENAI_API_KEY environment variable."}), 500

    try:
        conn = get_db()
        try:
            memory_row = conn.execute("SELECT memory_json FROM user_memory WHERE user_id = ?", (user_id,)).fetchone()
            memory_card = {}
            if memory_row and memory_row["memory_json"]:
                import json

                memory_card = json.loads(memory_row["memory_json"])
        finally:
            conn.close()

        saga_mode = bool(data.get("saga_mode", False))
        saga_context = str(data.get("saga_context", "")).strip()
        if saga_mode and not saga_context:
            saga_context = str(memory_card.get("last_story_summary", "")).strip()

        user_request = build_user_request(
            prompt=prompt,
            age_band=str(data.get("age_band", "")).strip(),
            theme=str(data.get("theme", "")).strip(),
            characters=str(data.get("characters", "")).strip(),
            setting=str(data.get("setting", "")).strip(),
            bedtime_mode=bool(data.get("bedtime_mode", True)),
            reading_level=str(data.get("reading_level", "")).strip(),
            disallow_topics=str(data.get("disallow_topics", "")).strip(),
            saga_mode=saga_mode,
            saga_context=saga_context,
        )

        story_constraints = {
            "reading_level": str(data.get("reading_level", "")).strip(),
            "disallow_topics": str(data.get("disallow_topics", "")).strip(),
            "saga_mode": bool(data.get("saga_mode", False)),
        }
        payload = generate_story_payload(user_request, memory_card, story_constraints)
        title = f"{str(data.get('theme', 'Bedtime')).strip() or 'Bedtime'} Bedtime Story"
        conn = get_db()
        try:
            conn.execute(
                """
                INSERT INTO stories(user_id, title, story, score_total, passed, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    title,
                    payload.get("story", ""),
                    int(payload.get("score_total", 0) or 0),
                    1 if bool(payload.get("passed", False)) else 0,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()

            # Update continuity memory card for next-night personalization.
            import json

            existing = memory_card if isinstance(memory_card, dict) else {}
            theme = str(data.get("theme", "")).strip()
            recent_themes = existing.get("recent_themes", [])
            if not isinstance(recent_themes, list):
                recent_themes = []
            if theme:
                recent_themes.insert(0, theme)
            recent_themes = recent_themes[:8]

            updated_memory = {
                "recent_themes": recent_themes,
                "preferred_age_band": str(data.get("age_band", "")).strip(),
                "last_story_title": title,
                "last_story_summary": str(payload.get("story", ""))[:280],
                "episode_count": int(existing.get("episode_count", 0) or 0) + (1 if saga_mode else 0),
                "last_bedtime_state": payload.get("explainability", {}).get("bedtime_state", "neutral"),
                "successful_patterns": payload.get("explainability", {}).get("quality_strengths", [])[:3],
                "safety_notes": payload.get("explainability", {}).get("safety_strengths", [])[:3],
            }
            conn.execute(
                """
                INSERT INTO user_memory(user_id, memory_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    memory_json=excluded.memory_json,
                    updated_at=excluded.updated_at
                """,
                (user_id, json.dumps(updated_memory), datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()
        finally:
            conn.close()
        return jsonify(payload)
    except Exception as exc:  # pragma: no cover
        return jsonify({"error": f"Generation failed: {str(exc)}"}), 500


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "").strip().lower() in {"1", "true", "yes"}
    app.run(host="127.0.0.1", port=8000, debug=debug_mode, threaded=True)
