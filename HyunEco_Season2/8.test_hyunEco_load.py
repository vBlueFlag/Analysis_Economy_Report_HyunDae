#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
test_news_classifier.py

7.번 파이썬 파일안에 8.번 파이썬 모듈이 모두 적용되었다. 이건 사용하지 않는다.
저장된 학습 모듈(nb_new.txt)을 이용해 테스트한다.
현재 테스트 파일이 따로 없어 이대로 돌리면 학습데이터와 테스트데이터가 같아져
정확한 결과가 나오기 어렵다.

사용법
------
$ python[3] classify_news_bin_nb.py test_data_file model_file

참고
----
나이브 베이즈 기법을 사용한다.
"""


import sys
import os.path
import ujson
import pickle
import numpy as np
from sklearn.externals import joblib

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

def read_docs(train_data_file_name):
    """
    형태소 분석 파일에서 문서와 레이블을 읽어서 돌려준다.

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
            if pos in PRED_POSES:
                morph = morph + u"다"

            morphs.append(morph)

    doc = " ".join(morphs)

    return doc


def main():
    """
    저장된 분류기 모델을 시험한다.

    인자
    ----
    test_data_file_name : string
        시험용 데이터 파일 이름

    model_file_name : string
        분류 모델이 저장된 파일 이름
    """
    test_data_file_name = "HyunEco_Season2/report_infomation.txt"
    model_file_name = "HyunEco_Season2/nb_new.txt"

    test_docs, test_labels = read_docs(test_data_file_name)
    clf = joblib.load(model_file_name)
    pred_labels = clf.predict(test_docs)
    num_correct = 0

    for test_label, pred_label in zip(test_labels, pred_labels):
        if test_label == pred_label:
            num_correct += 1

    accuracy = num_correct / len(test_labels)
    print("Accuracy: {}".format(accuracy))

main()
