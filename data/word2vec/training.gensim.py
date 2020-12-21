from gensim.models.word2vec import Word2Vec
import os
import multiprocessing
import logging

def ReadFile(filename):
    for line in open(filename,'r',encoding='utf-8'):
        yield line.lower().split()
class Corpus():
    def __init__(self, filename):
        self.filename = filename
    def __iter__(self):
        for line in open(filename,'r',encoding='utf-8'):
            yield line.lower().split()
    

filename = 'data/corpus-title.tok.txt'

# fine-grained ranging from 300-1000 dimensions
vector_size = 300
# remove word that has appeared less than this (may be misunderstanding since this was a problem https://github.com/RaRe-Technologies/gensim/issues/346)
min_count = 1
# use skipgram if equals 1, cbow otherwise
sg = 0
# windows
window = 5
# 10-20 epochs in published work
epochs = 10
# number of thread
workers = multiprocessing.cpu_count()
# using negative sampling
ns = 10
# using hierarchical softmax (not as good as negative sampling)
hs = 0

model = {}

corpus = Corpus(filename)

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
try:
    model = Word2Vec.load('corpus-title-{0}d.model'.format(vector_size))
    #model.build_vocab(corpus, update=True, progress_per=1000000)
except IOError:
    model = Word2Vec(sg=sg, size=vector_size, window=window, min_count=min_count, workers=workers, batch_words=10000, negative=ns, hs=hs)
    model.build_vocab(corpus, update=False, progress_per=1000000)
model.train(corpus, total_examples=model.corpus_count, total_words=model.corpus_total_words, epochs=epochs)
if sg == 0:
    model.save('data/word2vec/models/cbow/corpus-title-{0}d.model'.format(vector_size))
else:
    model.save('data/word2vec/models/skipgram/corpus-title-{0}d.model'.format(vector_size))