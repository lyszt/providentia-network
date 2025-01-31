import json

# Essential
import flask
from flask import request, Flask, jsonify
import logging
# Tools
from rich.console import Console
from rich.markdown import Markdown
# IMPORTED MODULES
from Modules.Configuration.configure import *
app = Flask(__name__)
console = Console()

with open('index.html') as f:
    index_html = f.read()

@app.after_request
def after_request(response: flask.Response):
    logging.info(f"Request received: {response}")
    console.print(Markdown(Outils().logResponse(request)))
    return response
@app.route('/')
def index():
    return index_html

if __name__ == '__main__':
    Setuṕ()
    app.run(debug=True)

