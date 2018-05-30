from flask import Flask, jsonify
from lib import * 
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello():
  return "Hello World!"

@app.route("/analyze/<int:_id>")
def analyze(_id):
  return jsonify(getTopicAnalyze(_id, 5))

@app.route("/analyze/more/<int:_id>/<category>/<int:skip>/<int:limit>/<int:subParam>")
def more(_id, category, skip, limit, subParam):
  return jsonify(getMore(_id, category, skip, limit, subParam))

@app.route("/analyze/<int:_id1>/<int:_id2>")
def cross_analyze(_id1, _id2):
  return jsonify(getCrossTopicsAnalyze(_id1, _id2))

@app.route("/hint/<entity>")
def hint(entity):
  return jsonify(getTopicByEntity(entity))

if __name__ == '__main__':
  app.run(port=5000)