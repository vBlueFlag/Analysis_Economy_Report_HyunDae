#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
build_kpop_word_cooc_mat_scikit.py

K-pop 텍스트 집합에서 어휘 공기 행렬을 생성한다.

사용법
------
$ python[3] build_kpop_word_cooc_mat_scikit.py kpop_morph_anal_file

참고
----
scikit-learn 라이브러리를 사용한다.
"""


import sys
import os.path
import ujson
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from pprint import pprint

FILTER_MAGAZINE_ID = "Nowhere"
FEATURE_POSES = {"NNG", "NNP", "NP", "VV", "VA", "MM", "MAG", "MAJ", "XR"}
PRED_POSES = {"VV", "VA"}
NUM_CLUSTERS = 10


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
    inputFolder = 'HyunEco_Seaso3/morphed/'

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


def buld_word_cooc_mat(docs):
    """
    텍스트 집합으로부터 어휘 공기 행렬를 생성하여 돌려준다.

    인자
    ----
    docs : list
        문서들을 원소로 하는 리스트

    반환값
    ------
    word_cooc_mat : array
        어휘 공기 행렬을 나타내는 2차원 배열
    """

    vectorizer = CountVectorizer(binary=True)
    doc_word_mat = vectorizer.fit_transform(docs)
    trans_doc_word_mat = doc_word_mat.transpose()
    word_cooc_mat = trans_doc_word_mat.dot(doc_word_mat).toarray()
    np.fill_diagonal(word_cooc_mat, 0)

    return word_cooc_mat


def main():
    """
    K-Pop 텍스트 집합에서 어휘 공기 행렬을 생성한다.

    인자
    ----
    kpop_morph_anal_file_name: : string
        K-Pop 형태소 분석 파일 이름
    """

    input_file_name = "HyunEco_Season3/report_infomation.txt"

    docs = read_docs(input_file_name)
    word_cooc_mat = buld_word_cooc_mat(docs)
    pprint(word_cooc_mat)


main()
