from json import JSONEncoder
import json
import numpy as np
import math

class ModelSimilarity:
    phobert_base = None
    phobert_fine_tuning = None

    def __init__(self, data):
        self.__dict__ = data
    def __getitem__(self, modelname):
        return self.__dict__[modelname]
    def __setitem__(self, modelname, data):
        self.__dict__[modelname] = data

css_threshold = 0.6

json_data = None
with open('results/evaluation_phobert.json', 'r', encoding='utf-8') as f:
    json_data = json.loads(f.read())

if json_data is None or json_data == '':
    raise('Evaluation file empty')
    exit()

evaluations = []
for data in json_data:
    evaluations.append(ModelSimilarity(data))

results = []

class Result:
    phobert_base = None
    phobert_fine_tuning = None

class RatingResult:
    def __init__(self):
        self.phobert_base = {
            'true_positive': 0, 'false_positive': 0, 'true_negative': 0, 'false_negative': 0}
        self.phobert_fine_tuning = {
            'true_positive': 0, 'false_positive': 0, 'true_negative': 0, 'false_negative': 0}

    def __getitem__(self, modelname):
        return self.__dict__[modelname]

    def __setitem__(self, modelname, data):
        self.__dict__[modelname] = data


for pair in evaluations:
    result = Result()
    result.label = pair.label

    result.phobert_base = 1 if pair.phobert_base['cs_sim'] >= css_threshold else 0
    result.phobert_fine_tuning = 1 if pair.phobert_base['cs_sim'] >= css_threshold else 0

    results.append(result)

json_string = json.dumps([obj.__dict__ for obj in results])
with open('results/classification_phobert.json', 'w', encoding='utf-8') as f:
    f.write(json_string)

rating = RatingResult()
for result in results:
    if result.phobert_base == result.label:
        if result.label == 1:
            rating.phobert_base['true_positive'] += 1
        else:
            rating.phobert_base['true_negative'] += 1
    else:
        if result.label == 0:
            rating.phobert_base['false_positive'] += 1
        else:
            rating.phobert_base['false_negative'] += 1

    if result.phobert_fine_tuning == result.label:
        if result.label == 1:
            rating.phobert_fine_tuning['true_positive'] += 1
        else:
            rating.phobert_fine_tuning['true_negative'] += 1
    else:
        if result.label == 0:
            rating.phobert_fine_tuning['false_positive'] += 1
        else:
            rating.phobert_fine_tuning['false_negative'] += 1

json_string = json.dumps(rating.__dict__)
with open('results/ratings_phobert.json', 'w', encoding='utf-8') as f:
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

with open('results/scores_phobert.json', 'w', encoding='utf-8') as f:
    json_string = Encoder().encode(rating)    
    f.write(json_string)