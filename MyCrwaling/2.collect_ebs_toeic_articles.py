#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
collect_nate_news_articles.py

김대균 토익 킹 문서를 몽땅 읽어온다.

사용법
------
$ python[3] collect_nate_news_articles.py

참고
----
1. URL 목록 파일명을 입력 받는다.
2. 출력 파일명을 입력 받는다.
2. 기사 URL 파일을 연다.
3. 출력 파일을 생성한다.
4. 기사 URL 파일을 한 줄씩 읽으며 더 읽을 내용일 없을 때까지 다음을 반복한다.
    4-1. 읽은 줄에서 기사 번호를 추출하여 인쇄용 URL을 만든다.
    4-2. 인쇄용 URL로 기사에 접근하여 HTML을 얻는다.
    4-3. 얻어온 HTML을 기사 파일에 기록한다.
    4-4. 2초 동안 쉰다.
5. 출력 파일을 닫는다.
6. URL 목록 파일을 닫는다.
"""

import time
import requests

fileName = "article_urls_160530"

def get_url_file_name(fileName):
    """
    URL 파일 이름을 입력 받아 돌려준다.

    반환값
    ------
    url_file_name : string
        읽어들일 URL을 포함하고 있는 파일의 이름
    """

    url_file_name = fileName #input("Enter url file name: ")

    return url_file_name + ".txt"


def get_output_file_name(fileName):
    """
    출력 파일 이름을 입력 받아 돌려준다.

    반환값
    ------
    output_file_name : string
        생성할 출력 파일의 이름
    """

    output_file_name = fileName #input("Enter output file name: ")

    return output_file_name+"_output.txt"


def open_url_file(url_file_name):
    """
    URL 파일을 연다.

    인자
    ----
    url_file_name : string
        읽어들일 URL 파일의 이름

    반환값
    ------
    url_file : file
        읽어들일 URL 파일 객체
    """

    url_file = open(url_file_name, "r", encoding="utf-8")

    return url_file


def create_output_file(output_file_name):
    """
    출력 파일을 생성한다.

    인자
    ----
    output_file_name : string
        출력 파일의 이름

    반환값
    ------
    output_file : file
        출력 파일 객체
    """

    output_file = open(output_file_name, "w", encoding="utf-8")

    return output_file


def gen_print_url(url_line):
    """
    주어진 링크 URL로부터 Post용 인자를 뽑아 객체로 전달한다.

    인자
    ----
    url_line : string
        파일로부터 읽어들인 기사 URL 라인

    반환값
    ------
    print_url : string
        인쇄용 페이지 URL

    참고
    ----
    EBS 게시판은 post 방식으로 만들어져 있다.
    그리고 post인자는 이름이 frm이라고 하는 form태그 안에 input 태그의 name 값으로 숨겨져 있다.
    이것과 해당 주소를 비교하여 주소 중에 해당 post인자들을 찾아서 pstId와 bbsId를 추출하면 된다.
    http://home.ebs.co.kr/toeic/board/23/10052166/view/10007124792?c.page=1&hmpMnuId=101&amp;searchKeywordValue=0&amp;bbsId=10052166&amp;fileClsCd=ANY&amp;searchKeyword=&amp;searchCondition=&amp;searchConditionValue=0&amp; 에서
    만 잘라낸다.
    """
    p = url_line.find("/view/")
    q = url_line.find("?")
    pstId = url_line[p+6 : q]

    p = url_line.find("/23/")
    q = url_line.find("/view/")
    bbsId = url_line[p+4 : q]
    '''
    requests.post() 작업 시작
    '''
    user_agent = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 " + \
        "(KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
    headers = {
        "User-Agent": user_agent
    }
    payload = {'pstId': pstId, 'bbsId': bbsId, 'hmpId': 'toeic', 'boardType': '2' }        
    
    return payload


def get_html(post_factor):
    """
    주어진 인쇄용 URL에 접근하여 HTML을 읽어서 돌려준다.

    인자
    ----
    print_url : string
        인쇄 페이지 URL

    반환값
    ----
    html : string
        기사를 포함하고 있는 HTML 문자열
    """


    
    response= requests.post("http://home.ebs.co.kr/toeic/board/23/10052166/popupPrnt",data = post_factor)

    html = response.text
    return html


def write_html(output_file, html):
    """
    주어진 HTML 텍스트를 출력 파일에 쓴다.

    인자
    ----
    output_file : file
        출력 파일 객체

    html : string
        기사를 포함하고 있는 HTML 문자열

    참고
    ----
    기사 한 건을 출력한 뒤 기사 구분자를 덧붙여 기록한다.
    """

    output_file.write("{}\n".format(html))
    output_file.write("@@@@@ ARTICLE DELIMITER @@@@@\n")


def pause():
    """
    1초 동안 쉰다.
    """

    time.sleep(2)


def close_output_file(output_file):
    """
    출력 파일을 닫는다.

    인자
    ----
    output_file : file
        출력 파일 객체
    """

    output_file.close()


def close_url_file(url_file):
    """
    URL 파일을 닫는다.

    인자
    ----
    url_file : file
        URL 파일 객체
    """

    url_file.close()


def main():
    """
    네이트 뉴스 기사를 수집한다.

    참고
    ----
    사용자로부터 기사 URL 파일 이름과 출력 파일의 이름을 입력받는다.
    """

    url_file_name = get_url_file_name(fileName)
    output_file_name = get_output_file_name(fileName)

    url_file = open_url_file(url_file_name)
    output_file = create_output_file(output_file_name)

    start_time = time.time()
    print("Start! now.." + str(start_time))

    for line in url_file:
        post_factor = gen_print_url(line)
        html = get_html(post_factor)
        write_html(output_file, html)

    close_output_file(output_file)
    close_url_file(url_file)
    
    end_time = time.time()
    print(end_time-start_time)

main()
