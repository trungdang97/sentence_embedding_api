import os
import sys

class SentencePair:
    def __init__(self, sentence1, sentence2, is_paraphrase):
        self.sentence1 = sentence1
        self.sentence2 = sentence2
        self.is_paraphrase = is_paraphrase

class VnPara:
    def _read_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            if '.tok.' in filename:              
                sentences = f.read().splitlines()
                for i,s in enumerate(sentences):
                    sentences[i] = s.lower().split()
                return sentences
            else:
                return f.read().splitlines()

    def __init__(self):
        self.pairs = []
        self.positive_pairs = 0
        sents1 = self._read_file('data/vnPara/pairs_data/Sentences1.tok.txt')
        sents2 = self._read_file('data/vnPara/pairs_data/Sentences2.tok.txt')
        labels = list(map(int, self._read_file('data/vnPara/pairs_data/Labels.txt')))
        if len(sents1) != len(sents2) != len(labels):
            raise Exception("Inputs doesn't have enough sentences/label to form pairs. Please check VnPara files.")
            return
        for i in range(len(labels)):
            if labels[i] == 1:
                self.positive_pairs += 1
            self.pairs.append(SentencePair(sents1[i],sents2[i],labels[i]))
        self.negative_pairs = len(self.pairs) - self.positive_pairs