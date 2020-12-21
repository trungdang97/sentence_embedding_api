import torch
import random
import time
import transformers.utils.logging as transformers_logging
from transformers import AutoModel, AutoTokenizer, PhobertTokenizer, AdamW, TrainingArguments, Trainer
from torch.utils.data import Dataset, DataLoader, TensorDataset, SequentialSampler
import logging
transformers_logging.set_verbosity_info()
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
model_dir = 'data/vnPara/'
corpus_file = 'data/vnPara/pairs_data/removed_dupe.tok.txt'
train_data = []
with open(corpus_file, 'r', encoding='utf-8') as f:
    train_data = f.read().splitlines()
    for i, data in enumerate(train_data):
        train_data[i] = data.lower()


class VnParaDataset(Dataset):
    def __init__(self, encodings):
        self.encodings = encodings

    def __len__(self):
        return len(self.encodings)

    def __getitem__(self, index):
        item = {key: torch.tensor(val[index])
                for key, val in self.encodings.items()}
        return item

# recommend to run this on Google Colab
device = 'cuda' if torch.cuda.is_available() else 'cpu'
phobert = AutoModel.from_pretrained("vinai/phobert-base")
tokenizer = PhobertTokenizer.from_pretrained("vinai/phobert-base")
phobert = phobert.to(device)
phobert.train()

epochs = 10
optimizer = AdamW(phobert.parameters(), lr=1e-5)

train_encodings = tokenizer(train_data, padding=True, truncation=True)
train_inputs_ids = torch.tensor(train_encodings['input_ids'])
train_attention_mask = torch.tensor(train_encodings['attention_mask'])
train_dataset = TensorDataset(train_inputs_ids, train_attention_mask)
train_sampler = SequentialSampler(train_dataset)

# train_dataset = VnParaDataset(train_encodings)
train_loader = DataLoader(train_dataset, sampler=train_sampler, batch_size=32)

for epoch in range(epochs):
    count = 0
    for batch in train_loader:
        start = time.time()
        optimizer.zero_grad()
        # input_ids = batch['input_ids'].to(device)
        # attention_mask = batch['attention_mask'].to(device)
        input_ids = batch[0].to(device)
        attention_mask = batch[1].to(device)
        outputs = phobert(
            input_ids, attention_mask=attention_mask, token_type_ids=None)
        loss = outputs[0]
        loss.mean().backward()
        optimizer.step()
        count += 1
        end = time.time()
        print('Epoch {0} - Batch {1} in {2} seconds'.format(epoch+1, count, end-start))
phobert.eval()
phobert.save_pretrained('data/vnPara/phobert_fine_tuning')
