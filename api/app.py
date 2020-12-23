from data.elasticsearch.es_repository import ES_Repository, News
from flask import Flask, jsonify, request
from flask_cors import CORS
from fse.models import SIF
import logging
import numpy as np
from api.sql import GetAllNews, GetAllCategories
logging.basicConfig(format='%(asctime)s : %(threadName)s : %(levelname)s : %(message)s', level=logging.INFO)
ES = ES_Repository()
###########################################################################
sif_model = 'data/word2vec/models/fse/corpus-title-100d.model'.format(100)
sif = SIF.load(sif_model)
def SentenceInference(sentence):
    vector = sif.infer([(sentence, 0)])
    return vector[0]
###########################################################################
from vncorenlp import VnCoreNLP
vncorenlp_file = r'common/VnCoreNLP-1.1.1.jar'
vncorenlp = VnCoreNLP(vncorenlp_file, annotators="wseg", max_heap_size="-Xmx1g")

class Preprocessing:
    def tokenize(self, text):
        sentences = vncorenlp.tokenize(text)
        return sentences

    def lowercase(self, sentences):
        for i, sentence in enumerate(sentences):
            sentences[i] = [word.lower() for word in sentence]
        return sentences

    def __call__(self, text):
        sentences = self.tokenize(text)
        sentences = self.lowercase(sentences)
        return sentences

preprocess = Preprocessing()
###########################################################################
app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True
host = "192.168.1.100"
port = "5000"
def start():
    app.run(use_reloader=False)

# TEST METHOD GOES HERE
@app.route('/api/v1/newscategory', methods=['GET'])
def get_newscategory():
    cates = GetAllCategories()
    for i, cat in enumerate(cates):
        cates[i] = {'id':cat[0], 'name':cat[1]}
    return jsonify(cates)

@app.route('/api/v1/news/search/sts', methods=['GET'])
def news_sts_search():
    sentence = request.args.get('text')
    size = request.args.get('size')
    newscategoryid = request.args.get('newscategoryid')
    if sentence != None and sentence != '':
        tokenized = preprocess(sentence)[0]
        vector = np.array(SentenceInference(tokenized)).tolist()
    else:
        vector = None
    response = ES.News_STS_Search(vector, size, newscategoryid)['hits']['hits']
    for news in response:
        news['_source']['embedding'] = None
    return jsonify(response)

@app.route('/api/v1/news/sync', methods=['POST'])
def news_sync():
    if ES.IsNewsDataEqual(type(News()).__name__.lower()):
        return jsonify('Data is equal. Syncing is unecessary.')

    data = GetAllNews()
    body = []
    for i, news in enumerate(data):
        title = preprocess(news[1])
        embedding = np.array(SentenceInference(title[0])).tolist()
        # data[i] = News(id=news[0], title=news[1], body=news[2], newscategoryid=news[3], embedding=embedding)
        body.append({
            "index":{
                "_index": type(News()).__name__.lower(),
                "_id": news[0]
            }
        })
        body.append({
            "title": news[1],
            "body": news[2],
            "newscategoryid": news[3],
            "embedding": embedding
        })
    
    response = ES.BulkIndex(index_name=type(News()).__name__.lower(), body=body)
    response['items']=len(response['items'])
    return jsonify(response)

@app.route('/api/v1/news/quantity', methods=['GET'])
def data_quantities():
    quantities = ES.CheckNewsQuantities()
    result = {
        "SQL": quantities[0],
        "ES": quantities[1]
    }
    return jsonify(result)

# testing app
@app.route('/', methods=['GET'])
def ping():
    return jsonify('API is running')
