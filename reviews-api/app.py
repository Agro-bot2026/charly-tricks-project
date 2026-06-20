from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import time
from datetime import datetime
from openai import OpenAI

app = Flask(__name__)
CORS(app)

DEEPSEEK_API_KEY = "TU_API_KEY_DEEPSEEK"
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

DB = "/root/reviews_api/reviews.db"

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            estrellas INTEGER NOT NULL,
            comentario TEXT NOT NULL,
            respuesta TEXT,
            fecha TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

def generar_respuesta(nombre, estrellas, comentario):
    prompt = f"""Un cliente dejó esta reseña en la web de Viña San Martín (venta de uva en fresco en Mendoza):
Nombre: {nombre}
Estrellas: {estrellas}/5
Comentario: {comentario}

Respondé de forma breve, cálida y profesional como "Equipo de Viña San Martín". Máximo 2 oraciones. En español argentino. Agradecé y si es crítica negativa, mostrá disposición a mejorar."""
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return resp.choices[0].message.content.strip()
    except:
        return "¡Gracias por tu reseña! Saludos del Equipo de Viña San Martín."

@app.route("/api/reviews", methods=["GET"])
def get_reviews():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM reviews ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    reviews = [dict(r) for r in rows]
    # Calcular promedio
    if reviews:
        promedio = round(sum(r["estrellas"] for r in reviews) / len(reviews), 1)
    else:
        promedio = 0
    return jsonify({"reviews": reviews, "promedio": promedio, "total": len(reviews)})

@app.route("/api/reviews", methods=["POST"])
def add_review():
    data = request.json
    nombre = (data.get("nombre") or "").strip()[:50]
    estrellas = int(data.get("estrellas", 5))
    comentario = (data.get("comentario") or "").strip()[:500]

    if not nombre or not comentario or estrellas < 1 or estrellas > 5:
        return jsonify({"error": "Datos inválidos"}), 400

    respuesta = generar_respuesta(nombre, estrellas, comentario)
    fecha = datetime.now().strftime("%d/%m/%Y")

    conn = sqlite3.connect(DB)
    conn.execute(
        "INSERT INTO reviews (nombre, estrellas, comentario, respuesta, fecha) VALUES (?, ?, ?, ?, ?)",
        (nombre, estrellas, comentario, respuesta, fecha)
    )
    conn.commit()
    conn.close()

    return jsonify({"ok": True, "respuesta": respuesta})


@app.route("/api/schema", methods=["GET"])
def get_schema():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM reviews ORDER BY id DESC").fetchall()
    conn.close()
    reviews = [dict(r) for r in rows]
    if not reviews:
        return jsonify({"hasReviews": False})
    promedio = round(sum(r["estrellas"] for r in reviews) / len(reviews), 1)
    review_items = []
    for r in reviews[:20]:
        review_items.append({
            "@type": "Review",
            "author": {"@type": "Person", "name": r["nombre"]},
            "reviewRating": {"@type": "Rating", "ratingValue": str(r["estrellas"]), "bestRating": "5"},
            "reviewBody": r["comentario"]
        })
    return jsonify({
        "hasReviews": True,
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": str(promedio),
            "reviewCount": str(len(reviews)),
            "bestRating": "5"
        },
        "reviews": review_items
    })


@app.route("/reviews-schema.json", methods=["GET"])
def reviews_schema_json():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM reviews ORDER BY id DESC").fetchall()
    conn.close()
    reviews = [dict(r) for r in rows]
    if not reviews:
        return jsonify({})
    promedio = round(sum(r["estrellas"] for r in reviews) / len(reviews), 1)
    review_items = []
    for r in reviews[:20]:
        review_items.append({
            "@type": "Review",
            "author": {"@type": "Person", "name": r["nombre"]},
            "reviewRating": {"@type": "Rating", "ratingValue": str(r["estrellas"]), "bestRating": "5"},
            "reviewBody": r["comentario"]
        })
    schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": "Viña San Martín",
        "image": "https://charly-tricks.dev/og-image.webp",
        "address": {"@type": "PostalAddress", "addressLocality": "San Martín", "addressRegion": "Mendoza", "addressCountry": "AR"},
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": str(promedio), "reviewCount": str(len(reviews)), "bestRating": "5"},
        "review": review_items
    }
    return jsonify(schema)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
