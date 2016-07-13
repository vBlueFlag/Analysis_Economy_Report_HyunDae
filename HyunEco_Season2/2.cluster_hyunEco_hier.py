#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os.path
import ujson
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.cluster.hierarchy import linkage
from scipy.cluster.hierarchy import dendrogram
import matplotlib
from matplotlib import pyplot as plt

''' 현대경제연구원 보고서 Scikit-learn과 scipy를 이용한 계층 군집 분석
    하고 싶었으나 데이터 양이 너무 많아 한계 초과다. 보고서 title만 형태소 분석한 후 나중에 한번 해보자.
    기술적으로는 특별한 것이 없고 이미 코드수정까지 모두 마쳤기에 이 코드는 그냥 넘어간다 16.07.04
 '''

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
    inputFolder = 'HyunEco_Season2/morphed/'

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
    return titles, fileNames, documents


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


def get_doc_term_mat(documents):
    """
    입력 문서들을 문서-어휘 행렬로 표상하여 벡터라이저와 함께 돌려준다.

    인자
    ----
    documents : list
        문서들을 원소로 하는 리스트

    반환값
    ------
    doc_term_mat : matrix
        문서-어휘 행렬

    vectorizer : vectorizer
        Tfidf 벡터라이저

    참고
    ----
    Tfidf 벡터라이저를 사용한다.
    """

    vectorizer = TfidfVectorizer(min_df=1)
    doc_term_mat = vectorizer.fit_transform(documents)

    return doc_term_mat

def get_hier_clusters(doc_term_mat):
    """
    주어진 문서-어휘 행렬로부터 계층적 클러스터를 생성하여 돌려준다.

    인자
    ----
    doc_term_mat : matrix
        문서-어휘 행렬

    반환값
    ------
    hc : linkage
        계층적 군집 분석 결과
    """

    hc = linkage(doc_term_mat.toarray(), "ward")

    return hc

def plot_linkage(hc, titles):
    """
    계층적 군집 분석 결과(덴드로그램)을 표시한다.

    인자
    ----
    hc : linkage
        계층적 군집 분석 결과

    titles : list
        가요 제목을 원소를 하는 리스트
    """
    count = range(0,300)
    plt.figure(figsize=(40, 80))
    dendrogram(hc, orientation="right",
               # truncate_mode="lastp",
               # p=30,
               # show_contracted=True,
               labels=titles)
    plt.savefig("hier_clust.png", dpi=200)
    # plt.show()
    plt.close()

def main():
    """
    현대경제연구소 보고서들을 군집화한다.

    """
    input_file_name = "HyunEco_Season2/report_infomation.txt"
    output_file_name= "HyunEco_Season2/cluster_HyunEco_flat.txt"

    titles, fileNames, documents = read_docs(input_file_name)
    doc_term_mat = get_doc_term_mat(documents)
    hc = get_hier_clusters(doc_term_mat)
    print(type(hc))
    print(hc)
    plot_linkage(hc, titles)

main()

