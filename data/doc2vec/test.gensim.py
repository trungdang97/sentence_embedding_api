from gensim.models.doc2vec import Doc2Vec
import requests
from sklearn.metrics.pairwise import cosine_similarity
import linecache
from vncorenlp import VnCoreNLP
# dm = 0 PV-DBOW, dm = 1 PV-DM
def loadModels(path):
    return Doc2Vec.load(path)
# def tokenize(text):
#     response = requests.get('http://localhost:8090/api/tokenize?text='+text).text.replace('[','').replace(']','').replace('"','')
#     #tokens = response.lower().split()
#     return response
def tokenize(text):
    with VnCoreNLP(address="http://localhost", port=9000) as vncorenlp:
        return vncorenlp.tokenize(text)[0]

model = loadModels('data/doc2vec/models/pv_dm/phapluat.model')
epochs = 10

sentence1 = "Ăn trộm tiền"
sentence2 = "Tài xế 'choáng váng' vì số tiền phạt 'nguội' bằng nửa giá trị chiếc xe"

vector1 = model.infer_vector(tokenize(sentence1), epochs=epochs)
vector2 = model.infer_vector(tokenize(sentence2), epochs=epochs)

# print(cosine_similarity([vector1],[vector2]))

print(model.docvecs.most_similar([vector2]))
# for sim in model.docvecs.most_similar([vector1]):
#     print(sim)