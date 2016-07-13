#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
draw_kpop_singer_mst.py

K-pop 텍스트 집합에서 가수 네트워크를 생성하여 표시한다.

사용법
------
$ python[3] draw_kpop_singer_mst.py kpop_morph_anal_file

참고
----
* scikit-learn과 networkx 라이브러리를 사용한다.
* 최소 신장 트리를 생성한다.
"""

import sys
import os.path
import ujson
from itertools import combinations
# default dict 사용
# from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import pairwise_distances
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

NUM_FEAT_WORDS = 300
SINGER_APPEAR_CUT = 1

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

    document = " ".join(document)
    return document


def ext_morphs(morphAnal):
    morphs = []
    for word in morphAnal:
        #for word in sen:
        for morph_lex, morph_pos in word:
            if morph_pos not in FEATURE_POSES: #지금은 모든 MazagineID를 실험한다
                continue
            if morph_pos in PRED_POSES:
                morph = morph + u"다"

            morphs.append(morph_lex)
    doc = " ".join(morphs)

    return doc


def split_singer_docs(singer_docs):
    """
    조건에 맞는 가수들의 가사들을 하나로 합치고 가수와 함께 돌려준다.

    인자
    ----
    singer_docs : dictionary
        가수를 키로, 해당 가수가 발표한 노래 가사들의 리스트를 값으로 가지는
        딕셔너리

    반환값
    ------
    flat_docs : list
        가수별로 하나로 합친 가사를 원소로 갖는 리스트

    singers : list
        가수 리스트
    """

    flat_docs = []
    singers = []

    for singer, docs in sorted(singer_docs.items()):
        if len(docs) < SINGER_APPEAR_CUT:
            continue

        flat_doc = " ".join(docs)
        flat_docs.append(flat_doc)
        singers.append(singer)

    return flat_docs, singers


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
    """

    vectorizer = CountVectorizer(binary=True, max_features=NUM_FEAT_WORDS)
    doc_word_mat = vectorizer.fit_transform(docs)

    return doc_word_mat


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


def build_word_cooc_mst(cos_sim_mat, singers):
    """
    유사도 네트워크를 생성하고 최소 신장 트리를 추출하여 돌려준다.

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

    G = nx.Graph()

    for i, j in combinations(range(len(singers)), 2):
        G.add_edge(singers[i], singers[j],
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


def main(kpop_morph_anal_file_name):
    """
    K-Pop 텍스트 집합에서 가수 네트워크를 생성하여 표시한다.

    인자
    ----
    kpop_morph_anal_file_name : string
        K-Pop 형태소 분석 파일 이름
    """

    singer_docs = read_singer_docs(kpop_morph_anal_file_name)
    flat_docs, singers = split_singer_docs(singer_docs)
    doc_word_mat = build_doc_word_matrix(flat_docs)
    word_cooc_mat = build_word_cooc_matrix(doc_word_mat)
    cos_sim_mat = build_cosine_sim_matrix(word_cooc_mat)
    T = build_word_cooc_mst(cos_sim_mat, singers)
    draw_mst(T)

main("kpop_1990-2015.ma.txt")
