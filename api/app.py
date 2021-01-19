from es_repository import ES_Repository, News, NewsTest
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from fse.models import SIF
import math
import logging
import time
import numpy as np
from configparser import ConfigParser
from sql import News_Fields, GetAllNews, GetAllCategories, GetNewsByCategoryId
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
sif_model = 'data/word2vec/models/fse/corpus-title-100d.500ksample.model'.format(100)
if "sample" in sif_model:
    index = type(NewsTest()).__name__.lower()
else:
    index = type(News()).__name__.lower()
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
@app.route('/api/v1/news/index', methods=['POST'])
def news_index():
    body = request.get_json()
    title = preprocess(body['title'])
    abstract = preprocess(body['abstract'])
    title_embedding = np.array(SentenceInference(title[0])).tolist()
    abstract_embedding = np.array(AbstractInference(abstract)).tolist()
    body['title_embedding'] = title_embedding
    body['abstract_embedding'] = abstract_embedding
    response = ES.Index(index_name=index,body=body,id=id)
    return jsonify(response)
@app.route('/api/v1/news/delete', methods=['DELETE'])
def news_delete():
    id = request.args.get('id')
    response = ES.Delete(index_name=index, id=id)
    return jsonify(response)

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
    if isTitle != '':
        isTitle = True if int(isTitle) == 1 else False
    else:
        isTitle = None
    if sentence != None and sentence != '':
        tokenized = preprocess(sentence)[0]
        vector = np.array(SentenceInference(tokenized)).tolist()
    else:
        vector = None
    if EMERGE_DEBUG:
        print(vector)
    global index
    response = ES.News_STS_Search(index, vector, size, newscategoryid, isTitle)
    if response == None:
        return jsonify(None)
    else:
        response = response['hits']['hits']
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
    global index
    for i, news in enumerate(data):
        title = preprocess(news[News_Fields.Title.value])
        abstract = preprocess(news[News_Fields.Abstract.value])
        title_embedding = np.array(SentenceInference(title[0])).tolist()
        abstract_embedding = np.array(AbstractInference(abstract)).tolist()
        body.append({
            "index":{
                "_index": index,
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

# TESTING
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

app.run(host=host, port=port,use_reloader=False)