#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
sent_anal_reviews_d2v.py

네이버 영화 리뷰를 감성 분류한다.

사용법
------
$ python[3] sent_anal_reviews_d2v.py ma_file_name

참고
----
doc2vec을 이용한다.
"""

import sys
import os.path
import ujson
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from gensim.models.doc2vec import TaggedDocument
from gensim.models.doc2vec import Doc2Vec

APP_NAME = os.path.basename(sys.argv[0])
LABEL_KEY = "label"
DOCUMENT_MA_KEY = "document_ma"
FEATURE_POSES = [
    "NNG", "NNP", "XR", "VV", "VA", "MM", "MAG", "IC", "SF"
]
LABEL_MAP = {
    "0": "neg",
    "1": "pos",
}


def read_docs(ma_file_name):
    """
    형태소 분석 파일에서 문서들과 레이블을 읽어서 돌려준다.

    인자
    ----
    ma_file_name : string
        형태소 분석 파일 이름

    반환값
    ------
    docs : list
        문서들을 원소로 하는 리스트

    labels : list
        문서들에 부여된 레이블을 원소로 하는 리스트
    """

    labels = []
    docs = []

    with open(ma_file_name, "r", encoding="utf-8") as data_file:
        for line in data_file:
            doc_obj = ujson.loads(line.strip())
            label_code = doc_obj[LABEL_KEY]

            if label_code not in LABEL_MAP:
                continue

            label = LABEL_MAP[label_code]
            labels.append(label)
            doc = gen_doc(doc_obj[DOCUMENT_MA_KEY])
            docs.append(doc)

    return docs, labels


def gen_doc(ma_res):
    """
    형태소 분석 결과로부터 입력 문서를 만들어 돌려준다.

    인자
    ----
    ma_res : list
        형태소 분석 결과를 담고 있는 리스트

    반환값
    ------
    morphs : list
        문서의 형태소들을 원소로 하는 리스트
    """

    morphs = []

    for sent in ma_res:
        for word in sent:
            for morph, pos in word:
                if pos not in FEATURE_POSES:
                    continue

                morph = morph.replace(" ", "")
                morphs.append(morph + "/" + pos)

    return morphs


def get_tagged_docs(docs, labels):
    """
    TaggedDocument 리스트를 만들어 돌려준다.

    인자
    ----
    docs : list
        문서들을 원소로 하는 리스트

    labels : list
        각 문서의 레이블을 원소로 하는 리스트

    반환값
    ------
    tagged_docs : list
        TaggedDocument 객체를 원소로 하는 리스트
    """

    tagged_docs = []

    for doc, label in zip(docs, labels):
        tagged_doc = TaggedDocument(doc, [label])
        tagged_docs.append(tagged_doc)

    return tagged_docs


def get_doc_feat_matrix(vectorizer, tagged_docs):
    """
    문서 자질 행렬을 생성하여 돌려준다.

    인자
    ----
    vectorizer : vectorizer
        Doc2Vec 객체

    tagged_docs : list
        TaggedDocument 객체를 원소로 하는 리스트

    반환값
    ------
    doc_feat_mat : matrix
        문서 자질 행렬
    """

    doc_feat_mat = []

    for doc in tagged_docs:
        doc_feat_mat.append(vectorizer.infer_vector(doc.words))

    return doc_feat_mat


def main(ma_file_name):
    """
    영화 리뷰를 나이브 베이즈 기법으로 분류한다.

    인자
    ----
    ma_file_name : string
        형태소 분석 파일 이름
    """

    docs, labels = read_docs(ma_file_name)
    train_docs, test_docs, train_labels, test_labels = \
        train_test_split(docs, labels)

    tagged_train_docs = get_tagged_docs(train_docs, train_labels)
    tagged_test_docs = get_tagged_docs(test_docs, test_labels)

    vectorizer = Doc2Vec(size=300, alpha=0.025, min_alpha=0.025, workers=2)
    vectorizer.build_vocab(tagged_train_docs)

    for epoch in range(10):
        print("Training iteration {}".format(epoch))
        vectorizer.train(tagged_train_docs)
        vectorizer.alpha -= 0.002
        vectorizer.min_alpha = vectorizer.alpha

    train_doc_feat_mat = get_doc_feat_matrix(vectorizer, tagged_train_docs)
    test_doc_feat_mat = get_doc_feat_matrix(vectorizer, tagged_test_docs)

    clf = LogisticRegression()
    clf.fit(train_doc_feat_mat, train_labels)
    pred_labels = clf.predict(test_doc_feat_mat)
    accuracy = accuracy_score(test_labels, pred_labels)

    print("Accuracy: {}".format(accuracy))


if len(sys.argv) < 2:
    print("usage: {} review_ma_file".format(APP_NAME))
    sys.exit(1)

main(sys.argv[1])

