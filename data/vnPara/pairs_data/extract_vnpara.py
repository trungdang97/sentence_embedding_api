# unused, no end-to-end training, all methods used are unsupervised (check http://ixa2.si.ehu.eus/stswiki/index.php/STSbenchmark#Results for more infomation)
# we used Doc2Vec (Le and Mikolov et al 14) and SIF (Arora et al 17) as stated in the table above
# which mean we doesn't need to split the dataset, either use pretrained models, train from scratch or fine-tune pretrained models

from sklearn.model_selection import train_test_split

files = ["data/vnPara/Sentences1.txt", "data/vnPara/Sentences2.txt"]
sentences = []

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        sentences.extend(f.readlines())
        f.close()

sentences = list(dict.fromkeys(sentences))

with open("data/vnPara/vnPara_removed_dupe.txt", 'w', encoding='utf-8') as f:
    f.writelines(sentences)
    f.close()

train = []
test = []
validation = []
train, test = train_test_split(sentences, test_size=500, random_state=42)
train, validation = train_test_split(train, test_size=500, random_state=42)

with open("data/vnPara/train.txt", 'w', encoding='utf-8') as f:
    f.writelines(train)
    f.close()
with open("data/vnPara/test.txt", 'w', encoding='utf-8') as f:
    f.writelines(test)
    f.close()
with open("data/vnPara/validation.txt", 'w', encoding='utf-8') as f:
    f.writelines(validation)
    f.close()