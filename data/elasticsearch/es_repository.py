from elasticsearch import Elasticsearch
import requests
import uuid
import logging
from configparser import ConfigParser
from enum import Enum
import numpy as np

from api.sql import SQLRecordsCount

config = ConfigParser()
config.read('config.ini')


class NLPModel(Enum):
    PV_DM = 0
    SIF = 1
    PHOBERT = 2


class NewsTitle:
    # cấu trúc dữ liệu được đánh chỉ mục vào Elasticsearch
    mappings = {
        "mappings": {
            "properties": {
                "sentence": {
                    "type": "text",
                    "analyzer": "vi_analyzer"
                },
                "pv_dm": {
                    "type": "dense_vector",
                    "dims": config.get("embedding_model", "dimensions")
                }
            }
        }
    }


class News:
    # cấu trúc dữ liệu được đánh chỉ mục vào Elasticsearch
    mappings = {
        "mappings": {
            "properties": {
                "title": {
                    "type": "text",
                    "analyzer": "vi_analyzer"
                },
                "body": {
                    "type": "text",
                    # "analyzer": "vi_analyzer"
                },
                "newscategoryid": {
                    "type": "text",
                },
                "embedding": {
                    "type": "dense_vector",
                    "dims": config.get("embedding_model", "dimensions")
                }
            }
        }
    }

    def __init__(self, id=None, title=None, body=None, newscategoryid=None, embedding=None):
        # khởi tạo mã uuid/guid
        if id == None:
            self.id = str(uuid.uuid4())
        self.title = title
        self.body = body
        self.newscategoryid = newscategoryid
        self.embedding = None


class ES_Repository:
    def __init__(self):
        # read ES config
        # create connection to hosts/nodes
        self.hosts = [host.strip() for host in config.get(
            "elasticsearch", "hosts").split('|')]
        self.client = Elasticsearch(self.hosts)
        # kiểm tra kết nối
        if not self.client.ping():
            logging.error(
                "Elasticsearch is not running at {0}".format(self.hosts))
        else:
            logging.info("Elasticsearch is running at {0}".format(self.hosts))
            logging.info("Bootstrapping ES indices")
            self.__bootstrap()

    # bootstrap
    def __bootstrap(self):
        self.__bootstrap_index(index_name=type(
            News()).__name__.lower(), mappings=News.mappings)

    # ping the server
    def Ping(self):
        return self.client.ping()

    # bootstrapping index if it doesn't exist
    def __bootstrap_index(self, index_name=None, mappings=None):
        if index_name == None or mappings == None:
            raise Exception("Bootstrap index or mappings must not be null")
            return
        if not self.client.indices.exists(index=index_name):
            logging.info("Index '{0}': CREATING.".format(index_name))
            response = self.client.indices.create(
                index=index_name, body=mappings)
            if response['acknowledged']:
                logging.info("Index '{0}': READY.".format(index_name))
            else:
                logging.error("Index '{0}': FAILED.".format(index_name))
        else:
            logging.info("Index '{0}': READY.".format(index_name))

    # get document by _id
    def GetById(self, index_name=None, id=None):
        if index_name == None or id == None:
            raise Exception("Document id and index name cannot be null")
            return
        response = self.client.get(index=index_name, id=id)
        return response["_source"]

    # index ONE document
    def Index(self, index_name=None, body=None, id=None):
        if index_name == None or body == None or id == None:
            raise Exception("Document id, body and index name cannot be null")
        response = self.client.index(index=index_name, body=body, id=id)
        return response

    # delete ONE document
    def Delete(self, index_name=None, id=None):
        if index_name == None or id == None:
            raise Exception("Document id and index name cannot be null")
        response = self.client.delete(index=index_name, id=id)
        return response

    # bulk indexing
    def BulkIndex(self, index_name=None, body=None):
        if index_name == None or body == None:
            raise Exception("Body and index name cannot be null")
        response = self.client.bulk(body, index_name)
        return response

    # compare SQL records quantity and Elasticsearch's
    def CheckNewsQuantities(self, index_name):
        sql_quantity = SQLRecordsCount()
        es_quantity = self.client.count(index=index_name)['count']
        return (sql_quantity, es_quantity)

    # check if need to be sync
    def IsNewsDataEqual(self, index_name):
        quantities = self.CheckNewsQuantities(index_name)
        if quantities[0] == quantities[1]:
            return True
        return False

    # STS search
    def News_STS_Search(self, query_vector, size=10, newscategoryid=None):
        if newscategoryid == None or newscategoryid == '':
            query = {
                "match_all": {}
            }
        else:
            query = {
                "match": {
                    "newscategoryid": newscategoryid
                }
            }
        body = {
            "size": size,
            "query": {
                "script_score": {
                    "query": query,
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, doc['embedding']) + 1.0",
                        "params": {"query_vector": query_vector}
                    }
                }
            }
        }

        if query_vector == None or query_vector == '':
            body = {
                "size": size,
                "query": {
                    "function_score": {
                        "functions": [{
                            "random_score": {
                                "seed": "1518707649"
                            }
                        }]
                    }
                }
            }

        response = self.client.search(body=body, index='news')
        return response
