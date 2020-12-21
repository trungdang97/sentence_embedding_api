import multiprocessing
from vncorenlp import VnCoreNLP
from gensim.models.word2vec import Word2Vec
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from fse.models import SIF
from fse import IndexedList
import subprocess

import logging
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
model_dir = 'data/vnPara/models/'
corpus_file = 'data/vnPara/pairs_data/removed_dupe.tok.txt'
train_data = []

with open(corpus_file, 'r', encoding='utf-8') as f:
    for line in f.read().splitlines():
        tokens = line.lower().split()
        train_data.append(tokens)

dim = 300

w2v_model = Word2Vec(sg=0, workers=multiprocessing.cpu_count(), negative=5, size=dim, min_count=1)
w2v_model.build_vocab(train_data, update=False)
w2v_model.train(sentences=train_data,
                total_examples=len(train_data), epochs=10)
w2v_model.save(model_dir + 'w2v_based_{0}d.model'.format(dim))

d2v_model = Doc2Vec(dm=1, workers=multiprocessing.cpu_count(), negative=5, size=dim)
tagged_docs = []
for i, sent in enumerate(train_data):
    tagged_docs.append(TaggedDocument(sent,[i]))
d2v_model.build_vocab(tagged_docs)
d2v_model.train(documents=tagged_docs, total_examples=len(tagged_docs), epochs=10)
d2v_model.save(model_dir + 'd2v_based_{0}d.model'.format(dim))
d2v_model = None

indexed_sents = IndexedList(train_data)

sif_direct = SIF(w2v_model, workers=multiprocessing.cpu_count())
sif_direct.train(indexed_sents)
sif_direct.save(model_dir + 'sif_based_{0}d.model'.format(dim))
sif_direct = None

w2v_pretrained = Word2Vec.load('data/word2vec/models/cbow/corpus-title-{0}d.model'.format(dim))
sif_pretrained = SIF(w2v_pretrained, workers=multiprocessing.cpu_count())
sif_pretrained.train(indexed_sents)
sif_pretrained.save(model_dir + 'sif_pretrained_{0}d.model'.format(dim))
sif_pretrained = None

w2v_pretrained.build_vocab(train_data, update=True)
w2v_pretrained.train(sentences=train_data,
                total_examples=len(train_data), epochs=10)
w2v_pretrained.save(model_dir + 'w2v_fine_tuning_{0}d.model'.format(dim))
sif_fine_tuning = SIF(w2v_pretrained, workers=multiprocessing.cpu_count())
sif_fine_tuning.train(indexed_sents)
sif_fine_tuning.save(model_dir + 'sif_fine_tuning_{0}d.model'.format(dim))
sif_fine_tuning = None

# phobert fine tuning: https://colab.research.google.com/drive/1qI6sN7DbMCitiUw68XpiS6KomJyCeLpx?usp=sharing