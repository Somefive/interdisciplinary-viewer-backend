from flask import Flask, jsonify
from flask_cache import Cache
from lib import * 
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
cache = Cache(app,config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': 'cache', 'CACHE_THRESHOLD': 20000})

@app.route("/")
def hello():
  return "Hello World!"

@app.route("/analyze/<int:_id>")
@cache.cached()
def analyze(_id):
  return jsonify(getTopicAnalyze(_id, 10))

@app.route("/analyze/more/<int:_id>/<category>/<int:skip>/<int:limit>/<int:subParam>")
def more(_id, category, skip, limit, subParam):
  return jsonify(getMore(_id, category, skip, limit, subParam))

@app.route("/analyze/<int:_id1>/<int:_id2>")
@cache.cached()
def cross_analyze(_id1, _id2):
  return jsonify(getCrossTopicsAnalyze(_id1, _id2))

@app.route("/hint/<entity>")
@cache.cached()
def hint(entity):
  return jsonify(getTopicByEntity(entity))

if __name__ == '__main__':
  # cache.clear()
  app.run(host='0.0.0.0', port=5000)