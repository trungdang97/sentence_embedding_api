# migrate from mongodump to mssql

import pyodbc
import pymongo
import requests
from vncorenlp import VnCoreNLP
import uuid
import time

start_time = time.time()
print("Opening connections...")
MSSQL = pyodbc.connect(
    Trusted_Connection='No',
    UID='sa',
    PWD='admin@123',
    Driver='{SQL Server}',
    Server='DESKTOP-A8POG6O\SQLEXPRESS',
    Database='NewsDatabase'
)
cursor = MSSQL.cursor()

categories = []
cursor.execute('select NewsCategoryId, Name from NewsCategory')
for row in cursor:
    categories.append({"id":row[0], "name": row[1]})

class MongoClient():
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.database = self.client["news"]
        self.collection = self.database["vietnamese"]

client = MongoClient()
documents = list(client.collection.aggregate([
    {"$sample": {"size": 50000}}
]))

print("Preparing data...")
news_list = []
for doc in documents:
    if len(doc['cates']) > 0:
        doc['cates'] = doc['cates'][0]
    else:
        doc['cates'] = 'Uncategorized'
    doc['cates'] = next(item["id"] for item in categories if item["name"] == doc['cates'])
    if doc['sapo'] != '' and doc['body'] != '':
        news_list.append({'id':doc['id'], 'title':doc['title'], 'abstract':doc['sapo'], 'body':doc['body'], 'cates':doc['cates']})

news_list = list({n['id']:n for n in news_list}.values())
for i, news in enumerate(news_list):
    news_list[i]['id'] = str(uuid.uuid4())

tuples = [tuple(d.values()) for d in news_list]

print("Inserting data...")
cmd = "insert into News(NewsId, Title, Abstract, Body, NewsCategoryId) VALUES(?,?,?,?,?)"
cursor.executemany(cmd, tuples)
MSSQL.commit()
MSSQL.close()
end_time = time.time()
print("Done in {0} seconds.".format(end_time-start_time))