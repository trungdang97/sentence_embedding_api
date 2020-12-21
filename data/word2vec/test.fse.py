from fse.models import SIF
from fse import IndexedList
from sys import getsizeof
# def ReadFile(filename):
#     f = open(filename, 'r', encoding='utf-8')
#     sentences = [s.split() for s in f.readlines()]
#     return sentences

# filename = 'data/corpus-title.tok.txt'
# sentences = IndexedList(ReadFile(filename))

model = SIF.load('data/word2vec/models/fse/corpus-title-100d.model')

print(getsizeof(model))

sent = ['cháy', 'nhà', 'trên', 'phố', 'cổ']
vector = model.infer([(sent, 0)])