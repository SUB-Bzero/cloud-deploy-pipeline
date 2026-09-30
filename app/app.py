"""Notes API - small Flask app used for the cloud deployment capstone.

Endpoints
  GET  /            simple HTML landing page
  GET  /health      liveness + database readiness (used by ALB, Docker, CloudWatch)
  GET  /api/notes   list notes
  POST /api/notes   create a note  {"text": "..."}
  GET  /boom        deliberately returns HTTP 500 (used to demo the 5xx alarm,
                    only enabled when ENABLE_FAULT_ENDPOINT=true)
"""
import os

from flask import Flask, jsonify, request

import db

APP_VERSION = os.getenv("APP_VERSION", "dev")


def create_app():
    app = Flask(__name__)

    @app.get("/")
    def index():
        return (
            "<h1>Capstone: Automated Cloud Deployment Pipeline</h1>"
            f"<p>Version: <b>{APP_VERSION}</b></p>"
            "<ul><li><a href='/health'>/health</a></li>"
            "<li><a href='/api/notes'>/api/notes</a></li></ul>"
        )

    @app.get("/health")
    def health():
        try:
            db.ping()
            database = "up"
        except Exception:  # noqa: BLE001 - any DB failure means "not ready"
            database = "down"
        status = "ok" if database == "up" else "degraded"
        code = 200 if database == "up" else 503
        return jsonify(status=status, database=database, version=APP_VERSION), code

    @app.get("/api/notes")
    def list_notes():
        return jsonify(notes=db.list_notes())

    @app.post("/api/notes")
    def add_note():
        payload = request.get_json(silent=True) or {}
        text = str(payload.get("text", "")).strip()
        if not text:
            return jsonify(error="'text' is required"), 400
        return jsonify(db.add_note(text)), 201

    if os.getenv("ENABLE_FAULT_ENDPOINT", "false").lower() == "true":

        @app.get("/boom")
        def boom():
            return jsonify(error="simulated failure"), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
