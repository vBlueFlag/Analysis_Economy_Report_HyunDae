#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
build_kpop_word_cooc_mat.py

K-pop 텍스트 집합에서 어휘 공기 행렬을 생성한다.

사용법
------
$ python[3] build_kpop_word_cooc_mat.py kpop_morph_anal_file

참고
----
2차원 딕녀서리를 사용한다.
"""


import sys
import os.path
import ujson
from itertools import combinations
from pprint import pprint
# 단순 2차원 딕셔너리 대신에 collections 모듈의
# defaultdict와 Counter를 이용하면 행렬 구축이 쉽다.
# from collections import defaultdict
# from collections import Counter

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

    doc = " ".join(document)
    return doc


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
    word_cooc_mat : dictioanry of dictionary
        어휘 공기 행렬을 나타내는 2차원 딕셔너리
    """

    word_cooc_mat = {}
    # defaultdict와 Counter를 이용할 수 있다.
    # word_cooc_mat = defaultdict(Counter)

    for doc in docs:
        words = doc.split()

        for word1, word2 in combinations(words, 2):
            if word1 not in word_cooc_mat:
                word_cooc_mat[word1] = {}

            if word2 not in word_cooc_mat[word1]:
                word_cooc_mat[word1][word2] = 1
            else:
                word_cooc_mat[word1][word2] += 1

            # defaultdict와 Counter를 이용하면 위의 두 if 문을
            # 다음 한 줄의 증가 할당문으로 대체할 수 있다.
            # word_cooc_mat[word1][word2] += 1

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
