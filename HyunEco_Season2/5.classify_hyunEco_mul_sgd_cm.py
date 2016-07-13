#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
혼돈 행렬을 이미지로 보여준다.
'''
import sys
import os.path
import ujson
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.cross_validation import train_test_split
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc #한글 폰트 넣기

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

    with open(morphed_info, 'r', encoding='utf-8') as ma_res:
        morphedText = ujson.load(ma_res)

        for j in range(len(morphedText)):
            document.append(ext_morphs(morphedText[j]['morphAnal']))

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


def plot_confusion_matrix(cm, title):
    """
    혼동 행렬 다이어그램을 그린다.

    인자
    ----
    cm : confusion matrix
        혼동 행렬

    title : string
        제목

    참고
    ----
    http://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html
    """
    font_manager.get_fontconfig_fonts() #한글폰트 설정
    font_info = {'family' : 'nanumgothic', 'weight' : 'bold', 'size'   : 10}
    rc('font', **font_info) # dict로 모든 인자들을 전달할때

    plt.figure()
    plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title(title)
    plt.colorbar()

    target_names = sorted(LABEL_MAP.values())
    tick_marks = np.arange(len(target_names))
    plt.xticks(tick_marks, target_names, rotation=45)
    plt.yticks(tick_marks, target_names)
    plt.tight_layout()
    plt.ylabel("True label")
    plt.xlabel("Predicted label")


def main():
    """
    뉴스 기사를 정치, 경제, 문화, 세 부류로 분류한다.

    인자
    ----
    news_ma_file_name : string
        뉴스 기사 형태소 분석 파일 이름
    """
    train_data_file_name = "HyunEco_Season2/report_infomation.txt"

    docs, labels = read_docs(train_data_file_name)
    train_docs, test_docs, train_labels, test_labels = \
        train_test_split(docs, labels)

    vectorizer = TfidfVectorizer()
    train_doc_term_mat = vectorizer.fit_transform(train_docs)
    test_doc_term_mat = vectorizer.transform(test_docs)

    sgd = SGDClassifier(loss="hinge", penalty="l2", alpha=1e-3,
                        n_iter=5, random_state=42)

    sgd.fit(train_doc_term_mat, train_labels)
    pred_labels = sgd.predict(test_doc_term_mat)

    cm = confusion_matrix(test_labels, pred_labels)
    title = "Confusion matrix w/o normalization"
    print(title)
    print(cm)
    plot_confusion_matrix(cm, title)

    np.set_printoptions(precision=2)
    cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
    title = "Confusion matrix w/ normalization"
    print(title)
    print(cm_norm)
    plot_confusion_matrix(cm_norm, "Confusion matrix w/ normalization")

    plt.show()

main()
