#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
classify_news_grid.py

최적 파라미터를 찾는다.
1. naive_bayes.py 의 664줄에 log()안에 0이 들어가 에러가 나기에 아래와 같이 바꿔넣었다. 혹시 문제가 생기면 나중에 바꾸자.
        self.feature_log_prob_ = (np.log(smoothed_fc +0.000000001)
                                  - np.log(smoothed_cc.reshape(-1, 1)))
2. 윈도우에서는 if __name__ == "__main__": 를 추가해야만 에러가 나지 않는다.

참고
----
* 나이브 베이즈 모델을 이용한다.
* 그리드 검색을 이용한다.
"""

import sys
import os.path
import ujson
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import train_test_split
from sklearn.metrics import precision_score, recall_score, accuracy_score

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
    train_data_file_name = "HyunEco_Season2/report_infomation.txt"

    docs, labels = read_docs(train_data_file_name)
    train_docs, test_docs, train_labels, test_labels = \
        train_test_split(docs, labels)

    vectorizer = TfidfVectorizer()
    #classifier = MultinomialNB()
    sgd = SGDClassifier()
    #sgd = SGDClassifier(n_iter=5, random_state=42)

    pipeline = Pipeline([
        ('vect', vectorizer),
        #('clf', classifier),
        ('clf', sgd),
    ])

    parameters = {
        #"vect__max_features": (5000, None),
        #"vect__ngram_range": ((1, 1), (1, 2)),
        "vect__use_idf": (True, False),
        "vect__smooth_idf": (True, False),
        "vect__sublinear_tf": (True, False),
        #"vect__norm": ("l1", "l2", None),
        "clf__alpha": (0.001, 1.0), #"clf__alpha": (0,0.1, 1.0),  <=이건 MultinomialNB()돌릴때 인자
        #"clf__loss":("hinge", "log", "modified_huber", "squared_hinge", "perceptron", "squared_loss", "huber", "epsilon_insensitive", "squared_epsilon_insensitive"),
        #"clf__penalty" : ("none", "l2", "l1", "elasticnet")
    }

    #param = { loss="hinge", penalty="l2", alpha=1e-3, n_iter=5, random_state=42 }

    grid_search = GridSearchCV(pipeline, parameters, n_jobs=-1,
                                verbose=1, scoring="accuracy", cv=3)
    if __name__ == "__main__":
        grid_search.fit(train_docs, train_labels)
        best_parameters = grid_search.best_estimator_.get_params()
        pred_labels = grid_search.predict(train_docs)

        print("Best score: {}".format(grid_search.best_score_))

        print("Best parameter set:")

        for param_name in sorted(parameters.keys()):
            print("\t{}: {}".format(param_name, best_parameters[param_name]))

        print("Accurary: {}".format(accuracy_score(test_labels, pred_labels)))
        print("Precision: {}".format(precision_score(test_labels, pred_labels)))
        print("Recall: {}".format(recall_score(test_labels, pred_labels)))

main()
