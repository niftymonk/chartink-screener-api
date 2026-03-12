import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='public')
CORS(app)

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
})

SCREENERS = {
    'green-candle': {
        'slug': 'daily-green-candle',
        'clause': '( {cash} ( latest close > latest open ) )',
        'label': 'Daily Green Candle',
    },
    'red-candle': {
        'slug': 'daily-red-candle',
        'clause': '( {cash} ( latest close < latest open ) )',
        'label': 'Daily Red Candle',
    },
}

PROCESS_URL = 'https://chartink.com/screener/process'


def get_csrf(slug):
    url = 'https://chartink.com/screener/' + slug
    resp = SESSION.get(url, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    csrf_tag = soup.find('meta', {'name': 'csrf-token'})
    csrf = csrf_tag['content'] if csrf_tag else ''
    clause = ''
    clause_tag = soup.find('textarea', {'id': 'scan_clause'}) or soup.find('input', {'name': 'scan_clause'})
    if clause_tag:
        clause = clause_tag.get_text() or clause_tag.get('value', '')
    if not clause:
        match = re.search(r"scan_clause['\"]?\s*[=:]\s*['\"](.+?)['\"]", resp.text)
        if match:
            clause = match.group(1)
    return csrf, clause


def fetch_screener(key):
    screener = SCREENERS.get(key)
    if not screener:
        return None, 'Unknown screener key: ' + key
    try:
        csrf, clause = get_csrf(screener['slug'])
        if not clause:
            clause = screener['clause']
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-TOKEN': csrf,
            'Referer': 'https://chartink.com/screener/' + screener['slug'],
            'Accept': 'application/json, text/javascript, */*; q=0.01',
        }
        resp = SESSION.post(PROCESS_URL, data={'scan_clause': clause}, headers=headers, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        return data.get('data', []), None
    except Exception as e:
        return None, str(e)


@app.route('/api/screener/<key>')
def screener(key):
    data, error = fetch_screener(key)
    if error:
        return jsonify({'success': False, 'error': error}), 500
    return jsonify({'success': True, 'data': data, 'count': len(data)})


@app.route('/api/screeners')
def list_screeners():
    return jsonify({'screeners': [
        {'key': k, 'label': v['label']} for k, v in SCREENERS.items()
    ]})


@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'python': '3.13'})


@app.route('/')
def index():
    return send_from_directory('public', 'index.html')


@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('public', path)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
