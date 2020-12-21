import requests
import json
import re
import uuid
from enum import Enum
from bs4 import BeautifulSoup
from vncorenlp import VnCoreNLP
import time
from underthesea import sent_tokenize, word_tokenize
from bs4.element import NavigableString

class model(Enum):
    W2V_AVG = 0
    FAST_AVG = 1
    PV_DM = 2
    PV_DBOW = 3
    SIF = 4
    USIF = 5

def tokenize(annotator, text):
    tokens = annotator.tokenize(text)[0]
    return tokens

def clean_tokens(tokens):
    for i, token in enumerate(tokens):
        tokens[i] = token[0].replace('_',' ')
    return tokens

def html_to_sentences(html):
    sentences = []
    soup = BeautifulSoup(html, 'lxml')

    # vnexpress crawler only
    location = soup.find('span', attrs='location-stamp')
    location.decompose()
    author = soup.find('p', attrs='author_mail')
    author.decompose()
    figures = soup.findAll('figure')
    for figure in figures:
        figure.decompose()
    ###
    invalid_tags = ['strong']
    for tag in invalid_tags:
        for match in soup.findAll(tag):
            match.replaceWithChildren()

    pTags = soup.findAll('p')
    
    raw_paragraphs = [p.get_text() for p in pTags]
    paragraphs = [p.get_text() for p in pTags]
    
    for p in paragraphs:
        p = p.replace('\xa0',' ')
        p = p.strip()
        sentences.extend(sent_tokenize(p))
    return sentences

def sentence_tokenize(sentences=None, sentence=None):
    if sentences != None and not isinstance(sentences, list):
        raise Exception("Parameter 'sentences' must be a list")
        return
    if sentence != None and not isinstance(sentence, str):
        raise Exception("Parameter 'sentences' must be a list")
        return
    
    if len(sentences) > 0:
        s = []
        for sent in sentences:
            clean = sent.replace('“','').replace('”','').replace('"','')
            s.append(["_".join(word.split()) for word in word_tokenize(clean)])
        return s
    elif sentence != None:
        return sent_tokenize(sentence)

def crawl_news(url):
    headers = requests.utils.default_headers()
    headers.update({ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})
    request = requests.get(url, headers)
    
    return request.content