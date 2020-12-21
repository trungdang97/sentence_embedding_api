import torch
import json
import time
from vnpara import VnPara

from gensim.models.doc2vec import Doc2Vec
from fse.models import SIF

vnPara = VnPara()
Cosine_Similarity = torch.nn.CosineSimilarity(dim=0, eps=1e-6)

class ModelSimilarity:
    def __init__(self, label):
        self.label = label
        self.doc2vec_based = None
        self.sif_based = None
        self.sif_pretrained = None
        self.sif_fine_tuning = None

evaluations = []
for pair in vnPara.pairs:
    evaluations.append(ModelSimilarity(pair.is_paraphrase))

print('Start testing similarity...')

dim = 300
model_dim = str(dim)+'d'

# doc2vec based (built dependently on vnPara) evaluation
start_time = time.time()
d2v_based = Doc2Vec.load('data/vnPara/models/d2v_based_{0}.model'.format(model_dim))
for i, pair in enumerate(vnPara.pairs):
    vector1 = d2v_based.infer_vector(pair.sentence1, epochs=20)
    vector2 = d2v_based.infer_vector(pair.sentence2, epochs=20)
    cs_sim = Cosine_Similarity(torch.tensor(vector1), torch.tensor(vector2)).item()
    evaluations[i].doc2vec_based = {'cs_sim': cs_sim}
d2v_based = None
end_time = time.time()
print('Doc2Vec based took: {0} seconds'.format(end_time-start_time))

# SIF based (w2v model built dependently on vnPara)
start_time = time.time()
sif_based = SIF.load('data/vnPara/models/sif_based_{0}.model'.format(model_dim))
for i, pair in enumerate(vnPara.pairs):
    vector1 = sif_based.infer([(pair.sentence1, 0)])[0]
    vector2 = sif_based.infer([(pair.sentence2, 0)])[0]
    cs_sim = Cosine_Similarity(torch.tensor(vector1), torch.tensor(vector2)).item()
    evaluations[i].sif_based = {'cs_sim': cs_sim}
sif_based = None
end_time = time.time()
print('SIF based took: {0} seconds'.format(end_time-start_time))

# SIF pretrained (w2v model built independently on vnPara)
start_time = time.time()
sif_pretrained = SIF.load('data/vnPara/models/sif_pretrained_{0}.model'.format(model_dim))
for i, pair in enumerate(vnPara.pairs):
    vector1 = sif_pretrained.infer([(pair.sentence1, 0)])[0]
    vector2 = sif_pretrained.infer([(pair.sentence2, 0)])[0]
    cs_sim = Cosine_Similarity(torch.tensor(vector1), torch.tensor(vector2)).item()
    evaluations[i].sif_pretrained = {'cs_sim': cs_sim}
sif_pretrained = None
end_time = time.time()
print('SIF pretrained took: {0} seconds'.format(end_time-start_time))

# SIF fine tuning (w2v model updated with vnPara)
start_time = time.time()
sif_fine_tuning = SIF.load('data/vnPara/models/sif_fine_tuning_{0}.model'.format(model_dim))
for i, pair in enumerate(vnPara.pairs):
    vector1 = sif_fine_tuning.infer([(pair.sentence1, 0)])[0]
    vector2 = sif_fine_tuning.infer([(pair.sentence2, 0)])[0]
    cs_sim = Cosine_Similarity(torch.tensor(vector1), torch.tensor(vector2)).item()
    evaluations[i].sif_fine_tuning = {'cs_sim': cs_sim}
sif_fine_tuning = None
end_time = time.time()
print('SIF fine tuning took: {0} seconds'.format(end_time-start_time))

######################################## RESULTS
json_string = json.dumps([obj.__dict__ for obj in evaluations])

with open('results/evaluation_{0}.json'.format(model_dim),'w',encoding='utf-8') as f:
    f.write(json_string)