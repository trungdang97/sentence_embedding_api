from gensim.models.word2vec import Word2Vec, Word2VecKeyedVectors
import requests
from sklearn.metrics.pairwise import cosine_similarity
import linecache
from vncorenlp import VnCoreNLP

def loadModels(path):
    return Word2Vec.load(path)
def tokenize(text, vncorenlp):
    # response = requests.get('http://localhost:9000/api/tokenize?text='+text).text.replace('[','').replace(']','').replace('"','')
    #tokens = response.lower().split()
    tokens = vncorenlp.tokenize(text)[0][0]
    return tokens
    

vncorenlp = VnCoreNLP(address="http://localhost", port=9000)

model = loadModels('data/word2vec/models/cbow/corpus-title.model')
epochs = 100

words = "tổng thống"
wv = model[tokenize(words, vncorenlp)]
#wv = model["tổng_thống"]
print(model.wv.most_similar([wv]))