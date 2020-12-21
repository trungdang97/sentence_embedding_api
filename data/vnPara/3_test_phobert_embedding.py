import torch
import json
import time
from vnpara import VnPara

vnPara = VnPara()
Cosine_Similarity = torch.nn.CosineSimilarity(dim=0, eps=1e-6)

class ModelSimilarity:
    def __init__(self, label):
        self.label = label
        self.phobert_base = None
        self.phobert_fine_tuning = None

evaluations = []
for pair in vnPara.pairs:
    evaluations.append(ModelSimilarity(pair.is_paraphrase))

print('Start evaluating...')
# PhoBERT base

from transformers import AutoModel, PhobertTokenizer
device = 'cuda' if torch.cuda.is_available() else 'cpu'

start_time = time.time()
phobert_base = AutoModel.from_pretrained("vinai/phobert-base", output_hidden_states=True)
tokenizer = PhobertTokenizer.from_pretrained("vinai/phobert-base")
phobert_base.to(device)
phobert_base.eval()
with torch.no_grad():
    for i, pair in enumerate(vnPara.pairs):
        encodings = tokenizer([' '.join(pair.sentence1), ' '.join(pair.sentence2)], padding=True, truncation=True)
        input_ids = torch.tensor(encodings['input_ids']).to(device)
        hidden_states = phobert_base(input_ids)['hidden_states']
        last_4_layers = [hidden_states[i] for i in (-1, -2, -3, -4)]
        sum_l4_layers = torch.stack(last_4_layers).mean(dim=0)
        sent_emb1 = torch.mean(hidden_states[-1][0], dim=0).squeeze()
        sent_emb2 = torch.mean(hidden_states[-1][1], dim=0).squeeze()
        cs_sim = Cosine_Similarity(sent_emb1, sent_emb2).item()
        evaluations[i].phobert_base = {'cs_sim': cs_sim}
end_time = time.time()
phobert_base = None
print('PhoBERT base took: {0} seconds'.format(end_time-start_time))

# PhoBERT fine tuning
start_time = time.time()
phobert_fine_tuning = AutoModel.from_pretrained("data/vnPara/phobert_fine_tuning", output_hidden_states=True)
# tokenizer = PhobertTokenizer.from_pretrained("vinai/phobert-base")
phobert_fine_tuning.to(device)
phobert_fine_tuning.eval()
with torch.no_grad():
    for i, pair in enumerate(vnPara.pairs):
        encodings = tokenizer([' '.join(pair.sentence1), ' '.join(pair.sentence2)], padding=True, truncation=True)
        input_ids = torch.tensor(encodings['input_ids']).to(device)
        hidden_states = phobert_fine_tuning(input_ids)['hidden_states']
        last_4_layers = [hidden_states[i] for i in (-1, -2, -3, -4)]
        sum_l4_layers = torch.stack(last_4_layers).mean(dim=0)
        sent_emb1 = torch.mean(hidden_states[-1][0], dim=0).squeeze()
        sent_emb2 = torch.mean(hidden_states[-1][1], dim=0).squeeze()
        cs_sim = Cosine_Similarity(sent_emb1, sent_emb2).item()
        evaluations[i].phobert_fine_tuning = {'cs_sim': cs_sim}
end_time = time.time()
phobert_fine_tuning = None
print('PhoBERT fine-tuning took: {0} seconds'.format(end_time-start_time))
######################################## RESULTS
json_string = json.dumps([obj.__dict__ for obj in evaluations])

with open('results/evaluation_phobert.json','w',encoding='utf-8') as f:
    f.write(json_string)