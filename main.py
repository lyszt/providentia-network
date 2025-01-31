import json

from flask import request, Flask, jsonify
import logging

app = Flask(__name__)
with open('index.html') as f:
    index_html = f.read()
@app.route('/')
def index():
    return index_html

@app.route('/', method=['GET'])
def response():
    resp = jsonify({'success': True})
    resp.status_code = 200
    return resp
if __name__ == '__main__':
    app.run()

