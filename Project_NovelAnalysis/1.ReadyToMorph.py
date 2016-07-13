''' 1. 파일리스트를 해당 폴더에서 모두 받아 리스트로 저장한다.
    2. 기존 ansi 파일을 utf-8으로 바꾸어 해당 파일들을 하나하나 연다.
    3. 텍스트의 줄바꿈(\n)을 제거한다.
    4. 그리고 새로운 폴더(ready)를 만들어 같은 이름으로 12권 모두 저장한다.
'''

import os
from pprint import pprint
inputfileList = []
outputFileList = []
inputFolder = 'Project_NovelAnalysis/txt/'
outputFolder = 'Project_NovelAnalysis/ready/'

if not os.path.isdir(outputFolder): # 결과 출력 폴더가 없다면
    os.mkdir(outputFolder)  # 폴더를 만든다

for root, dirs, files in os.walk(inputFolder): # 입력 폴더에서 파일리스트를 받아
    for file in files:
        inputfileList.append(root + file) # 리스트로 만든다.
        outputFileList.append( outputFolder + file)

pprint(inputfileList)
pprint(outputFileList)

for i in range(len(inputfileList)):
    f = open(inputfileList[i],'r')
    w = open(outputFileList[i],'w')
    lines = f.readlines()
    result = list(map(lambda lines:lines.replace("\n",""),lines));
    w.write(str(result))
    f.close()
    w.close()   
    

