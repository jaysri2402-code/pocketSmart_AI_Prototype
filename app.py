from flask import Flask, render_template, request, jsonify
import sqlite3, os, uuid

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

DB = "pocketsmart.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            budget REAL NOT NULL,
            occasion TEXT NOT NULL,
            style TEXT NOT NULL,
            outfit_image TEXT,
            selected_products TEXT,
            total REAL,
            remaining REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

PRODUCTS = [
    {"id": 1, "name": "Temple Gold-Tone Necklace", "type": "Necklace", "price": 1999, "color": "Gold", "style": "Traditional", "occasion": "Wedding"},
    {"id": 2, "name": "Classic Gold Jhumka", "type": "Earrings", "price": 799, "color": "Gold", "style": "Traditional", "occasion": "Wedding"},
    {"id": 3, "name": "Traditional Bangles Set", "type": "Bangles", "price": 699, "color": "Gold", "style": "Traditional", "occasion": "Wedding"},
    {"id": 4, "name": "Minimal Pearl Necklace", "type": "Necklace", "price": 1499, "color": "Pearl", "style": "Minimal", "occasion": "Birthday"},
    {"id": 5, "name": "Elegant Pearl Studs", "type": "Earrings", "price": 599, "color": "Pearl", "style": "Minimal", "occasion": "Party"},
    {"id": 6, "name": "Modern Silver Chain", "type": "Necklace", "price": 1299, "color": "Silver", "style": "Modern", "occasion": "Party"},
    {"id": 7, "name": "Modern Hoop Earrings", "type": "Earrings", "price": 499, "color": "Silver", "style": "Modern", "occasion": "Birthday"},
    {"id": 8, "name": "Bridal Kundan Set", "type": "Jewelry Set", "price": 2999, "color": "Gold", "style": "Bridal", "occasion": "Wedding"},
    {"id": 9, "name": "Elegant Stone Bracelet", "type": "Bracelet", "price": 899, "color": "Rose Gold", "style": "Elegant", "occasion": "Party"},
    {"id": 10, "name": "Classic Pearl Bracelet", "type": "Bracelet", "price": 749, "color": "Pearl", "style": "Elegant", "occasion": "Birthday"},
]

def recommend(budget, occasion, style):
    # Prototype recommendation engine.
    # Replace this function with Gemini API logic later.
    exact = [p for p in PRODUCTS if p["style"] == style and p["occasion"] == occasion]
    style_matches = [p for p in PRODUCTS if p["style"] == style and p not in exact]
    occasion_matches = [p for p in PRODUCTS if p["occasion"] == occasion and p not in exact and p not in style_matches]
    candidates = exact + style_matches + occasion_matches + PRODUCTS

    result = []
    total = 0
    seen = set()
    for p in candidates:
        if p["id"] in seen:
            continue
        if p["price"] <= budget - total:
            result.append(p)
            total += p["price"]
            seen.add(p["id"])
        if len(result) == 3:
            break

    # If three items cannot fit, show the best affordable alternatives.
    if not result:
        affordable = sorted([p for p in PRODUCTS if p["price"] <= budget],
                            key=lambda x: (x["style"] != style, x["occasion"] != occasion, x["price"]))
        result = affordable[:3]
        total = sum(p["price"] for p in result)

    return result, total

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/api/recommend")
def api_recommend():
    try:
        budget = float(request.form.get("budget", 0))
        occasion = request.form.get("occasion", "Wedding")
        style = request.form.get("style", "Traditional")
        image = request.files.get("outfit")

        image_name = None
        if image and image.filename:
            ext = os.path.splitext(image.filename)[1].lower() or ".jpg"
            image_name = f"{uuid.uuid4().hex}{ext}"
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_name))

        products, total = recommend(budget, occasion, style)
        remaining = round(budget - total, 2)

        conn = get_db()
        cur = conn.execute(
            """INSERT INTO recommendations
               (budget, occasion, style, outfit_image, selected_products, total, remaining)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (budget, occasion, style, image_name, json.dumps(products), total, remaining)
        )
        conn.commit()
        recommendation_id = cur.lastrowid
        conn.close()

        return jsonify({
            "success": True,
            "id": recommendation_id,
            "budget": budget,
            "occasion": occasion,
            "style": style,
            "products": products,
            "total": total,
            "remaining": remaining,
            "image": f"/uploads/{image_name}" if image_name else None,
            "message": "Prototype recommendation generated successfully."
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.get("/api/history")
def history():
    conn = get_db()
    rows = conn.execute("""
        SELECT id, budget, occasion, style, total, remaining, created_at
        FROM recommendations ORDER BY id DESC LIMIT 10
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.get("/uploads/<filename>")
def uploaded_file(filename):
    from flask import send_from_directory
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
