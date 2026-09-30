"""Thin PostgreSQL data-access layer (psycopg 3)."""
import os

import psycopg

_initialised = False


def _dsn():
    return os.environ["DATABASE_URL"]


def _connect():
    return psycopg.connect(_dsn(), connect_timeout=3)


def _init(conn):
    global _initialised
    if not _initialised:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS notes ("
            " id SERIAL PRIMARY KEY,"
            " text TEXT NOT NULL,"
            " created_at TIMESTAMPTZ NOT NULL DEFAULT now())"
        )
        conn.commit()
        _initialised = True


def ping():
    with _connect() as conn:
        _init(conn)
        conn.execute("SELECT 1")


def list_notes():
    with _connect() as conn:
        _init(conn)
        rows = conn.execute(
            "SELECT id, text, created_at FROM notes ORDER BY id DESC LIMIT 50"
        ).fetchall()
    return [{"id": r[0], "text": r[1], "created_at": r[2].isoformat()} for r in rows]


def add_note(text):
    with _connect() as conn:
        _init(conn)
        row = conn.execute(
            "INSERT INTO notes (text) VALUES (%s) RETURNING id, text, created_at",
            (text,),
        ).fetchone()
        conn.commit()
    return {"id": row[0], "text": row[1], "created_at": row[2].isoformat()}
