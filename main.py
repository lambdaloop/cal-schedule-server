from flask import Flask, jsonify, request
from flask.ext.cors import CORS
from flask.ext.compress import Compress

import os
import requests

app = Flask(__name__)
CORS(app)
Compress(app)

@app.route('/')
def hello():
    return "Hello, the server is running!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 33507))
    app.run(host='0.0.0.0', port=port, debug=True)

