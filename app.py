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
        r = s.get("https://chartink.com/screener/bullish-pullback-buy-signal", timeout=15)
        m = re.search(r'csrf-token" content="(.+?)"', r.text)
        h = {
            "Referer": "https://chartink.com/screener/bullish-pullback-buy-signal",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        if m:
            h["X-CSRF-TOKEN"] = m.group(1)
        p = {"scan_clause": "( {46553} (  1 day ago close >  1 day ago open and  daily close <  daily open and  daily high <=  1 day ago high and  daily low >=  1 day ago low and  daily close <=  1 day ago high -  (  (  1 day ago high -  1 day ago low ) *  0.5 ) and  daily close >=  1 day ago high -  (  (  1 day ago high -  1 day ago low ) *  0.6 ) ) )"}
        res = s.post("https://chartink.com/screener/process", data=p, headers=h, timeout=15)
        d = res.json()
        stocks = d.get("data", [])
        return jsonify({"success": True, "data": stocks})
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "data": []})

if __name__ == '__main__':
    app.run()
