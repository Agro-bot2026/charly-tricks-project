from flask import Blueprint, request, jsonify
import sqlite3
import json
from pywebpush import webpush, WebPushException

push_bp = Blueprint('push', __name__)

VAPID_PRIVATE_KEY = "TU_VAPID_PRIVATE_KEY"
VAPID_PUBLIC_KEY = "BNFBvrvkafVZ6HgA6cHaHzA349hhxNWaBPPveLr7UOzknwNnguOuxzRUuZvUfbM3roIxu9G-kdAH4V2eGYadJ0k"
VAPID_CLAIMS = {"sub": "mailto:info@charly-tricks.dev"}

DB = "/root/reviews_api/reviews.db"

def init_push_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS push_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subscription TEXT NOT NULL UNIQUE,
            fecha TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_push_db()

@push_bp.route("/api/vapid-public-key", methods=["GET"])
def vapid_public_key():
    return jsonify({"publicKey": VAPID_PUBLIC_KEY})

@push_bp.route("/api/subscribe", methods=["POST"])
def subscribe():
    from datetime import datetime
    sub = request.json
    conn = sqlite3.connect(DB)
    try:
        conn.execute(
            "INSERT OR IGNORE INTO push_subscriptions (subscription, fecha) VALUES (?, ?)",
            (json.dumps(sub), datetime.now().strftime("%d/%m/%Y"))
        )
        conn.commit()
        total = conn.execute("SELECT COUNT(*) FROM push_subscriptions").fetchone()[0]
    finally:
        conn.close()
    return jsonify({"ok": True, "total": total})

@push_bp.route("/api/send-notification", methods=["POST"])
def send_notification():
    # Protegido con clave secreta para que solo vos puedas enviar
    secret = request.headers.get("X-Secret")
    if secret != "TU_SECRETO_ENVIO":
        return jsonify({"error": "No autorizado"}), 401

    data = request.json
    title = data.get("title", "🍇 Viña San Martín")
    body = data.get("body", "¡Tenemos novedades!")
    url = data.get("url", "https://charly-tricks.dev")

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    subs = conn.execute("SELECT * FROM push_subscriptions").fetchall()
    conn.close()

    enviados = 0
    fallidos = 0
    for s in subs:
        try:
            webpush(
                subscription_info=json.loads(s["subscription"]),
                data=json.dumps({"title": title, "body": body, "url": url}),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims=dict(VAPID_CLAIMS)
            )
            enviados += 1
        except WebPushException:
            fallidos += 1

    return jsonify({"ok": True, "enviados": enviados, "fallidos": fallidos})
