#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
7.train_hyunEco_save.py

1. 분류 모델을 학습하여 저장한다. (중요!)
2. 아래와 같이 최적화도 시켜봤다.
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), smooth_idf=False,
                                 sublinear_tf=True, use_idf=True)
3. 학습된 모델을 읽어와 테스트하는 모듈까지 함께 적용했다.

----
나이브 베이즈 모형을 사용한다.
"""


import sys
import os.path
import pickle
import ujson
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.externals import joblib
import random

SUBJ_CODE_KEY = "magazineID"
#TITLE_MA_KEY = "titleID"
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
TRAIN_CHECK = True


def read_docs(train_data_file_name, test_list):
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

    global TRAIN_CHECK

    with open(train_data_file_name, 'r', encoding="utf-8") as f:
        information = ujson.load(f)
        inputfileList, inputFolder = make_inputfileList()
        for i in range(len(information)):

            subj_code = information[i][SUBJ_CODE_KEY]

            if subj_code not in LABEL_MAP or information[i]['morphedName'] not in inputfileList :
                continue

            if TRAIN_CHECK :
                if information[i]['morphedName'] in test_list: #만약 훈련을 하는데 그 데이터가 test_list에 있는 거라면
                    continue # 이건 훈련데이터가 아니라 테스트 데이터니 훈련하지 말고 그냥 넘어가라. 
            else:
                if information[i]['morphedName'] not in test_list:
                    continue
            label = LABEL_MAP[subj_code]
            labels.append(label)

            #title_text = information[i][TITLE_MA_KEY] #타이틀 정보는 넘겨주지 않는다. 컴퓨터가 쉽게 맞출 수 있기 때문에
            body_text = gen_doc(information[i]['morphedName'],inputFolder )
            #doc = "{} {}".format(title_text, body_text) 두개의 형태소 문서가 있을 때 이처럼 넘겨준다
            doc = "{}".format(body_text)
            docs.append(doc)

    # 리스트를 numpy 모듈에서 제공하는 배열로 바꾼다.
    labels = np.asarray(labels)
    docs = np.asarray(docs)
    TRAIN_CHECK = False

    return docs, labels

def make_inputfileList(): #입력 폴더에 있는 파일들의 리스트와 폴더명을 리턴한다.
    inputfileList = []
    inputFolder = 'HyunEco_Season2/morphed/'
    for root, dirs, files in os.walk(inputFolder): # 입력 폴더에서 파일리스트를 받아
        for file in files:
            inputfileList.append(file) #리스트로 만든다.
    return inputfileList, inputFolder

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

def make_test_list(test_list): #테스트 파일 목록을 만들어 리턴한다

    rand_set = {}
    inputfileList, _ = make_inputfileList()
    for i in range(len(inputfileList)): #훈련 데이터와 테스트 데이터를 구분하기 위해 모듈을 하나 추가한다.
        test_list.append(random.choice(inputfileList))
        rand_set = set(test_list)
        if len(rand_set) >= len(inputfileList)/10:
            break
    test_list = list(rand_set) #test_list에는 랜덤하게 뽑힌 211개의 중복되지 않은 파일명 리스트가 들어가 있다.
    return test_list


def main():
    """
    보고서 모델을 저장하고 테스트 한다. 원래는 훈련과 테스트가 쪼개져 있는데
    현재 두개를 분리하는 모델을 하나로 만들어놨기 때문에 하나의 파일로 합쳐서 테스트한다.
    """
    test_list  = []
    test_list = make_test_list(test_list) #테스트로 활용할 목록을 만들어 리턴한다.
    # 1. joblib 모듈을 이용해 학습 모델(nb_new.txt)을 만든다.
    train_data_file_name = "HyunEco_Season2/report_infomation.txt"
    test_data_file_name = "HyunEco_Season2/report_infomation.txt"
    model_file_name = "HyunEco_Season2/nb_new.txt"

    train_docs, train_labels = read_docs(train_data_file_name,test_list)
    print(u"훈련중...")
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), smooth_idf=False,
                                 sublinear_tf=True, use_idf=True)
    #classifier = MultinomialNB(alpha=1.0)

    sgd = SGDClassifier(loss="hinge", penalty="l2", alpha=1e-3, n_iter=5, random_state=42)
    #sgd.fit(train_doc_term_mat, train_labels)
    #pred_labels = sgd.predict(test_doc_term_mat)

    pipeline = Pipeline([
        ('vect', vectorizer),
        #('clf', classifier), #이건 MultinomialNB()클래스로 훈련
        ('clf', sgd), #이건 SGDClassifier()클래스 - SVM 백터기계 알고리즘으로 훈련
    ])

    pipeline.fit(train_docs, train_labels)
    joblib.dump(pipeline, model_file_name, compress=9)
    #w = open(model_file_name,'wb') #이건 pickle모듈로 저장해본 것이다.
    #pickle.dump(pipeline,w)
    #w.close()
    print(u"훈련완료.\n테스트 중...")
    # 2. 저장된 모델(nb_new.txt)을 바탕으로 테스트 
    # - 나중에 테스트 파일만 나눠 사용할때는 8번 파이썬 파일을 참고해서 아래의 코드들을 넣으면 된다.
    test_docs, test_labels = read_docs(test_data_file_name,test_list)
    clf = joblib.load(model_file_name)
    #f = open(model_file_name,'rb') #이건 pickle모듈로 읽어오기 한것이다.
    #clf = pickle.load(f)
    #f.close()
    pred_labels = clf.predict(test_docs)
    num_correct = 0

    for test_label, pred_label in zip(test_labels, pred_labels):
        if test_label == pred_label:
            num_correct += 1

    accuracy = num_correct / len(test_labels)
    print("Accuracy: {}".format(accuracy))


main()
