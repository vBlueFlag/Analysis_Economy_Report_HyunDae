#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
get_kpop_topic_words.py

한국 가요 가사에 토픽 모델링을 적용하여 토픽별 어휘를 출력한다.

사용법
------
$ python[3] get_kpop_topic_words.py kpop_morph_anal_file
"""

import sys
import os.path
import ujson
from gensim import corpora
from gensim import models


NUM_TOPICS = 5
NUM_TOPIC_WORDS = 10

FILTER_MAGAZINE_ID = "Nowhere"
FEATURE_POSES = {"NNG", "NNP", "NP", "VV", "VA", "MM", "MAG", "MAJ", "XR"}
PRED_POSES = {"VV", "VA"}



def read_docs(input_file_name):
    """
    주어진 보고서에서 fileName과 titleID 그리고 본문을 형태소 분석한 morphAnal을 가져온다.

    반환값
    ------
    fileName : list [보고서의 파일명]
    titleID : list [보고서의 제목]
    morphAnal : list [형태소 분석된 보고서]
    """

    titles = []
    fileNames = []
    documents = []
    information = []
    inputfileList = []
    inputFolder = 'HyunEco_Season3/morphed/'

    for root, dirs, files in os.walk(inputFolder): # 입력 폴더에서 파일리스트를 받아
        for file in files:
            inputfileList.append(file) # 리스트로 만든다.

    with open(input_file_name, "r", encoding="utf-8") as f:
        information = ujson.load(f)

        for i in range(len(information)):

            if FILTER_MAGAZINE_ID in information[i]['magazineID'] or information[i]['morphedName'] not in inputfileList:
                continue
            title = information[i]['titleID']
            fileName = information[i]['fileName']
            document = gen_doc(information[i]["morphedName"])
            titles.append(title)
            fileNames.append(fileName)
            documents.append(document)
    return documents


def gen_doc(morphedName):

    document = []
    morphed_file = "HyunEco_Season3/morphed/" + morphedName
    try:
        with open(morphed_file, 'r', encoding='utf-8') as morphedReport:
            morphedText = ujson.load(morphedReport)
            for j in range(len(morphedText)):
                document.append(ext_morphs(morphedText[j]['morphAnal']))
    except:
        pass

    return document


def ext_morphs(morphAnal):
    morphs =[]
    for word in morphAnal:
        for morph, pos in word:
            if pos not in FEATURE_POSES: #지금은 모든 MazagineID를 실험한다
                continue
            if pos in PRED_POSES:
                morph = morph + u"다"

            morphs.append(morph)

    doc = " ".join(morphs)

    return doc


def build_doc_word_matrix(docs):
    """
    문서 어휘 행렬을 구성하여 돌려준다.

    인자
    ----
    docs : list
        문서들을 원소로 하는 리스트

    반환값
    ------
    corpus : list
        어휘 가방 모형으로 표현된 문서의 리스트

    dictionary : dictionary
        문서들에서 추출된 어휘 딕셔너리
    """

    dictionary = corpora.Dictionary(docs)
    
    corpus = []

    for doc in docs:
        bow = dictionary.doc2bow(doc)
        corpus.append(bow)

    # 리스트 내포 사용
    # corpus = [dictionary.doc2bow(doc) for doc in docs]

    return corpus, dictionary


def print_topic_words(model):
    """
    토픽별로 토픽 어휘들을 출력한다.

    인자
    ----
    model : 토픽 모델
    """

    for topic_id in range(model.num_topics):
        word_probs = model.show_topic(topic_id, NUM_TOPIC_WORDS)
        print("Topic ID: {}".format(topic_id))

        for word, prob in word_probs:
            print("\t{}\t{}".format(word, prob))

        print("\n")


def main():
    """
    한국 가요 가사에 토픽 모델링을 적용한다.

    인자
    ------
    kpop_morph_anal_file_name : string
        K-Pop 형태소 분석 파일
    """
    input_file_name = "HyunEco_Season3/report_infomation.txt"

    docs = read_docs(input_file_name)
    corpus, dictionary = build_doc_word_matrix(docs)
    model = models.ldamodel.LdaModel(corpus, num_topics=NUM_TOPICS,
                                     id2word=dictionary,
                                     alpha=1)
    print_topic_words(model)

main()
