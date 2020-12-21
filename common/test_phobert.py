import torch
from transformers import AutoModel, PhobertTokenizer

device = 'cuda' if torch.cuda.is_available() else 'cpu'
phobert = AutoModel.from_pretrained("vinai/phobert-base", output_hidden_states=True)
tokenizer = PhobertTokenizer.from_pretrained("vinai/phobert-base")

# INPUT TEXT MUST BE ALREADY WORD-SEGMENTED!

sent1 = "Tôi là sinh_viên trường đại_học Công_nghệ .".lower()
sent2 = "Tôi là học_sinh tiểu_học Đại_yên .".lower()

# input_ids_1 = torch.tensor([tokenizer.encode(sent1)])
# print('input_ids_1_tokens', tokenizer.convert_ids_to_tokens(tokenizer.encode(sent1)))
# input_ids_2 = torch.tensor([tokenizer.encode(sent2)])
encodings = tokenizer([sent1, sent2], padding=True, truncation=True)
input_ids = torch.tensor(encodings['input_ids'])

phobert = phobert.to(device)
# input_ids_1 = input_ids_1.to(device)
# input_ids_2 = input_ids_2.to(device)
input_ids = input_ids.to(device)

phobert.eval()

with torch.no_grad():
    features = phobert(input_ids)

hidden_states = features[2]

cos = torch.nn.CosineSimilarity(dim=0, eps=1e-6)

sent_emb1 = torch.mean(hidden_states[-1][0], dim=0).squeeze()
sent_emb2 = torch.mean(hidden_states[-1][1], dim=0).squeeze()

similarity = cos(sent_emb1, sent_emb2)
print(similarity)