def _read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read().splitlines()
def _write_file(filename, sentences):
    with open(filename, 'w', encoding='utf-8') as f:
        for sent in sentences:
            f.write(sent)
            if sent != sentences[-1]:
                f.write('\n')

sents1_og = _read_file('data/vnPara/pairs_data/Sentences1.txt')
sents2_og = _read_file('data/vnPara/pairs_data/Sentences2.txt')

vncorenlp_file = r'VnCoreNLP-1.1.1.jar'

sents1_tok = []
sents2_tok = []
from vncorenlp import VnCoreNLP
with VnCoreNLP(vncorenlp_file) as vncorenlp:
    for i, sent in enumerate(sents1_og):
        segmented = []
        tokens = vncorenlp.tokenize(sent)
        for tok in tokens:
            segmented.extend(tok)
        sents1_tok.append(segmented)
    for i, sent in enumerate(sents2_og):
        segmented = []
        tokens = vncorenlp.tokenize(sent)
        for tok in tokens:
            segmented.extend(tok)
        sents2_tok.append(segmented)

for i, sent in enumerate(sents1_tok):
    s = ' '.join(sent)
    sents1_tok[i] = s
for i, sent in enumerate(sents2_tok):
    s = ' '.join(sent)
    sents2_tok[i] = s

_write_file('data/vnPara/pairs_data/Sentences1.tok.txt', sents1_tok)
_write_file('data/vnPara/pairs_data/Sentences2.tok.txt', sents2_tok)

remove_dupe_set = []
remove_dupe_set.extend(sents1_tok)
remove_dupe_set.extend(sents2_tok)

remove_dupe_set = list(dict.fromkeys(remove_dupe_set))
_write_file('data/vnPara/pairs_data/removed_dupe.tok.txt', remove_dupe_set)