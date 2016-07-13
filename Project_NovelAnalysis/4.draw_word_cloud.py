#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
draw_word_cloud.py

워드 클라우드를 그린다.

좋아. 여기까지 왔다. 
1. 먼저 12권 각각의 워드 클라우드를 그리고
2. 그것을 자동으로 저장한다.
2. 다음 12권 전체를 하나의 txt 랭킹 파일로 만든 후 그것의 워드 클라우드도 그린다.

참고
----
* 입력 파일은 다음과 같은 형식의 TSV 파일이다.
  형태소[TAB]품사태그[TAB]빈도
* 입력 파일은 형태소 빈도 역순으로 정렬되어 있어야 한다.
"""

import sys
import os.path
import matplotlib.pyplot as plt
import wordcloud

import os
inputfileList = []
outputFileList = []
inputFolder = 'Project_NovelAnalysis/ranked/'
outputFolder = 'Project_NovelAnalysis/result_wordcloud/'

if not os.path.isdir(outputFolder): # 결과 출력 폴더가 없다면
    os.mkdir(outputFolder)  # 폴더를 만든다

for root, dirs, files in os.walk(inputFolder): # 입력 폴더에서 파일리스트를 받아
    for file in files:
        inputfileList.append(root + file) # 리스트로 만든다.
        outputFileList.append( outputFolder + file+ '.png')

# 워드 클라우드 배경색
BACKGROUND_COLOR = "black"
# 워드 클라우드 폭
WIDTH = 1500
# 워드 클라우드 높이
HEIGHT = 900

# 윈도우 사용자는 아래와 같이 워드 클라우드에 사용할 글꼴을 지정한다.
FONT_PATH = "C:/Windows/Fonts/malgun.ttf"

# 품사 필터링을 위한 품사 분류
NOMINALS = {    # 체언
    "NNG",      # 일반명사
    "NNP",      # 고유명사
    "XR",       # 어근 ("공부"+하다)
    "SH",       # 한자
    "SL",       # 외국어 (로만문자)
}
PREDICATES = {  # 용언
    "VV",       # 동사
    "VA",       # 형용사
}
MODIFIERS = {   # 수식언
    "MM",       # 관형사
    "MAG",      # 일반부사
}
FILTER_IN_POSES = NOMINALS | PREDICATES | MODIFIERS
# 최대 단어 수
MAX_NUM_WORDS = 200


def read_word_counts(word_count_file_name):
    """
    어휘 빈도를 읽어서 돌려준다.

    인자
    ----
    word_count_file_name : string
        어휘(형태소) 빈도가 기록된 파일 이름

    반환값
    ------
        (words, counts) : tuple
            어휘의 리스트와 빈도수의 리스트로 이루어진 튜플
    """

    words = []
    counts = []

    with open(word_count_file_name, "r") as word_count_file:
        word_num = 0

        for line in word_count_file:
            word, pos, count = line.strip().split("\t")

            if pos not in FILTER_IN_POSES: #pos는 일단 사용하지 않는다.
                continue

            count = int(count)
            words.append(word)
            counts.append(count)
            word_num += 1

            if word_num == MAX_NUM_WORDS:
                break

    return words, counts


def adjust_counts(counts):
    """
    어휘 빈도를 조정하여 돌려준다.

    인자
    ----
    counts : list
        어휘 빈도로 이루어진 리스트

    반환값
    ------
    adj_counts : list
        조정된 빈도로 이루어진 리스트

    참고
    ----
    원 빈도를 10으로 나눈 뒤 반올림하고 정수화하여 빈도를 조정한다.
    """

    adj_counts = []

    for count in counts:
        adj_count = int(round(count / 10.0))
        adj_counts.append(adj_count)

    # 위의 for 문은 아래의 리스트 내포로 표현 가능하다.
    # adj_counts = [int(round(count / 10.0)) for count in counts]

    return adj_counts


def generate_text(words, counts):
    """
    어휘 빈도를 반영하여 텍스트를 생성한다.

    인자
    ----
    words : list
        어휘의 리스트

    counts : list
        조정된 어휘 빈도의 리스트

    반환값
    ------
    text : string
        조정된 어휘 빈도를 반영하여 빈도수만큼 어휘가 반복된 텍스트
    """

    text_words = []

    for word, count in zip(words, counts):
        sub_text_words = [word] * count
        text_words.extend(sub_text_words)
        # text_words += sub_text_words

    text = " ".join(text_words)

    return text


def draw_cloud(text):
    """
    워드 클라우드를 생성하여 돌려준다.

    인자
    ----
    text : string
        워드 클라우드 생성 대상 문자열

    반환값
    ------
    cloud : graphic object
        생성된 워드 클라우드 객체
    """

    cloud_gen = wordcloud.WordCloud(background_color=BACKGROUND_COLOR,
                                    width=WIDTH, height=HEIGHT,
                                    font_path=FONT_PATH)
    cloud = cloud_gen.generate(text)

    return cloud


def show_cloud(cloud, outputFileList):
    """
    워드 클라우드를 화면에 표시한다.

    인자
    ----
    cloud : graphic object
        생성된 워드 클라우드 객체
    """

    plt.imshow(cloud)
    plt.axis("off")
    fig = plt.gcf()
    fig.savefig(outputFileList)
    #plt.show()
    plt.close()

def main():
    """
    워드 클라우드를 그린다.

    인자
    ----
    word_count_file_name : string
        어휘(형태소) 빈도 파일 이름
    """
    for i in range(len(inputfileList)):
        words, counts = read_word_counts(inputfileList[i])
        counts = adjust_counts(counts)
        text = generate_text(words, counts)
        cloud = draw_cloud(text)
        show_cloud(cloud, outputFileList[i])

main()
