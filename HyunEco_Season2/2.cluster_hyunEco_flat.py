#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os.path
import ujson
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

''' 현대경제연구원 보고서 Scikit-learn과 scipy를 이용한 비계층 군집 분석 '''

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

    return doc_term_mat, vectorizer


def get_kmeans_clusters(doc_term_mat):
    """
    보고서 본문을 대상으로 K-평균 군집을 생성한다.

    인자
    ----
    doc_term_mat : matrix
        보고서 본문 문서-어휘 행렬

    반환값
    ------
    km : model
        K-평균 군집 모형
    """

    km = KMeans(n_clusters=NUM_CLUSTERS, init="k-means++", verbose=1)
    km.fit(doc_term_mat)

    return km


def print_clusters(km, titles, fileNames,w):
    """
    군집 분석 결과를 출력한다.

    인자
    ----
    km : model
        K-평균 군집 모형

    titles : list
        보고서 본문을 원소로 하는 리스트

    fileNames : list
    """

    result = {}
    text = []

    for doc_num, cluster_num in enumerate(km.labels_):
        if cluster_num not in result:
            result[cluster_num] = []

        result[cluster_num].append(doc_num)
    
    text.append(u"군집 분석 결과\n")
    text.append(u"목표 군집 수: " + str(NUM_CLUSTERS)+ "\n\n")

    for cluster_num, doc_nums in result.items():
        clustered_titles = []

        for doc_num in doc_nums:
            txt = titles[doc_num] + '(' + fileNames[doc_num]+')'
            clustered_titles.append(txt)

        # clustered_titles = [titles[doc_num] for doc_num in doc_nums]
        instant_titles = " ".join(clustered_titles)
        text.append(u"군집 : "+ str(cluster_num) + u"\t총개수 : " + str(len(clustered_titles)) + u"\t보고서 :\n" + instant_titles +"\n\n")
    text = " ".join(text)
    w.write(text)


def print_centroid_words(km, vectorizer, titles,w):
    """
    군집별 중심 어휘를 출력한다.

    인자
    ----
    km : model
        K-평균 군집 모형

    vectorizer : vectorizer
        Tfidf 벡터라이저

    참고
    ----
    http://scikit-learn.org/stable/auto_examples/text/document_clustering.html
    """
    text = []
    text.append(u"군집별 중심 어휘\n\n")

    ordered_centroids = km.cluster_centers_.argsort()[:, ::-1]
    words = vectorizer.get_feature_names()

    for cluster_num in range(NUM_CLUSTERS):
        center_word_nums = []

        for word_num in ordered_centroids[cluster_num, :20]:
            center_word_nums.append(word_num)

        # center_word_nums = [word_num
        #                     for word_num in ordered_centroids[cluster_num,
        #                                                       :20]]

        center_words = []

        for word_num in center_word_nums:
            center_words.append(words[word_num])

        # center_words = [words[word_num] for word_num in center_word_nums]

        text.append(u"군집 " + str(cluster_num) + " : " + ", ".join(center_words) + "\n")
    text = " ".join(text)
    w.write(text)


def main():
    """
    현대경제연구소 보고서들을 군집화한다.

    """
    input_file_name = "HyunEco_Season2/report_infomation.txt"
    output_file_name= "HyunEco_Season2/cluster_HyunEco_flat.txt"

    titles, fileNames, documents = read_docs(input_file_name)
    doc_term_mat, vectorizer = get_doc_term_mat(documents)
    km = get_kmeans_clusters(doc_term_mat)

    with open(output_file_name, 'w', encoding = 'utf-8') as w:
        print_clusters(km, titles, fileNames,w)
        print_centroid_words(km, vectorizer, titles,w)
    w.close()

main()

