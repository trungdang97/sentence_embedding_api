from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import os
import multiprocessing
import logging


def ReadFile(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            yield TaggedDocument(line.lower().split(), [i])


class Corpus():
    def __init__(self, filename):
        self.filename = filename

    def __iter__(self):
        with open(self.filename, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                yield TaggedDocument(line.lower().split(), [i])


logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

filename = 'data/mongodb/txt/phapluat.tok.txt'

# fine-grained ranging from 300-1000 dimensions
vector_size = 100
# remove word that has appeared less than this (may be misunderstanding since this was a problem https://github.com/RaRe-Technologies/gensim/issues/346)
min_count = 5
# use PV-DM if equals 1, PV-DBOW otherwise
dm = 1
# windows
window = 5
# 10-20 epochs in published work
epochs = 10
# number of thread
workers = multiprocessing.cpu_count()

corpus = Corpus(filename)

model = Doc2Vec(dm=dm, vector_size=vector_size, window=window,
                min_count=min_count, workers=workers, epochs=epochs)
model.build_vocab(corpus)

model_name = 'phapluat.model'
model.train(corpus, total_examples=model.corpus_count, epochs=model.epochs)
if dm == 1:
    model.save('data/doc2vec/models/pv_dm/' + model_name)
else:
    model.save('data/doc2vec/models/pv_dbow/'+model_name)
