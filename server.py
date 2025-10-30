#!/usr/bin/env python3
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from api import api_blueprint
from config import AUTO_REFRESH_INTERVAL
from utils import get_user_lang, load_translations

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)


@app.route('/api')
def api_root():
    return jsonify({"status": "ok"})
app.register_blueprint(api_blueprint, url_prefix='/api')

@app.route('/')
def index():
    lang = get_user_lang()
    translations = load_translations(lang)
    return render_template("index.html", lang=lang, translations=translations, AUTO_REFRESH_INTERVAL=AUTO_REFRESH_INTERVAL)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
