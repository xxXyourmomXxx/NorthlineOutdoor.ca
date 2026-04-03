from flask import Flask, request, jsonify, render_template
import psycopg2
import os
import requests

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/track', methods=['POST'])
def track():
    data = request.json

    visitor_id = data.get('visitor_id')
    page = data.get('page')

    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')

    # Get geolocation
    try:
        geo = requests.get(f"http://ip-api.com/json/{ip}", timeout=2).json()
        country = geo.get('country')
        city = geo.get('city')
    except:
        country, city = None, None

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

if __name__ == "__main__":
    app.run()