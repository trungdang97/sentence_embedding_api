from data.elasticsearch.es_repository import ES_Repository, News
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from fse.models import SIF
import math
import logging
import time
import numpy as np
from configparser import ConfigParser
from api.sql import News_Fields, GetAllNews, GetAllCategories, GetNewsByCategoryId
logger = logging.getLogger()
logging.basicConfig(format='%(asctime)s : %(threadName)s : %(levelname)s : %(message)s', level=logging.WARNING)
# logging.getLogger("SIF").setLevel(logging.WARNING)
import threading
SYNC_LOCK = threading.Lock()

config = ConfigParser()
config.read('config.ini')
ES = ES_Repository()

EMERGE_DEBUG = True if int(config.get("emerge","debug"))==1 else False
###########################################################################
sif_model = 'data/word2vec/models/fse/corpus-title-100d.model'.format(100)
sif = SIF.load(sif_model)
def SentenceInference(sentence):
    vector = sif.infer([(sentence, 0)])
    return vector[0]
def AbstractInference(sentences):
    for i, sent in enumerate(sentences):
        sentences[i] = (sent, i)
    vectors = sif.infer(sentences)
    return np.mean(vectors, axis=0)
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
    app.run(host=host, port=port,use_reloader=False)

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
    isTitle = request.args.get('isTitle')
    isTitle = True if int(isTitle) == 1 else False
    if sentence != None and sentence != '':
        tokenized = preprocess(sentence)[0]
        vector = np.array(SentenceInference(tokenized)).tolist()
    else:
        vector = None
    if EMERGE_DEBUG:
        print(vector)
    response = ES.News_STS_Search(vector, size, 
                newscategoryid, isTitle)['hits']['hits']
    print('')
    for news in response:
        news['_source']['title_embedding'] = None
        news['_source']['abstract_embedding'] = None
    return jsonify(response)

@app.route('/api/v1/news/sync', methods=['POST'])
def news_sync():
    forced = False if request.args.get('forced') == '' else False

    if ES.IsNewsDataEqual() and not forced:
        return jsonify('Data is equal. Syncing is unecessary.')

    global SYNC_LOCK
    if not SYNC_LOCK.acquire(False):
        return jsonify("Syncing in progress.")
    
    batch = int(config.get("elasticsearch", "bulk_batch"))
    data = GetAllNews()
    print("Syncing {0} batch(es) of {1} at maximum".format(math.ceil(len(data)/batch), batch))
    body = []
    start_time = time.time()
    for i, news in enumerate(data):
        title = preprocess(news[News_Fields.Title.value])
        abstract = preprocess(news[News_Fields.Abstract.value])
        title_embedding = np.array(SentenceInference(title[0])).tolist()
        abstract_embedding = np.array(AbstractInference(abstract)).tolist()
        body.append({
            "index":{
                "_index": type(News()).__name__.lower(),
                "_id": news[News_Fields.NewsId.value]
            }
        })
        body.append({
            "title": news[News_Fields.Title.value],
            "abstract": news[News_Fields.Abstract.value],
            "body": news[News_Fields.Body.value],
            "newscategoryid": news[News_Fields.NewsCategoryId.value],
            "title_embedding": title_embedding,
            "abstract_embedding": abstract_embedding
        })
        if (i+1) % batch == 0:
            response = ES.BulkIndex(index_name=type(News()).__name__.lower(), body=body)
            body = []
            end_time = time.time()
            print('Done batch {0} in {1} seconds'.format(math.ceil((i+1)/batch), end_time-start_time))
            start_time = time.time()
    if len(body) > 0:
        response = ES.BulkIndex(index_name=type(News()).__name__.lower(), body=body)
        end_time = time.time()
        print('Done batch {0} in {1} seconds'.format(math.ceil((i+1)/batch), end_time-start_time))
    response['items']=len(response['items'])
    SYNC_LOCK.release()
    return jsonify("Finish syncing")

@app.route('/api/v1/news/quantity', methods=['GET'])
def data_quantities():
    quantities = ES.CheckNewsQuantities("news")
    result = {
        "SQL": quantities[0],
        "ES": quantities[1]
    }
    return jsonify(result)

# testing
@app.route('/', methods=['GET'])
def ping():
    return app.send_static_file('api/interface.html')

@app.route('/fix_failed_docs', methods=['GET'])
def fix_failed_docs():
    # if ES.IsNewsDataEqual(type(News()).__name__.lower()):
    #     return jsonify('Data is equal. Syncing is unecessary.')

    # global SYNC_LOCK
    # if not SYNC_LOCK.acquire(False):
    #     return jsonify("Syncing in progress.")
    
    batch = int(config.get("elasticsearch", "bulk_batch"))
    data = GetNewsByCategoryId(id='EF4BCA17-630E-4760-8C6B-2E6C5BDEA8AB')
    print("Syncing {0} batch(es) of {1} at maximum".format(math.ceil(len(data)/batch), batch))
    body = []
    start_time = time.time()
    for i, news in enumerate(data):
        title = preprocess(news[News_Fields.Title.value])
        abstract = preprocess(news[News_Fields.Abstract.value])
        title_embedding = np.array(SentenceInference(title[0])).tolist()
        abstract_embedding = np.array(AbstractInference(abstract)).tolist()
        body.append({
            "index":{
                "_index": type(News()).__name__.lower(),
                "_id": news[News_Fields.NewsId.value]
            }
        })
        body.append({
            "title": news[News_Fields.Title.value],
            "abstract": news[News_Fields.Abstract.value],
            "body": news[News_Fields.Body.value],
            "newscategoryid": news[News_Fields.NewsCategoryId.value],
            "title_embedding": title_embedding,
            "abstract_embedding": abstract_embedding
        })
        if (i+1) % batch == 0:
            response = ES.BulkIndex(index_name=type(News()).__name__.lower(), body=body)
            body = []
            end_time = time.time()
            print('Done batch {0} in {1} seconds'.format(math.ceil((i+1)/batch), end_time-start_time))
            start_time = time.time()
    if len(body) > 0:
        response = ES.BulkIndex(index_name=type(News()).__name__.lower(), body=body)
        end_time = time.time()
        print('Done batch {0} in {1} seconds'.format(math.ceil((i+1)/batch), end_time-start_time))
    response['items']=len(response['items'])
    # SYNC_LOCK.release()
    return jsonify("Finish syncing")