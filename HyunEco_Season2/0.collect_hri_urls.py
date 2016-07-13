#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
1.collect_hri_urls.py

현대 경제 연구원의 보고서들을 모두 크롤링한다.

참고
----
1. 수집 대상 날짜를 입력 받는다.
2. 출력 파일을 생성한다.
3. 페이지 번호를 1에서부터 1씩 증가시키며 아래 동작을 반복한다.
    3-1. 인덱스 페이지에 접근하여 HTML을 읽어온다.
    3-2. 페이징이 끝나면 반복을 멈춘다.
    3-3. 기사 링크에서 URL들을 추출한다.
    3-4. 추출한 기사 URL들을 출력 파일에 쓴다.
    3-5. 2초 동안 쉰다.
4. 출력 파일을 닫는다.
"""

import time
import re
import urllib.parse
import urllib.request
import math
import os
import ujson

import winsound # 크롤링이 다 끝나면 노래를 연주한다.

folder = False
pageNum = 4
def get_html(page_num):

    #page_url = "http://hri.co.kr/storage/newReList.asp" # 최신보고서 게시판 주소
    page_url = "http://hri.co.kr/board/reportList.asp" # 경제 보고서 게시판 주소

    #넘겨줘야 하는 post방식 중에서도 urlencode 스타일이라 아래와 같이 만들어 준 후
    payload = urllib.parse.urlencode({'numIdx': '', 
               'skin': '', 
               'mode': '', 
               'GotoPage': page_num,
               'column':'',
               'keyword':'',
               'firstDepth':'1',
               'secondDepth':pageNum,
               'thirdDepth':'',
               'fourthDepth':'',
               'boardid':'1,2,8,38,125,126,127,128,129,5,132',
               'sortby':''})

    #이것을 다시 euc-kr로 인코딩해야만 제대로 들어간다. 
    payload = payload.encode('euc-kr')
    url = urllib.request.Request(page_url, payload)
    url.add_header("User-Agent","Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.29 Safari/525.13")

    response = urllib.request.urlopen(url)
    response = response.read()
    html = response.decode('euc-kr', 'ignore') #euc-kr의 경우 꼭 이렇게 디코딩을 해야만 정상적으로 들어간다. 'ignore'는 없어도 되는데 아마 에러 발생을 무시하라는 것 같아 계속 넣어놓는다.

    return html

def paging_done(html):
    """
    페이징이 완료되었는지를 판단한다.
    """

    done_pat = u"해당 자료가 없습니다" #u는 유니코드란 뜻

    if done_pat in html:
        return True

    return False


def ext_pageInfo(html,pageInfo):
    """
    주어진 HTML에서 원하는 정보(numIdx, GotoPage)들만 추려내어 리턴한다.

    """

    numIdx = re.findall('보고서로 이동\"><a href=\"javascript:goToPageNew\(\'(.*?)\'',html)
    #GotoPage = re.findall('\'/storage/newReView.asp\',\'1\',\'0\',\'\',\'\',\'\',\'(.*?)\'',html) #최신 보고서 정규식
    GotoPage = re.findall('\'/board/reportView.asp\',\'1\',\'4\',\'\',\'\',\'\',\'(.*?)\'',html)

    for i in range(len(numIdx)):
        if re.search(numIdx[i],str(pageInfo)): # 이미 있는 numIdx라면 새로 추가하지 않는다
            continue
        pageInfo.append({'numIdx' : numIdx[i], 'GotoPage' : GotoPage[i]})

    return pageInfo


def get_fileList(numIdx,GotoPage):

    #page_url = "http://hri.co.kr/storage/newReView.asp" #최신 보고서 상세페이지 주소
    page_url = "http://hri.co.kr/board/reportView.asp" #경제 보고서 상세페이지 주소

    payload = urllib.parse.urlencode({'numIdx': numIdx, 
                'skin': '', 
                'mode': '', 
                'GotoPage': GotoPage,
                'column':'',
                'keyword':'',
                'firstDepth':'1',
                'secondDepth':pageNum,
                'thirdDepth':'',
                'fourthDepth':'',
                'boardid':'1,2,8,38,125,126,127,128,129,5,132',
                'sortby':''})

    #이것을 다시 euc-kr로 인코딩해야만 제대로 들어간다. 
    payload = payload.encode('euc-kr')
    url = urllib.request.Request(page_url, payload)
    url.add_header("User-Agent","Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.29 Safari/525.13")

    response = urllib.request.urlopen(url)
    response = response.read()
    html = response.decode('euc-kr', 'ignore') #euc-kr의 경우 꼭 이렇게 디코딩을 해야만 정상적으로 들어간다. 'ignore'는 없어도 되는데 아마 에러 발생을 무시하라는 것 같아 계속 넣어놓는다.

    return html


def ext_informPDF(html,i):
    """
    주어진 HTML에서 원하는 정보(numIdx, GotoPage)들만 추려내어 리턴한다.

    """
    reportInfo ={}
    
    try:
        titleID = "class=\"heading\">(.*?)<" #이런 거지같은ㅡ,ㅡ
        rx_sequence=re.compile(titleID,re.MULTILINE) #제목을 뽑아내기 위해 멀티라인 정규표현식 사용
        for match in rx_sequence.finditer(html):
            titleID = match.group(1)
            titleID = titleID.strip()
        dateID = re.search("class=\"li_report01\">(.*?)<",html).group(1)
        whoID = re.search("연구자 : (.*?)<",html).group(1)
        magazineID = re.search("class=\"li_report02\">(.*?)<",html).group(1)
        reportID = re.search("download_attach\(\'/publication/\',\'(.*?)\[",html).group(1)
        reportURL = "https://hri.co.kr:442/download.asp?file_path=%2Fpublication%2F&file_name="+ urllib.parse.quote_plus(reportID) + "%5B1%5D.pdf"
    except:

        titleID = "TitlelessReport"
        dateID = "Dateless"
        whoID = "Nobody"
        magazineID = "Nowhere"
        reportURL ="https://hri.co.kr:442/download.asp?file_path=%2Fpublication%2F&file_name=2016620161013%5B1%5D.pdf"
    
    fileName = dateID + '[' + str(i) +'].pdf' #이렇게 파일이름까지 모두 만들어서 넘겨준다
    reportInfo ={ 'fileNum' : i, 'titleID' : titleID, 'dateID' : dateID, 'whoID' : whoID, 'fileName' : fileName, 'reportURL' : reportURL , 'magazineID' : magazineID}

    return reportInfo

def folderCheck(): #pdf폴더 만들기
    global folder

    if folder == False:
        outputFolder = 'HyundaeEconomy/pdfs'
        if not os.path.isdir(outputFolder): # 결과 출력 폴더가 없다면
            os.mkdir(outputFolder)  # 폴더를 만든다
        os.chdir(outputFolder) #해당 폴더로 이동한다
        folder = True;

def savePDF(reportInfo):

    #reportURL로 가서 파일을 가져온다.
    urllib.request.urlretrieve(reportInfo['reportURL'], reportInfo['fileName'])

def main():
    """
    현대 경제 연구원의 모든 보고서 pdf 파일들을 긁어온다.
    """

    # 1. 보고서 페이지 전체를 돌며 상세 페이지 접속에 필요한 [numIdx, GotoPage] 값을 리스트로 받아온다.
    pageInfo = []
    start_time = time.time() 
    print("Start! now.." + str(start_time))
    w = open("HyundaeEconomy/crawling_infomation.txt", 'w')

    page_num = 1 # 첫페이지부터 크롤링해라.

    i = 0;
    while True:
        html = get_html(page_num)
        pageInfo = ext_pageInfo(html,pageInfo)
        i = i+ 1
        if paging_done(html):
            break
        print("crawling... %d" %(i) )
        page_num += 1

        #time.sleep(1)
    ujson.dump(pageInfo,w)
    w.close()
    end_time = time.time()
    print("1. spending time : %d min. %.2f sec." % (math.floor((end_time - start_time)/ 60) , (end_time - start_time)% 60))


    #2. 받아온 [numIdx, GotoPage]를 이용해 해당 페이지에 접속하여 pdf 첨부파일 주소를 만든 후 모두 가져온다.
    try:
        start_time = time.time() 
        print("Start! now.." + str(start_time))
        f = open("HyundaeEconomy/crawling_infomation.txt", 'r')
        folderCheck()
        w = open("report_infomation.txt", 'a') #리포트에 대한 정리 문서
        reportInfoList = []
        information= ujson.load(f)

        for i in range(1000):#len(information)):  #특정 번호의 리포트부터 가져오고 싶을 때는 range(번호,len(information)) 로 바꾼다.
            html = get_fileList(information[i]['numIdx'],information[i]['GotoPage']) #json으로 넘겨주어 html을 받아오고
            reportInfo = ext_informPDF(html,i) #그 html에서 리포트에 대한 모든 정보를 뽑아낸 후
            #reportInfoList.append(reportInfo) #먼저 리스트에 정보를 추가하고 #그러고 보니 이걸 할 필요가 없잖아.
            reportfile = ujson.dumps(reportInfo, ensure_ascii=False,indent = 4)
            w.write(reportfile)
            savePDF(reportInfo) #저장하다.
            print("saving... %d / %d" % (i,len(information)-1))
            #time.sleep(2)

        #reportfile = ujson.dumps(reportInfoList, ensure_ascii=False) # 리스트 정보를 한글 정보가 포함된 json 파일로 저장한다.
        #w.write(reportfile) #중간에 세션이 끊어지는 경우가 있어 json파일을 먼저 저장하고 파일저장은 주석처리했다가 다시 반대로 해서 작업한다.
        w.close()
        f.close()
    
        end_time = time.time()
        print("2. spending time : %d min. %.2f sec." % (math.floor((end_time - start_time)/ 60) , (end_time - start_time)% 60))
        
    except:
        pass
    winsound.PlaySound('MyWay.wav', winsound.SND_FILENAME)  
      

main()
