#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
collect_nate_economy_news_urls.py

네이트 경제 뉴스 기사 URL을 수집한다.

사용법
------
$ python[3] collect_nate_economy_news_urls.py

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
import requests

fileName = "160530"

def get_date(fileName):
    """
    나의 첫 크롤링 : 김대균 토익 킹(http://home.ebs.co.kr/toeic/board/)

    반환값
    ------
    날짜는 단지 참고용으로 크롤링 날짜를 코드에 직접 입력했다.
    """

    target_date = fileName

    return target_date


def create_output_file(target_date):
    """
    출력 파일을 생성하고 파일 객체를 돌려준다.

    인자
    ----
    target_date : string
        기사 수집 대상 날짜 (YYYYMMDD)

    반환값
    ------
    output_file : file
        출력 파일 객체

    참고
    ----
    문자열 연산에 의해 출력 파일 이름을 생성한다.
    """

    output_file_name = "article_urls_" + target_date + ".txt"
    output_file = open(output_file_name, "w", encoding="utf-8")

    return output_file


def get_html(target_date, page_num):
    """
    주어진 날짜와 페이지 번호에 해당하는 페이지 URL에 접근하여 HTML을 돌려준다.
    참고 : 김대균 토익에는 페이지 번호만 들어가 있다.

    인자
    ----------
    target_date : string
        크롤링 데이터 수집 날짜

    page_num : int
        페이지 번호

    반환값
    -------
    html : string
        기사를 포함하고 있는 HTML 문자열

    참고
    ----
    인자로 주어진 페이지 번호를 이용하여 URL을 생성하고 이 URL에 접근하여
    HTML 문자열을 가져온다. Requests 모듈의 `get()` 메소드를 이용하며 User-Agent를
    요청 헤더에 지정한다.

    """

    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) " + \
        "AppleWebKit/537.36 (KHTML, like Gecko) " + \
        "Chrome/37.0.2062.94 Safari/537.36"
    headers = {"User-Agent": user_agent}

    page_url = "http://home.ebs.co.kr/toeic/board/23/10052166/list?c.page=" + \
        str(page_num) + "&hmpMnuId=101&searchKeywordValue=0&bbsId=10052166&fileClsCd=ANY&searchKeyword=&searchCondition=&searchConditionValue=0&"

    response = requests.get(page_url, headers=headers) #requests와 get메서드는 알아보자.
    html = response.text

    return html


def paging_done(html):
    """
    페이징이 완료되었는지를 판단한다.

    반환값
    ------
    bool
        페이징이 완료되었으면 True를, 그렇지 않았으면 False를 반환한다.

    참고
    ----
    페이징이 완료되었음을 판단할 수 있는 문자열의 포함 여부로 페이징의 완료 여부를 판단한다.
    """

    done_pat = u"작성된 게시물이 없습니다." #u는 유니코드란 뜻

    if done_pat in html:
        return True

    return False


def ext_news_article_urls(html):
    """
    주어진 HTML에서 게시판 URL을 추출하여 돌려준다.

    인자
    ----
    html : string
        기사 인덱스 페이지 HTML

    반환값
    ------
    news_article_urls : list
        HTML에서 추출한 기사 URL의 리스트

    참고
    ----
    HTML에서 정규표현을 이용하여 개별 기사로의 링크 URL을 추출한다.
    """

    url_frags = re.findall('<a href="(.*?)"', html)
    news_article_urls = []

    for url_frag in url_frags:
        if not url_frag.startswith("/toeic/board/23/10052166/view/"):
            continue

        url = "http://home.ebs.co.kr" + url_frag
        news_article_urls.append(url)

    return news_article_urls


def write_news_article_urls(output_file, urls):
    """
    기사 URL들을 출력 파일에 기록한다.

    인자
    ----
    output_file : file
        출력 파일 객체

    urls : list
        기사 URL들을 포함하고 있는 리스트
    """

    for url in urls:
        print(url, file=output_file)


def pause():
    """
    2초 동안 쉰다.
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


def main():
    """
    김대균 토익킹의 텍스트 문서들을 모두 수집한다.
    """

    target_date = get_date(fileName)
    output_file = create_output_file(target_date)
    page_num = 1

    start_time = time.time()
    print("Start! now.." + str(start_time))

    while True:
        html = get_html(target_date, page_num)

        if paging_done(html):
            break

        urls = ext_news_article_urls(html)
        write_news_article_urls(output_file, urls)
        page_num += 1
        pause()

    close_output_file(output_file)

    end_time = time.time()
    print(end_time - start_time)


main()
