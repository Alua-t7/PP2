import psycopg2
from psycopg2 import sql
from datetime import datetime
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

_conn = None   # module-level connection (lazy)


def _connect():
    global _conn
    if _conn is None or _conn.closed:
        _conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT,
            dbname=DB_NAME, user=DB_USER, password=DB_PASS
        )
        _conn.autocommit = False
    return _conn


def init_db():
    """Create tables if they don't exist. Safe to call on every startup."""
    try:
        conn = _connect()
        cur  = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id       SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id            SERIAL PRIMARY KEY,
                player_id     INTEGER REFERENCES players(id),
                score         INTEGER   NOT NULL,
                level_reached INTEGER   NOT NULL,
                played_at     TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"[DB] init_db failed: {e}")
        return False


def get_or_create_player(username: str) -> int | None:
    """Return player id, creating the row if needed."""
    try:
        conn = _connect()
        cur  = conn.cursor()
        cur.execute("SELECT id FROM players WHERE username = %s", (username,))
        row = cur.fetchone()
        if row:
            cur.close()
            return row[0]
        cur.execute("INSERT INTO players (username) VALUES (%s) RETURNING id", (username,))
        pid = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return pid
    except Exception as e:
        print(f"[DB] get_or_create_player failed: {e}")
        try: _conn.rollback()
        except: pass
        return None


def save_session(username: str, score: int, level: int) -> bool:
    """Insert a game session row."""
    try:
        pid = get_or_create_player(username)
        if pid is None:
            return False
        conn = _connect()
        cur  = conn.cursor()
        cur.execute(
            "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
            (pid, score, level)
        )
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"[DB] save_session failed: {e}")
        try: _conn.rollback()
        except: pass
        return False


def get_leaderboard(limit=10) -> list[dict]:
    """Return top-N scores across all players."""
    try:
        conn = _connect()
        cur  = conn.cursor()
        cur.execute("""
            SELECT p.username, gs.score, gs.level_reached, gs.played_at
            FROM game_sessions gs
            JOIN players p ON p.id = gs.player_id
            ORDER BY gs.score DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        cur.close()
        return [
            {"username": r[0], "score": r[1], "level": r[2],
             "date": r[3].strftime("%Y-%m-%d") if r[3] else ""}
            for r in rows
        ]
    except Exception as e:
        print(f"[DB] get_leaderboard failed: {e}")
        return []


def get_personal_best(username: str) -> int:
    """Return the player's highest score ever, or 0."""
    try:
        conn = _connect()
        cur  = conn.cursor()
        cur.execute("""
            SELECT MAX(gs.score)
            FROM game_sessions gs
            JOIN players p ON p.id = gs.player_id
            WHERE p.username = %s
        """, (username,))
        row = cur.fetchone()
        cur.close()
        return row[0] if row and row[0] else 0
    except Exception as e:
        print(f"[DB] get_personal_best failed: {e}")
        return 0


def close():
    global _conn
    if _conn and not _conn.closed:
        _conn.close()
    _conn = None