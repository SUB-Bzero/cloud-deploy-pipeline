import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app as app_module  # noqa: E402
import db  # noqa: E402


@pytest.fixture()
def client(monkeypatch):
    store = []

    monkeypatch.setattr(db, "ping", lambda: None)
    monkeypatch.setattr(db, "list_notes", lambda: list(reversed(store)))

    def fake_add(text):
        note = {"id": len(store) + 1, "text": text, "created_at": "2026-01-01T00:00:00"}
        store.append(note)
        return note

    monkeypatch.setattr(db, "add_note", fake_add)
    return app_module.create_app().test_client()


def test_index_ok(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Capstone" in res.data


def test_health_ok(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"
    assert res.get_json()["database"] == "up"


def test_health_returns_503_when_db_down(client, monkeypatch):
    def broken():
        raise RuntimeError("db unreachable")

    monkeypatch.setattr(db, "ping", broken)
    res = client.get("/health")
    assert res.status_code == 503
    assert res.get_json()["database"] == "down"


def test_create_and_list_notes(client):
    assert client.post("/api/notes", json={"text": "hello"}).status_code == 201
    notes = client.get("/api/notes").get_json()["notes"]
    assert notes[0]["text"] == "hello"


def test_create_note_validation(client):
    res = client.post("/api/notes", json={"text": "   "})
    assert res.status_code == 400


def test_fault_endpoint_disabled_by_default(client):
    assert client.get("/boom").status_code == 404


def test_fault_endpoint_enabled(monkeypatch):
    monkeypatch.setenv("ENABLE_FAULT_ENDPOINT", "true")
    c = app_module.create_app().test_client()
    assert c.get("/boom").status_code == 500
