from flask import Flask, jsonify
from flask_cors import CORS
import requests
import re

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
      return jsonify({"status": "ChartInk Screener API is running"})

@app.route('/api/screener')
def screener():
      try:
                session = requests.Session()
                r = session.get("https://chartink.com/screener/daily-green-candle", timeout=15)
                token_match = re.search(r'csrf-token" content="(.+?)"', r.text)
                headers = {
                    "Referer": "https://chartink.com/screener/daily-green-candle",
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                if token_match:
                              headers["X-CSRF-TOKEN"] = token_match.group(1)
                          payload = {"scan_clause": "( {cash} ( latest close > latest open ) )"}
                resp = session.post("https://chartink.com/screener/process", data=payload, headers=headers, timeout=15)
                data = resp.json()
                stocks = data.get("data", [])
                return jsonify({"success": True, "data": stocks, "count": len(stocks)})
except Exception as e:
        return jsonify({"success": False, "error": str(e), "data": []})

if __name__ == '__main__':
      app.run(debug=True)
