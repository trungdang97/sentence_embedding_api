from gensim.models import Word2Vec
from fse.models import SIF
from fse import IndexedList
import multiprocessing
import logging
import random

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
# class Corpus():
#     def __init__(self, filename):
#         self.filename = filename
#     def __iter__(self):
#         for line in open(filename,'r',encoding='utf-8'):
#             yield line.lower().split()
def ReadFile(filename):
    f = open(filename, 'r', encoding='utf-8')
    sentences = [s.split() for s in f.readlines()]
    
    random.shuffle(sentences)
    sentences = sentences[0:2000000]

    return sentences

filename = 'data/corpus-title.tok.txt'

fse_path = 'data/word2vec/models/fse/'
w2v_path = 'data/word2vec/models/'
sg = 0
if sg == 0:
    w2v_path = w2v_path + 'cbow/'
else:
    w2v_path = w2v_path + 'skipgram/'

dim = 300

w2v_path = w2v_path + 'corpus-title-{0}d.model'.format(dim)
word2vec = Word2Vec.load(w2v_path)

fse = SIF(word2vec, workers=multiprocessing.cpu_count())

sentences = IndexedList(ReadFile(filename))
fse.train(sentences)
fse.save(fse_path + 'corpus-title-{0}d.model'.format(dim))