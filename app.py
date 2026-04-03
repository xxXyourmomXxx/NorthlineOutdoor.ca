from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
import requests

app = Flask(__name__)

# 🔥 CORS fix: allow your live site (and optionally localhost for testing)
CORS(app, resources={r"/*": {"origins": ["https://northlineoutdoor.ca", "http://127.0.0.1:5500"]}})

DATABASE_URL = os.environ.get("DATABASE_URL")

# For Heroku/PostgreSQL URL compatibility
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def get_conn():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

@app.route('/')
def home():
    return "Backend running"

@app.route('/track', methods=['POST', 'OPTIONS'])
def track():
    # Handle preflight request
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json(force=True)
        visitor_id = data.get('visitor_id')
        page = data.get('page')

        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent')

        # Geolocation (optional)
        country, city = None, None
        try:
            geo = requests.get(f"http://ip-api.com/json/{ip}", timeout=2).json()
            country = geo.get('country')
            city = geo.get('city')
        except:
            pass

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO visits 
            (visitor_id, ip_address, country, city, page_visited, user_agent)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (visitor_id, ip, country, city, page, user_agent))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"status": "ok"})

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    app.run()