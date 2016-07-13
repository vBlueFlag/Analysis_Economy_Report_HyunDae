#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
벡터기계(SVM) 알고리즘 모듈 내 KFold클래스를 이용한 교차검증
"""

import sys
import os.path
import ujson
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.cross_validation import KFold
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score

SUBJ_CODE_KEY = "magazineID"
FEATURE_POSES = {"NNG", "NNP", "NP" "XR", "VV" "VA", "MM", "MAG", "MAJ", "XR"}
LABEL_MAP = {
    "VIP Report": "VIP Report", # vip
    "한국경제주평" : "한국경제주평", #korea
    "이슈리포트" : "이슈리포트", #issue
    "연금시장리뷰" :"연금시장리뷰", #pension
    "Chairperson Note" : "Chairperson Note", #chair
    "통일경제" : "통일경제", #unity
    "지식경제" : "지식경제" #knowledge
}

#LABEL_MAP = {
#    "VIP Report": "VIP Report", # vip
#    "한국경제주평" : "한국경제주평", #korea
#    "이슈리포트" : "이슈리포트", #issue
#    "Chairperson Note" : "Chairperson Note", #chair
#}

def read_docs(train_data_file_name):
    """
    형태소 분석 파일에서 문서와 레이블을 읽어서 돌려준다.

    인자
    ----
    news_ma_file_name : string
        뉴스 기사 형태소 분석 파일 이름

    반환값
    ------
    docs : numpy.array
        문서들을 원소로 하는 numpy 배열

    labels : numpy.array
        레이블들을 원소로 하는 numpy 배열
    """

    labels = []
    docs = []
    information = []

    inputfileList = []
    inputFolder = 'HyunEco_Season2/morphed/'
    for root, dirs, files in os.walk(inputFolder): # 입력 폴더에서 파일리스트를 받아
        for file in files:
            inputfileList.append(file) # 리스트로 만든다.

    with open(train_data_file_name, 'r', encoding="utf-8") as f:
        information = ujson.load(f)

        for i in range(len(information)):

            subj_code = information[i][SUBJ_CODE_KEY]

            if subj_code not in LABEL_MAP or information[i]['morphedName'] not in inputfileList :
                continue

            label = LABEL_MAP[subj_code]
            labels.append(label)

            #title_text = information[i][TITLE_MA_KEY] #타이틀 정보는 넘겨주지 않는다. 컴퓨터가 쉽게 맞출수 있기 때문에
            body_text = gen_doc(information[i]['morphedName'],inputFolder )
            #doc = "{} {}".format(title_text, body_text) 두개의 형태소 문서가 있을 때 이처럼 넘겨준다
            doc = "{}".format(body_text)
            docs.append(doc)

    # 리스트를 numpy 모듈에서 제공하는 배열로 바꾼다.

    labels = np.asarray(labels)
    docs = np.asarray(docs)

    return docs, labels


def gen_doc(morphed_file,inputFolder):

    morphed_info = inputFolder + morphed_file
    document = []
    try:
        with open(morphed_info, 'r', encoding='utf-8') as ma_res:
            morphedText = ujson.load(ma_res)

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

            morphs.append(morph)

    doc = " ".join(morphs)

    return doc


def main():
    """

    """
    report_infomation_name = "HyunEco_Season2/report_infomation.txt"
    docs, labels = read_docs(report_infomation_name)
    vectorizer = TfidfVectorizer()
    sgd = SGDClassifier(loss="hinge", penalty="l2", alpha=1e-3, n_iter=5, random_state=42)

    num_folds = 10
    accuracies = []
    precisions = []
    recalls = []
    f1s = []

    cross_val_set = KFold(n=len(docs), n_folds=num_folds, shuffle=True)

    for train, test in cross_val_set:
        train_docs = docs[train]
        train_labels = labels[train]
        test_docs = docs[test]
        test_labels = labels[test]

        train_doc_term_mat = vectorizer.fit_transform(train_docs)
        test_doc_term_mat = vectorizer.transform(test_docs)

        sgd.fit(train_doc_term_mat, train_labels)
        pred_labels = sgd.predict(test_doc_term_mat)

        accuracy = accuracy_score(test_labels, pred_labels)
        precision = precision_score(test_labels, pred_labels, average="macro")
        recall = recall_score(test_labels, pred_labels, average="macro")
        f1 = f1_score(test_labels, pred_labels, average="macro")

        accuracies.append(accuracy)
        precisions.append(precision)
        recalls.append(recall)
        f1s.append(f1)

    print("Accuracy\tPrecision\tRecall\t\tF1")

    for accuracy, precision, recall, f1 in zip(accuracies, precisions,
                                               recalls, f1s):
        print("{:.5f}\t\t{:.5f}\t\t{:.5f}\t\t{:.5f}".format(accuracy,
                                                            precision,
                                                            recall, f1))

    print()
    print("Avg Accuracy: {}, Std Dev: {}".format(np.mean(accuracies),
                                                 np.std(accuracies)))
    print("Avg Precision: {}, Std Dev: {}".format(np.mean(precisions),
                                                  np.std(precisions)))
    print("Avg Recall: {}, Std Dev: {}".format(np.mean(recalls),
                                               np.std(recalls)))
    print("Avg F1: {}, Std Ddev: {}".format(np.mean(f1s), np.std(f1s)))


main()
