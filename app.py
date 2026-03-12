from flask import Flask, jsonify
from flask_cors import CORS
import requests
import re

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"status": "ok"})

@app.route('/api/screener')
def screener():
    try:
        s = requests.Session()
        r = s.get("https://chartink.com/screener/daily-green-candle", timeout=15)
        m = re.search(r'csrf-token" content="(.+?)"', r.text)
        h = {
            "Referer": "https://chartink.com/screener/daily-green-candle",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        if m:
            h["X-CSRF-TOKEN"] = m.group(1)
        p = {"scan_clause": "( {cash} ( latest close > latest open ) )"}
        res = s.post("https://chartink.com/screener/process", data=p, headers=h, timeout=15)
        d = res.json()
        stocks = d.get("data", [])
        return jsonify({"success": True, "data": stocks})
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "data": []})

if __name__ == '__main__':
    app.run()
