from flask import request, Flask, jsonify

app = Flask(__name__)
with open('index.html') as f:
    index_html = f.read()
@app.route('/')
def index():
    return index_html
if __name__ == '__main__':
    app.run()