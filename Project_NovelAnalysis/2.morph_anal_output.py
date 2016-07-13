#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
morph_anal_output.py

형태소 분석 결과를 반정형 텍스트 형식으로 저장한다.

"""

from konlpy.tag import Komoran
import ujson

import os
inputfileList = []
outputFileList = []
inputFolder = 'Project_NovelAnalysis/ready/'
outputFolder = 'Project_NovelAnalysis/morphed/'

if not os.path.isdir(outputFolder): # 결과 출력 폴더가 없다면
    os.mkdir(outputFolder)  # 폴더를 만든다

for root, dirs, files in os.walk(inputFolder): # 입력 폴더에서 파일리스트를 받아
    for file in files:
        inputfileList.append(root + file) # 리스트로 만든다.
        outputFileList.append( outputFolder + file)

#FILE_NAME = { 'input' : "Project_NovelAnalysis/txt/arirang_01.txt", # 형태소 분석할 파일,
#             'output' : "Project_NovelAnalysis/txt/counted_arirang_01.txt" # 형태소 분석이 완료된 파일
#    }

def split_sentences(text):
    """
    입력 문자열을 문장들의 리스트로 만들어 돌려준다.

    인자
    ----
    src : string
        입력 문자열

    반환값
    ------
    sentences : list
        문장의 리스트. 각 문장은 문자열이다.

    참고
    ----
    마침표(.), 물음표(?), 느낌표(!)에 이어서 공백 문자가 있으면 문장을 나눈다.
    """

    new_text = \
        text.replace(". ", ".\n").replace("? ", "?\n").replace("! ", "!\n")
    sentences = new_text.splitlines()

    return sentences


def get_morph_anal(analyzer, text):
    """
    주어진 텍스트에 대해 형태소 분석을 수행하여 결과를 돌려준다.

    인자
    ----
    analyzer : KoNLPy morphological analyzer class instance
        형태소 분석기 객체

    text : string
        입력 문자열

    반환값
    ------
    morph_anal : list
        형태소 분석 결과를 담고 있는 리스트
    """

    morph_anal = analyzer.pos(text, flatten=False)

    return morph_anal


def print_morph_anal(text, morph_anal):
    """
    형태소 분석 결과를 출력한다.

    인자
    ----
    text : string
        입력 문자열

    morph_anal : list
        형태소 분석 결과를 담고 있는 리스트

    output_format : string
        출력 형식을 문자열로 지정한다.
        "vert" : 세로형
        "hori" : 가로형
        "json" : JSON 형식
    """

    output = get_json_output(text, morph_anal)

    return output


def get_json_output(text, morph_anal):
    """
    입력 텍스트와 이에 대한 형태소 분석 결과를 JSON 형식의 문자열로 만든다.

    인자
    ----
    text : string
        입력 문자열

    morph_anal : list
        형태소 분석 결과

    반환값
    ------
    output : string
        JSON 형식의 출력 문자열
    """

    outputObj = {
        "text": text,
        "morphAnal": morph_anal
    }
    output = ujson.dumps(outputObj, ensure_ascii=False)

    return output


def main():
    """형태소 분석 결과를 json 형식의 딕셔너리로 저장한다.
    { ‘morphAnal’ : [ 한 문장 [ 한 어절 [ ‘형태소’ , ‘형태소 약어’] ] ],
      ‘text’ : ‘전체 문장’ }
    """

    komoran = Komoran()
    result = ""
    for i in range(len(inputfileList)):
        f = open(inputfileList[i],'r') 
        w = open(outputFileList[i],'w')
        for line in f:
            sentences = split_sentences(line)
            for sentence in sentences:
                morph_anal = get_morph_anal(komoran, sentence)
                result = print_morph_anal(sentence, morph_anal)

                w.write(result+'\n')
    f.close()
    w.close()   

    # 아무리봐도 encoding='utf-8'으로 해야할 이유가 없어.
    #s = open(FILE_NAME['output'], 'w', encoding='utf-8')
    #with open(FILE_NAME['input'], "r", encoding="utf-8") as f:
    #    for line in f:
    #        sentences = split_sentences(line)
    #        for sentence in sentences:
    #            morph_anal = get_morph_anal(komoran, sentence)

    #            result = print_morph_anal(sentence, morph_anal)

    #            s.write(result+'\n')
    #s.close();

main()
