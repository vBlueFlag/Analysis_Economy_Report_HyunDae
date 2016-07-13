''' 1. 파일리스트를 해당 폴더에서 모두 받아 리스트로 저장한다.
    2. 기존 ansi 파일을 utf-8으로 바꾸어 해당 파일들을 하나하나 연다.
    3. 텍스트의 줄바꿈(\n)을 제거한다.
    4. 그리고 새로운 폴더(ready)를 만들어 모두 저장한다.
'''

import os
from pprint import pprint
import requests
import urllib.request

inputfileList = []
outputFileList = []
inputFolder = 'HyundaeEconomy/txt/'
outputFolder = 'HyundaeEconomy/ready/'

if not os.path.isdir(outputFolder): # 결과 출력 폴더가 없다면
    os.mkdir(outputFolder)  # 폴더를 만든다

for root, dirs, files in os.walk(inputFolder): # 입력 폴더에서 파일리스트를 받아
    for file in files:
        inputfileList.append(root + file) # 리스트로 만든다.
        outputFileList.append( outputFolder + file)

def exe(i):
    f = open(inputfileList[i],'r', encoding="utf-8")
    w = open(outputFileList[i],'w', encoding="utf-8")

    lines = f.readlines()
    replace_text = reFile.readlines()
    for line in lines:
        line = line.replace("------------------------- Converted by Unregistered Simpo PDF Converter -------------------------"," ")
        line = line.replace("\0"," ") #문서를 잘 보면 null문자가 곳곳에 들어가 있다. 아주 악질이야.
        line = line.replace("\n"," ")

        w.write(line.strip())
    #result = full.replace("\n","")
    #result = str(result)
    
    print("ready...%s" % inputfileList[i]) 
    w.close() 
    f.close()

for i in range(len(inputfileList)):
    try:
        exe(i)
    except:
        i = i+1
  

