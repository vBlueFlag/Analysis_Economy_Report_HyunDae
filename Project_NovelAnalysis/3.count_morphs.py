#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
> 3.count_morph.py
----
형태소 분석 완료된 파일을 빈도계수에 맞춰 랭킹화 하여 파일로 출력한다.

> 참고
----
입력 파일은 형태소 분석 결과 파일이다.
"""

import sys
import os.path
from collections import Counter
import ujson

import winsound, sys # 다 끝나면 소리가 나게 만들어봤다. 근데 이건 양이 적어 그다지 필요없다.
def beep(sound):
    winsound.PlaySound('%s' % sound, winsound.SND_FILENAME)

import os
inputfileList = []
outputFileList = []
inputFolder = 'Project_NovelAnalysis/morphed/'
outputFolder = 'Project_NovelAnalysis/ranked/'

if not os.path.isdir(outputFolder): # 결과 출력 폴더가 없다면
    os.mkdir(outputFolder)  # 폴더를 만든다

for root, dirs, files in os.walk(inputFolder): # 입력 폴더에서 파일리스트를 받아
    for file in files:
        inputfileList.append(root + file) # 리스트로 만든다.
        outputFileList.append( outputFolder + file)
MORPH = "morphAnal"

'''
{ ‘morphAnal’ : [ 한 문장 [ 한 어절 [ ‘형태소’ , ‘형태소 약어’] ] ],
  ‘text’ : ‘전체 문장’ }
'''

def ext_morphs(ma_res):
    """
    구조화된 형태소 분석 결과에서 형태소들을 추출하여 돌려준다.

    인자
    ----
    ma_res : list
        구조화된 형태소 분석 결과가 들어 있는 리스트 객체

    반환값
    ------
    morphs: list
        형태소와 태그의 튜플로 이루어진 리스트
    """

    morphs = []


    for word in ma_res: #먼저 어절을 뽑아내고
        for morph_lex, morph_pos in word: #다음 형태소를 뽑아낸다.
            morphs.append((morph_lex, morph_pos))

    return morphs


def main():
    morph_counter = Counter()

    for i in range(len(inputfileList)):
        f = open(inputfileList[i],'r') 
        w = open(outputFileList[i],'w')
        for line in f:
            doc_obj = ujson.loads(line)
            title_morphs = ext_morphs(doc_obj[MORPH])
            morph_counter.update(title_morphs)

        # 형태소 빈도 계수 결과를 빈도 역순으로 출력 파일에 기록한다.
        for (morph_lex, morph_pos), count in morph_counter.most_common():
            print("{}\t{}\t{}".format(morph_lex, morph_pos, count),file=w)

    f.close()
    w.close()  
    if __name__ == '__main__':
        beep('MyWay.mp3')

main()