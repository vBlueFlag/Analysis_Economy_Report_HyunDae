#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
word2vec_reviews.py

네이버 영화 리뷰에 대하여 word2vec 분석을 수행한다.

사용법
------
$ python[3] word2vec_reviews.py ma_file_name
"""

import sys
import os.path
import ujson
from gensim.models import Word2Vec


APP_NAME = os.path.basename(sys.argv[0])
LABEL_KEY = "label"
DOCUMENT_MA_KEY = "document_ma"
FEATURE_POSES = {
    "NNG", "NNP", "XR", "VV", "VA", "MM", "MAG", "IC", "SF"
}
PRED_POSES = {"VV", "VA"}


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
    """

    docs = []

    with open(ma_file_name, "r", encoding="utf-8") as data_file:
        for line in data_file:
            doc_obj = ujson.loads(line.strip())
            doc = gen_doc(doc_obj[DOCUMENT_MA_KEY])
            docs.append(doc)

    return docs


def gen_doc(ma_res):
    """
    형태소 분석 결과로부터 입력 문서를 만들어 돌려준다.

    인자
    ----
    ma_res : list
        형태소 분석 결과를 담고 있는 리스트

    반환값
    ------
    doc : string
        주요 폼사 형태소만으로 이루어진 문서
    """

    morphs = []

    for sent in ma_res:
        for word in sent:
            for morph, pos in word:
                if pos not in FEATURE_POSES:
                    continue

                if pos in PRED_POSES:
                    morph += u"다"

                morph = morph.replace(" ", "")
                morphs.append(morph)

    return morphs


def main(ma_file_name):
    """
    네이버 영화 리뷰에 대하여 word2vec 분석을 수행한다.

    인자
    ----
    ma_file_name : string
        형태소 분석 파일 이름
    """

    docs = read_docs(ma_file_name)
    model = Word2Vec(docs, window=5, min_count=5, size=100)

    for word, sim in model.similar_by_word(u"이정재", topn=20): #이정재와 가장 비슷한 단어 20개를 보여줘
        print("{}\t{}".format(word, sim))

    print()

    for word, sim in model.similar_by_word(u"예쁘다", topn=20):
        print("{}\t{}".format(word, sim))

    print()

    for word, sim in model.most_similar(positive=[u"이정재", u"고소영"],
                                        topn=20):
        print("{}\t{}".format(word, sim))


#if len(sys.argv) < 2:
#    print("usage: {} review_ma_file".format(APP_NAME))
#    sys.exit(1)

main("ratings.ma.txt")
