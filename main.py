from flask import request, Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"message": "Active."})

if __name__ == '__main__':
    app.run()