#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
draw_word_cooc_net.py

K-pop 텍스트 집합에서 어휘 공기 네트워크를 생성하여 표시한다.

사용법
------
$ python[3] draw_word_cooc_net.py kpop_morph_anal_file

참고
----
scikit-learn과 networkx 라이브러리를 사용한다.
"""


import sys
import os.path
import ujson
from itertools import combinations
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import pairwise_distances
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

NUM_FEAT_WORDS = 50

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
    morphed_file = "HyunEco_Season2/morphed/" + morphedName
    try:
        with open(morphed_file, 'r', encoding='utf-8') as morphedReport:
            morphedText = ujson.load(morphedReport)
            for j in range(len(morphedText)):
                document.append(ext_morphs(morphedText[j]['morphAnal']))
    except:
        pass

    document = " ".join(document)
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
    문서 어휘 행렬을 생성하여 돌려준다.

    인자
    ----
    docs : list
        문서를 원소로 하는 리스트

    반환값
    ------
    doc_word_mat : matrix
        문서 어휘 행렬
    feature_words : list
        자질 어휘 리스트
    """

    vectorizer = CountVectorizer(binary=True, max_features=NUM_FEAT_WORDS)
    doc_word_mat = vectorizer.fit_transform(docs)
    feature_words = vectorizer.get_feature_names()

    return doc_word_mat, feature_words


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


def build_word_cooc_network(cos_sim_mat, feature_words):
    """
    어휘 공기 네트워크를 생성하여 돌려준다.

    인자
    ----
    cos_sim_mat : matrix
        코사인 유사도 행렬

    feature_words : list
        자질 어휘 리스트

    반환값
    ------
    G : network
        어휘 공기 네트워크
    """

    G = nx.Graph()

    for i, j in combinations(range(NUM_FEAT_WORDS), 2):
        G.add_edge(feature_words[i], feature_words[j],
                   weight=cos_sim_mat[i, j])

    return G


def draw_network(G):
    """
    네트워크를 시각화한다.

    인자
    ----
    G : network
        어휘 공기 네트워크
    """

    nodes = nx.nodes(G)
    degrees = nx.degree(G)

    node_size = []

    for node in nodes:
        ns = degrees[node] * 50
        node_size.append(ns)

    # node_size = [degrees[node] * 50 for node in nodes]

    nx.draw(G,
            pos=nx.fruchterman_reingold_layout(G, k=0.2),
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
    K-Pop 텍스트 집합에서 어휘 공기 네트워크를 생성하여 표시한다.

    인자
    ----
    kpop_morph_anal_file_name: : string
        K-Pop 형태소 분석 파일 이름
    """
    input_file_name = "HyunEco_Season3/report_infomation.txt"

    docs = read_docs(input_file_name)
    doc_word_mat, feature_words = build_doc_word_matrix(docs)
    word_cooc_mat = build_word_cooc_matrix(doc_word_mat)
    cos_sim_mat = build_cosine_sim_matrix(word_cooc_mat)
    G = build_word_cooc_network(cos_sim_mat, feature_words)
    draw_network(G)

main()
