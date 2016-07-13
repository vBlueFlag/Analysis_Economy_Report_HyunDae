#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
extract_nate_news_articles.py

네이트 뉴스 기사 HTML에서 순수 텍스트 기사를 추출한다.

사용법
------
$ python[3] extract_nate_news_articles.py

참고
----
1. HTML 파일 이름을 입력 받는다.
2. 텍스트 기사 파일 이름을 입력 받는다.
3. HTML 기사 파일을 연다.
4. 텍스트 기사 파일을 생성한다.
5. 다음의 동작을 반복한다.
    5-1. HTML 파일에서 HTML 기사 하나를 읽는다.
    5-2. 읽은 HTML 기사가 빈 문자열이면 반복을 멈춘다.
    5-3. HTML 기사에서 제목을 추출한다.
    5-4. HTML 기사에서 기사 작성 날짜/시간을 추출한다.
    5-5. HTML 기사에서 HTML을 제거하고 본문을 추출한다.
    5-6. 텍스트 기사 파일에, 제목, 날짜/시간, 본문을 기록한다.
6. 텍스트 기사 파일을 닫는다.
7. HTML 기사 파일을 닫는다.
"""

import bs4
import re
import time

## 성공했다. 오케이 이 코드를 기반으로 이제 모든 것들을 크롤링해서 데이터를 정련할 수 있을 것 같다! 아자~~
ARTICLE_DELIMITER = "@@@@@ ARTICLE DELIMITER @@@@@\n"
TITLE_START_PAT = u"<!-- 개행 문자 -->"
TITLE_END_PAT = "</span>"
DATE_TIME = u"<dt>작성일</dt>\n\n\t\t\t\t<dd>(.*?)</dd>" #찾기가 너무 복잡해서 정규표현식으로 찾을거다
BODY_START_PAT = u"<!-- AS-IS 이관 시점(20121217) 기준으로 스마트 에디터 개행 처리 이슈 -->"
BODY_END_PAT = u"</SPAN></STRONG></SPAN></P></div>"
TIDYUP_START_PAT = "//<![CDATA["


def get_html_file_name():
    """
    사용자로부터 HTML 파일 이름을 입력받아 돌려준다.

    반환값
    ------
    html_file_name : string
        HTML 파일의 이름
    """

    html_file_name = "article_urls_160530_output.txt" #input("Enter HTML file name: ")

    return html_file_name


def get_text_file_name():
    """
    사용자로부터 텍스트 파일 이름을 입력받아 돌려준다.

    반환값
    ------
    text_file_name : string
        텍스트 파일의 이름
    """

    text_file_name = "article_result.txt"#input("Enter text file name: ")

    return text_file_name


def open_html_file(html_file_name):
    """
    HTML 기사 파일을 열어서 파일 객체를 돌려준다.

    인자
    ----
    html_file_name : string
        HTML 파일의 이름

    반환값
    ------
    html_file : file
        HTML 파일 객체
    """

    html_file = open(html_file_name, "r", encoding="utf-8")

    return html_file


def create_text_file(text_file_name):
    """
    텍스트 기사 파일을 만들어 파일 객체를 돌려준다.

    인자
    ----
    text_file_name : string
        텍스트 파일의 이름

    반환값
    ------
    text_file : string
        텍스트 파일 객체
    """

    text_file = open(text_file_name, "w", encoding="utf-8")

    return text_file


def read_html_article(html_file):
    """
    HTML 파일에서 기사 하나를 읽어서 돌려준다.

    인자
    ----
    html_file : file
        HTML 파일 객체

    반환값
    ------
    html_text : string
        단일 HTML 기사 문자열

    참고
    ----
    HTML 파일에서 더 이상 읽을 줄이 없으면 None을 돌려준다.
    """

    lines = []

    for line in html_file:
        if line.startswith(ARTICLE_DELIMITER):
            html_text = "".join(lines).strip()
            return html_text

        lines.append(line)

    return None


def ext_title(html_text):
    """
    HTML 기사에서 제목을 추출하여 돌려준다.

    인자
    ----
    html_text : string
        단일 기사 HTML 텍스트

    반환값
    ------
    title : string
        추출한 기사 제목
    """

    p = html_text.find(TITLE_START_PAT)
    q = html_text.find(TITLE_END_PAT)
    title = html_text[p + len(TITLE_START_PAT):q]
    title = title.strip()

    return title


def ext_date_time(html_text):
    """
    HTML 기사에서 날짜와 시간을 추출하여 돌려준다.

    인자
    ----
    html_text : string
        단일 기사 HTML 텍스트

    반환값
    ------
    date_time : string
        날짜, 시간 문자열
    """
    rx_sequence=re.compile(DATE_TIME,re.MULTILINE)

    for match in rx_sequence.finditer(html_text):
        date_time = match.group(1)
        date_time = date_time.strip()
    return date_time


def strip_html(html_body):
    """
    HTML 본문에서 HTML 태그를 제거하고 돌려준다.

    인자
    ----
    html_body : string
        HTML 본문 문자열

    반환값
    ------
    body : string
        HTML 태그가 제거된 순수 본문 텍스트

    참고
    ----
    HTML 태그 제거에 BeautifulSoup 모듈을 이용한다.
    """

    page = bs4.BeautifulSoup(html_body, "html.parser")
    body = page.text

    return body


def tidyup(body):
    """
    본문에서 필요없는 부분을 자르고 돌려준다.

    인자
    ----
    body : string
        본문 텍스트

    반환값
    ------
    body : string
        쓸모 없는 부분을 자른 본문 텍스트
    """

    p = body.find(TIDYUP_START_PAT)
    body = body[:p]
    body = body.strip()

    return body


def ext_body(html_text):
    """
    HTML 기사에서 본문을 추출하여 돌려준다.

    인자
    ----
    html_text : string
        단일 기사 HTML 텍스트

    반환값
    ------
    body : string
        본문 텍스트
    """

    p = html_text.find(BODY_START_PAT)
    q = html_text.find(BODY_END_PAT)
    html_body = html_text[p + len(BODY_START_PAT):q]
    html_body = html_body.replace("<br />", "\n")
    html_body = html_body.strip()
    body = strip_html(html_body)
    body = tidyup(body)

    return body


def write_article(text_file, title, date_time, body):
    """
    텍스트 파일에 항목이 구분된 기사를 출력한다.

    인자
    ----
    text_file : file
        텍스트 파일 객체
    title : string
        기사 제목
    date_time : string
        기사 작성 날짜, 시간
    body : string
        기사 본문
    """

    text_file.write("{}\n".format(title))
    text_file.write("{}\n".format(date_time))
    text_file.write("{}\n".format(body))
    text_file.write(ARTICLE_DELIMITER)


def main():
    """
    네이트 뉴스 기사 HTML에서 순수 텍스트 기사를 추출한다.
    """

    html_file_name = get_html_file_name()
    text_file_name = get_text_file_name()
    html_file = open_html_file(html_file_name)
    text_file = create_text_file(text_file_name)

    start_time = time.time()
    print("Start! now.." + str(start_time))

    while True:
        html_text = read_html_article(html_file)

        if not html_text:
            break

        title = ext_title(html_text)
        date_time = ext_date_time(html_text)
        body = ext_body(html_text)
        write_article(text_file, title,date_time, body)

    end_time = time.time()
    print(end_time-start_time)

    html_file.close()
    text_file.close()

main()
