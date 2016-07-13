#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
draw_kpop_topic_word_mst.py

한국 가요 가사에 토픽 모델링을 적용한 다음 토픽별 어휘 공기 네트워크를
생성한다.

사용법
------
$ python[3] draw_kpop_topic_word_mst.py kpop_morph_anal_file
"""

import sys
import os.path
import ujson
from itertools import combinations
from gensim import corpora, models
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import pairwise_distances
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

NUM_TOPICS = 5

FILTER_MAGAZINE_ID = "Nowhere"
#FEATURE_POSES = {"NNG", "NNP", "NP", "VV", "VA", "MM", "MAG", "MAJ", "XR"}
FEATURE_POSES = {"NNG", "NNP", "MM", "MAG","XR"}
PRED_POSES = {"VV", "VA"}
LABEL_MAP = {
    #"VIP Report": "VIP Report", # vip
    #"한국경제주평" : "한국경제주평", #korea
    #"이슈리포트" : "이슈리포트", #issue
    #"연금시장리뷰" :"연금시장리뷰", #pension
    #"Chairperson Note" : "Chairperson Note", #chair
    "통일경제" : "통일경제", #unity
    #"지식경제" : "지식경제", #knowledge
}


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
            if information[i]['magazineID'] not in LABEL_MAP:
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


def build_topic_word_matrix(docs, model):
    """
    토픽 어휘 행렬을 생성하여 돌려준다.

    인자
    ----
    model : model
        토픽 모델링 결과

    반환값
    ------
    topic_word_mat : matrix
        토픽​ 어휘 행렬

    feature_words : list
        자질 어휘 리스트
    """

    str_docs = []

    for doc in docs:
        str_doc = " ".join(doc)
        str_docs.append(str_doc)

    # 리스트 내포 사용
    # str_docs = [" ".join(doc) for doc in docs]

    topic_words = get_topic_words(model)
    vectorizer = CountVectorizer(binary=True, vocabulary=topic_words)
    topic_word_mat = vectorizer.fit_transform(str_docs)

    return topic_word_mat, topic_words


def get_topic_words(model):
    """
    토픽 어휘들을 모아서 돌려준다.

    인자
    ----
    model : model
        토픽 모델링 결과

    반환값
    ------
    topic_words : set
        토픽 어휘 집합
    """

    topic_words = set()

    for topic_id in range(model.num_topics):
        word_probs = model.show_topic(topic_id)

        for word, porb in word_probs:
            topic_words.add(word)

    return topic_words


def build_word_cooc_matrix(doc_word_mat):
    """
    문서 어휘 행렬로부터 어휘 공기 행렬을 생성하여 돌려준다.

    인자
    ----
    doc_word_mat : matrix
        문서 어휘 행렬

    반환값
    ------
    word_cooc_mat : array
        어휘 공기 행렬
    """

    word_cooc_trans_mat = doc_word_mat.transpose()
    word_cooc_mat = word_cooc_trans_mat.dot(doc_word_mat)
    word_cooc_mat = word_cooc_mat.toarray()
    np.fill_diagonal(word_cooc_mat, 0)

    return word_cooc_mat


def build_cosine_sim_matrix(word_cooc_mat):
    """
    어휘 공기 행렬로부터 코사인 유사도 행렬을 생성하여 돌려준다.

    인자
    ----
    word_cooc_mat : matrix
        어휘 공기 행렬

    반환값
    ------
    cos_sim_mat : matrix
        코사인 유사도 행렬
    """

    cos_sim_mat = pairwise_distances(word_cooc_mat, metric="cosine")

    return cos_sim_mat


def build_word_cooc_mst(cos_sim_mat, feature_words):
    """
    어휘 공기 네트워크를 생성하고 최소 신장 트리를 추출하여 돌려준다.

    인자
    ----
    cos_sim_mat : matrix
        코사인 유사도 행렬

    feature_words : list
        자질 어휘 리스트

    반환값
    ------
    T : tree
        어휘 공기 최소 신장 트리
    """

    feature_words = list(feature_words)
    G = nx.Graph()

    for i, j in combinations(range(len(feature_words)), 2):
        G.add_edge(feature_words[i], feature_words[j],
                   weight=cos_sim_mat[i, j])

    T = nx.minimum_spanning_tree(G)

    return T


def draw_mst(T):
    """
    최소 신장 트리를 시각화한다.

    인자
    ----
    T : tree
        최소 신장 트리
    """

    nodes = nx.nodes(T)
    degrees = nx.degree(T)

    node_size = []

    for node in nodes:
        ns = degrees[node] * 400
        node_size.append(ns)

    # node_size = [degrees[node] * 400 for node in nodes]

    nx.draw(T,
            pos=nx.spring_layout(T, k=0.02),
            node_size=node_size,
            node_color="#FFE27F",
            font_family="malgun gothic",
            # 오에스텐을 위한 글꼴 설정
            # font_family="Apple SD Gothic Neo",
            label_pos=0,  # 0=head, 0.5=center, 1=tail
            with_labels=True,
            font_size=13)

    plt.axis("off")
    # plt.savefig("graph.png")
    plt.show()


def main():
    """
    한국 가요 가사에 토픽 모델링을 적용한 다음 토픽별 어휘 공기 네트워크를
    생성한다.

    인자
    ----
    kpop_morph_anal_file_name : string
        한국 가요 가사 형태소 분석 파일 이름
    """
    input_file_name = "HyunEco_Season3/report_infomation.txt"

    docs = read_docs(input_file_name)
    corpus, dictionary = build_doc_word_matrix(docs)
    model = models.ldamodel.LdaModel(corpus, num_topics=NUM_TOPICS,
                                     id2word=dictionary,
                                     alpha=1)

    topic_word_mat, topic_words = build_topic_word_matrix(docs, model)
    word_cooc_mat = build_word_cooc_matrix(topic_word_mat)
    cos_sim_mat = build_cosine_sim_matrix(word_cooc_mat)
    T = build_word_cooc_mst(cos_sim_mat, topic_words)
    draw_mst(T)

main()
