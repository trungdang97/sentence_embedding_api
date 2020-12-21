from json import JSONEncoder
import json
import numpy as np
import math

class ModelSimilarity:
    label = None
    doc2vec_based = None
    sif_based = None
    sif_pretrained = None
    sif_fine_tuning = None

    def __init__(self, data):
        self.__dict__ = data
    def __getitem__(self, modelname):
        return self.__dict__[modelname]
    def __setitem__(self, modelname, data):
        self.__dict__[modelname] = data


dim = 300
css_threshold = 0.7

json_data = None
with open('results/evaluation_{0}d.json'.format(dim), 'r', encoding='utf-8') as f:
    json_data = json.loads(f.read())

if json_data is None or json_data == '':
    raise('Evaluation file empty')
    exit()

evaluations = []
for data in json_data:
    evaluations.append(ModelSimilarity(data))

results = []

class Result:
    label = None
    doc2vec_based = None
    sif_based = None
    sif_pretrained = None
    sif_fine_tuning = None

class RatingResult:
    def __init__(self):
        self.doc2vec_based = {
            'true_positive': 0, 'false_positive': 0, 'true_negative': 0, 'false_negative': 0}
        self.sif_based = {'true_positive': 0, 'false_positive': 0,
                          'true_negative': 0, 'false_negative': 0}
        self.sif_pretrained = {
            'true_positive': 0, 'false_positive': 0, 'true_negative': 0, 'false_negative': 0}
        self.sif_fine_tuning = {
            'true_positive': 0, 'false_positive': 0, 'true_negative': 0, 'false_negative': 0}

    def __getitem__(self, modelname):
        return self.__dict__[modelname]

    def __setitem__(self, modelname, data):
        self.__dict__[modelname] = data


for pair in evaluations:
    result = Result()
    result.label = pair.label

    result.doc2vec_based = 1 if pair.doc2vec_based['cs_sim'] >= css_threshold else 0
    result.sif_based = 1 if pair.sif_based['cs_sim'] >= css_threshold else 0
    result.sif_pretrained = 1 if pair.sif_pretrained['cs_sim'] >= css_threshold else 0
    result.sif_fine_tuning = 1 if pair.sif_fine_tuning['cs_sim'] >= css_threshold else 0

    results.append(result)

json_string = json.dumps([obj.__dict__ for obj in results])
with open('results/classification_{0}d.json'.format(dim), 'w', encoding='utf-8') as f:
    f.write(json_string)

rating = RatingResult()
for result in results:
    if result.doc2vec_based == result.label:
        if result.label == 1:
            rating.doc2vec_based['true_positive'] += 1
        else:
            rating.doc2vec_based['true_negative'] += 1
    else:
        if result.label == 0:
            rating.doc2vec_based['false_positive'] += 1
        else:
            rating.doc2vec_based['false_negative'] += 1

    if result.sif_based == result.label:
        if result.label == 1:
            rating.sif_based['true_positive'] += 1
        else:
            rating.sif_based['true_negative'] += 1
    else:
        if result.label == 0:
            rating.sif_based['false_positive'] += 1
        else:
            rating.sif_based['false_negative'] += 1

    if result.sif_pretrained == result.label:
        if result.label == 1:
            rating.sif_pretrained['true_positive'] += 1
        else:
            rating.sif_pretrained['true_negative'] += 1
    else:
        if result.label == 0:
            rating.sif_pretrained['false_positive'] += 1
        else:
            rating.sif_pretrained['false_negative'] += 1

    if result.sif_fine_tuning == result.label:
        if result.label == 1:
            rating.sif_fine_tuning['true_positive'] += 1
        else:
            rating.sif_fine_tuning['true_negative'] += 1
    else:
        if result.label == 0:
            rating.sif_fine_tuning['false_positive'] += 1
        else:
            rating.sif_fine_tuning['false_negative'] += 1

json_string = json.dumps(rating.__dict__)
with open('results/ratings_{0}d.json'.format(dim), 'w', encoding='utf-8') as f:
    f.write(json_string)

# precision, recall, f1
class Scoring:
    def __init__(self, TP, TN, FP, FN):
        self.precision = TP / (TP + TN)
        self.recall = TP / (TP + FN)
        self.f1_score = 2 * self.precision * \
            self.recall / (self.precision + self.recall)
        self.accuracy = (TP + TN) / (TP+TN+FP+FN)
        self.pearson = None
for model in rating.__dict__:
    TP = rating[model]['true_positive']
    TN = rating[model]['true_negative']
    FP = rating[model]['false_positive']
    FN = rating[model]['false_negative']
    rating[model] = Scoring(TP, TN, FP, FN)

# pearson
class PearsonCorrelationCoeff:
    def __call__(self, labels, predictions):
        self.labels = labels
        self.predictions = predictions
        self.labels_mean = np.mean(labels)
        self.predictions_mean = np.mean(predictions)
        return self.PearsonNominator()/self.PearsonDenominator()

    def PearsonNominator(self):
        sigma = 0
        for i, label in enumerate(self.labels):
            sigma += (self.labels[i]-self.labels_mean) * \
                (self.predictions[i]-self.predictions_mean)
        return sigma

    def PearsonDenominator(self):
        label_sigma = 0
        prediction_sigma = 0
        for i, label in enumerate(self.labels):
            label_sigma += (self.labels[i]-self.labels_mean)**2
            prediction_sigma += (self.predictions[i]-self.predictions_mean)**2
        return math.sqrt(label_sigma)*math.sqrt(prediction_sigma)

labels = []
predictions = {}
pearson = PearsonCorrelationCoeff()
for model in evaluations[0].__dict__:
    if model != 'label':
        predictions[model] = []

for pair in evaluations:
    labels.append(pair.label)
    for model in predictions:
        predictions[model].append(pair[model]['cs_sim'])

for model in rating.__dict__:
    rating[model].pearson = pearson(labels, predictions[model])

class Encoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

with open('results/scores_{0}d.json'.format(dim), 'w', encoding='utf-8') as f:
    json_string = Encoder().encode(rating)    
    f.write(json_string)

print("Done evaluation")