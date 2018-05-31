from pymongo import MongoClient
import numpy as np
from utils import ranker, ranki
from nltk import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
import json
ps = PorterStemmer()
lmtzr = WordNetLemmatizer()
mongo_config = json.load(open('config.json'))['mongo']
client = MongoClient(mongo_config['host'], port=mongo_config['port'], username=mongo_config['username'], password=mongo_config['password'], authSource=mongo_config['authSource'])
db = client['interdisciplinary']
year_gross = np.asarray(db.values.find_one({'_id': 'year_gross'})['data'], dtype=int)

topics = []
topic_tokens = []
entity_lookup = {}
topics = list(sorted(db.topics.find({}), key=lambda x: x['_id']))
for topic in topics:
  for entity in topic['entities']:
    entity_lookup[entity] = len(topic_tokens)
  topic_tokens.append(topic['token'])

def getTopicByEntity(_entity):
  trans = str(_entity).lower()
  if trans in entity_lookup:
    return topics[entity_lookup[trans]]
  _trans = ' '.join([lmtzr.lemmatize(part) for part in trans.split(' ')])
  if _trans in entity_lookup:
    return topics[entity_lookup[_trans]]
  _trans = ' '.join([ps.stem(part) for part in trans.split(' ')])
  if _trans in entity_lookup:
    return topics[entity_lookup[_trans]]
  return None

# return (token, entities)
def getTopicById(_id):
  _ = db.topics.find_one({'_id': _id})
  return (_['token'], _['entities']) if _ else None

def getTrendById(_id):
  _ = db.trends.find_one({'_id': _id}, {'data': {'$slice': [_id, 1]}})
  return np.asarray(_['data'][0], dtype=int) if _ else None

def getData(_id, attr):
  return np.asarray(db[attr].find_one({'_id': _id})['data'], dtype=float)

def getTopicAnalyze(_id, topN = 25):
  te = getTopicById(_id)
  if not te:
    return None
  pmi, pcc, lf, tg = getData(_id, 'pmi'), getData(_id, 'pcc'), getData(_id, 'lf'), np.swapaxes(getData(_id, 'tg'), 0, 1)
  strength = np.abs(pmi * pcc)
  return {'token': te[0], 
          'entities': te[1],
          'trends': (getTrendById(_id) / year_gross).tolist(),
          'pmi': ranker(pmi, topic_tokens)[:topN],
          'pcc': ranker(pcc, topic_tokens)[:topN],
          'strength': ranker(strength, topic_tokens)[:topN],
          'lf': ranker(lf, topic_tokens)[:topN],
          'tg': list(map(lambda tgi: ranker(tgi, topic_tokens)[:topN], tg)),
          'lf_self': [lf[_id], ranki(lf, lf[_id])],
          'tg_self': list(map(lambda tgi: (tgi[_id], ranki(tgi, tgi[_id])), tg))
          }

def getCrossTrendByIds(_id1, _id2):
  _ = db.trends.find_one({'_id': _id1}, {'data': {'$slice': [_id2, 1]}})
  return np.asarray(_['data'][0], dtype=int) if _ else None

def getCrossTopicsAnalyze(_id1, _id2):
  te1 = getTopicById(_id1)
  te2 = getTopicById(_id2)
  pmi1, pmi2 = getData(_id1, 'pmi'), getData(_id2, 'pmi')
  pcc1, pcc2 = getData(_id1, 'pcc'), getData(_id2, 'pcc')
  strength1, strength2 = np.abs(pmi1 * pcc1), np.abs(pmi2 * pcc2)
  lf1, lf2 = getData(_id1, 'lf'), getData(_id2, 'lf')
  tg1, tg2 = getData(_id1, 'tg'), getData(_id2, 'tg')
  pmi, pcc, strength, lfi1, lfi2, tgi1, tgi2 = pmi1[_id2], pcc1[_id2], strength1[_id2], lf1[_id2], lf2[_id1], tg1[_id2], tg2[_id1]
  return {
    'token': [te1[0], te2[0]],
    'entities': [te1[1], te2[1]],
    'pmi': [pmi, ranki(pmi1, pmi), ranki(pmi2, pmi)],
    'pcc': [pcc, ranki(pcc1, pcc), ranki(pcc2, pcc)],
    'strength': [strength, ranki(strength1, strength), ranki(strength2, strength)],
    'lf': [lfi1, ranki(lf1, lfi1), lfi2, ranki(lf2, lfi2)],
    'tg': list(map(lambda year: (tgi1[year], ranki(tg1[:,year], tgi1[year]), tgi2[year], ranki(tg2[:,year], tgi2[year])), range(30)))
  }

def getMore(_id, category, skip, limit, subParam = None):
  te = getTopicById(_id)
  if not te:
    return None
  data = getData(_id, category)
  if category != 'tg':
    return ranker(data, topic_tokens)[skip:skip+limit]
  else:
    data = data.swapaxes(0, 1)
    if subParam:
      return ranker(data[subParam], topic_tokens)[skip:skip+limit]
    else:
      return list(map(lambda d: ranker(d, topic_tokens)[skip:skip+limit], data))

