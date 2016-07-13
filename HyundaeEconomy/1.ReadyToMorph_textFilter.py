#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

보고서명(MagazineID)과 저자명(whoID)를 보고서안에서 모두 제거한다

"""

import os
from pprint import pprint
import requests
import urllib.request

inputfileList = []
outputFileList = []
inputFolder = 'HyundaeEconomy/ready/'
outputFolder = 'HyundaeEconomy/upgraded_ready/'
replaceFile = 'HyundaeEconomy/replace_text.txt'

if not os.path.isdir(outputFolder): # 결과 출력 폴더가 없다면
    os.mkdir(outputFolder)  # 폴더를 만든다

for root, dirs, files in os.walk(inputFolder): # 입력 폴더에서 파일리스트를 받아
    for file in files:
        inputfileList.append(root + file) # 리스트로 만든다.
        outputFileList.append( outputFolder + file)

def exe(i):
    f = open(inputfileList[i],'r', encoding="utf-8")
    reFile = open(replaceFile, 'r', encoding="utf-8")
    w = open(outputFileList[i],'w', encoding="utf-8")

    lines = f.readlines()
    reTexts = reFile.readlines()
    for line in lines:
        for reText in reTexts:
            line = line.replace(reText.strip(),"")

        w.write(line)
    #result = full.replace("\n","")
    #result = str(result)
    
    print("ready...%s" % inputfileList[i]) 
    reFile.close()
    w.close() 
    f.close()

for i in range(len(inputfileList)):
    try:
        exe(i)
    except:
        i = i+1
  

