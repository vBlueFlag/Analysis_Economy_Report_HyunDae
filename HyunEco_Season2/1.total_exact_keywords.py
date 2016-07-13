#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
현대경제연구원 보고서 쿨백라이블러 발산 (Kullback–Leibler divergence) 분석
모든 MagazineID를 기준으로 키워드 분석. 
"""

import sys
import os.path
from collections import Counter
import math
import ujson

''' 모든 카테고리(MagazineID)를 출력'''

Subject_KEY = "magazineID"
MagazinID_MAP = { # 이건 지금 할 필요가 없지만 혹시 필터 처리가 필요할지 몰라 넣어놓는다.
    "VIP Report": "VIP Report", # vip
    "한국경제주평" : "한국경제주평", #korea
    "이슈리포트" : "이슈리포트", #issue
    "연금시장리뷰" :"연금시장리뷰", #pension
    "Chairperson Note" : "Chairperson Note", #chair
    "통일경제" : "통일경제", #unity
    "지식경제" : "지식경제" #knowledge
}
FEATURE_POSES = ["NNG"]


def get_subj_morph_counts(input_file_name):
    """
    면종별 형태소 빈도를 계수한다.

    인자
    ----
    input_file_name : string
        입력 파일 이름

    all_morphs : set
        신문 기사 말뭉치에 포함된 모든 형태소를 담고 있는 세트 객체
    """

    vip_morph_counts = Counter()
    korea_morph_counts = Counter()
    issue_morph_counts = Counter()
    pension_morph_counts = Counter()
    chair_morph_counts = Counter()
    unity_morph_counts = Counter()
    knowledge_morph_counts = Counter()
    all_morphs = set()
    information = []
    subjs_counts = {}

    vip_num = 0
    korea_num = 0
    issue_num = 0
    pension_num = 0
    chair_num = 0
    unity_num = 0
    knowledge_num = 0
    all_num = 0

    with open(input_file_name, 'r', encoding='utf-8') as f:
        information = ujson.load(f)
        for i in range(len(information)):
            subj_code = information[i][Subject_KEY]
            if subj_code == "Nowhere": #이건 pass!
                continue
            subj = MagazinID_MAP[subj_code]

            morphed_file = "HyunEco_Season2/morphed/" + information[i]['morphedName']
            try:
                with open(morphed_file, 'r', encoding='utf-8') as morphedReport:
                    morphedText = ujson.load(morphedReport)
                    morphs = []
                    for j in range(len(morphedText)):
                        morphs = ext_morphs(morphedText[j]['morphAnal'],morphs) #이렇게 해도 문제는 없겠다
                    
                    if subj == "VIP Report":
                        vip_num = vip_num +1 
                        vip_morph_counts.update(morphs)
                    elif subj == "한국경제주평":
                        korea_num = korea_num +1
                        korea_morph_counts.update(morphs)
                    elif subj == "이슈리포트":
                        issue_num = issue_num + 1
                        issue_morph_counts.update(morphs)
                    elif subj == "연금시장리뷰":
                        pension_num = pension_num +1
                        pension_morph_counts.update(morphs)
                    elif subj == "Chairperson Note":
                        chair_num = chair_num+1
                        chair_morph_counts.update(morphs)
                    elif subj == "통일경제":
                        unity_num = unity_num +1 
                        unity_morph_counts.update(morphs)
                    elif subj == "지식경제":
                        knowledge_num = knowledge_num +1
                        knowledge_morph_counts.update(morphs)
                    all_morphs.update(morphs)
                    all_num = all_num +1 
            except:
                pass

    subjs_counts = { "vip" : vip_morph_counts, "korea" : korea_morph_counts, "issue" : issue_morph_counts,\
                    "pension":pension_morph_counts, "chair":chair_morph_counts, "unity":unity_morph_counts,\
                    "knowledge":knowledge_morph_counts, "all" : all_morphs}
    num_counts = {"vip":vip_num, "korea" : korea_num, "issue" : issue_num,"pension":pension_num,"chair":chair_num,\
                  "unity":unity_num,"knowledge":knowledge_num,"all" : all_num}
    return subjs_counts, num_counts


def ext_morphs(ma_res,morphs): #이때는 처음 json을 깔때라 어설프게 만들었다. 그래도 잘 돌아가니 그대로 둔다.
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
    #for line in ma_res: #안타깝게도 한줄씩 읽어와야 한다. 강사님이 준 엉망(?)의 json형식으로 이미 인코딩을 해버렸기 때문이다.
    #    wordforms = line.strip().split() #다음부터는 꼭 내 스타일로 json을 만들자. 
    # ㅋㅋㅋ 그냥 강사님 문서를 모두 내 스타일로 바꿨다. 개고생,ㅡ 16.07.03

    for word in ma_res:
        #for word in sen:
        for morph_lex, morph_pos in word:
            if morph_pos not in FEATURE_POSES: #지금은 모든 MazagineID를 실험한다
                continue

            morphs.append(morph_lex)

    return morphs


def get_subj_morph_kl_divs(subjs_counts):
    """
    면종별 키워드 KL 발산을 계산한다.

    all_morphs : set
        말뭉치에 포함된 모든 형태소를 담고 있는 세트 객체

    subj_morph_kl_divs : list
        면종, 형태소, KL 발산으로 이루어진 리스트를 원소로 갖는 리스트
    """

    sum_vip_morph_counts = 0
    sum_korea_morph_counts = 0
    sum_issue_morph_counts = 0
    sum_pension_morph_counts = 0
    sum_chair_morph_counts = 0
    sum_unity_morph_counts = 0
    sum_knowledge_morph_counts = 0

    for count in subjs_counts['vip'].values():
        sum_vip_morph_counts += count

    for count in subjs_counts['korea'].values():
        sum_korea_morph_counts += count

    for count in subjs_counts['issue'].values():
        sum_issue_morph_counts += count

    for count in subjs_counts['pension'].values():
        sum_pension_morph_counts += count

    for count in subjs_counts['chair'].values():
        sum_chair_morph_counts += count

    for count in subjs_counts['unity'].values():
        sum_unity_morph_counts += count

    for count in subjs_counts['knowledge'].values():
        sum_knowledge_morph_counts += count

    #드디어 KL발산을 계산한다
    subj_morph_kl_divs = []

    for morph in subjs_counts['all']:
        for subj, morph_counts, sum_morph_counts in zip(["VIP Report","한국경제주평","이슈리포트","연금시장리뷰",\
                                                            "Chairperson Note","통일경제","지식경제" ],
                                         [subjs_counts['vip'],subjs_counts['korea'],subjs_counts['issue'],subjs_counts['pension'],\
                                          subjs_counts['chair'],subjs_counts['unity'],subjs_counts['knowledge']],
                                                        [sum_vip_morph_counts,sum_korea_morph_counts,sum_issue_morph_counts,
                                                         sum_pension_morph_counts,sum_chair_morph_counts,
                                                         sum_unity_morph_counts,sum_knowledge_morph_counts]):
            subj_morph_count = morph_counts[morph]
            subj_morph_prob = subj_morph_count / sum_morph_counts

            vip = subjs_counts['vip'][morph] / sum_vip_morph_counts
            korea = subjs_counts['korea'][morph] / sum_korea_morph_counts
            issue = subjs_counts['issue'][morph] / sum_issue_morph_counts
            pension = subjs_counts['pension'][morph] / sum_pension_morph_counts
            chair = subjs_counts['chair'][morph] / sum_chair_morph_counts
            unity = subjs_counts['unity'][morph] / sum_unity_morph_counts
            knowledge = subjs_counts['knowledge'][morph] / sum_knowledge_morph_counts

            if subj == "VIP Report": # [ korea, vip, issue, pension, chair, unity, knowledge ]
                other_subj_morph_probs = [ korea, issue, pension, chair, unity, knowledge ]

            elif subj == "한국경제주평":
                other_subj_morph_probs = [ vip, issue, pension, chair, unity, knowledge ]

            elif subj == "이슈리포트":
                other_subj_morph_probs = [ korea, vip, pension, chair, unity, knowledge ]

            elif subj == "연금시장리뷰":
                other_subj_morph_probs = [ korea, vip, issue, chair, unity, knowledge ]

            elif subj == "Chairperson Note":
                other_subj_morph_probs = [ korea, vip, issue, pension, unity, knowledge ]

            elif subj == "통일경제":
                other_subj_morph_probs = [ korea, vip, issue, pension, chair, knowledge ]

            elif subj == "지식경제":
                other_subj_morph_probs = [ korea, vip, issue, pension, chair, unity ]

            avg_morph_prob = \
                (subj_morph_prob + sum(other_subj_morph_probs)) / 7

            try:
                kl_div = calc_kl_div(subj_morph_prob, avg_morph_prob)
            except:
                kl_div = 0.0

            subj_morph_kl_divs.append([subj, morph, kl_div])

    return subj_morph_kl_divs


def calc_kl_div(subj_morph_prob, avg_morph_prob):
    """
    KL 발산을 계산한다.

    인자
    ----
    subj_morph_prob : float
        특정 주제에서의 형태소의 발현 확률

    avg_morph_prob: float
        형태소의 평균 발현 확률

    반환값
    ------
    kl_div : float
        계산된 KL 발산
    """

    kl_div = subj_morph_prob * math.log(subj_morph_prob / avg_morph_prob)

    return kl_div


def write_subj_morph_kl_divs(output_file_name, subj_morph_kl_divs):
    """
    면종별 키워드 KL 발산을 출력 파일에 기록한다.

    인자
    ----
    output_file_name : string
        출력 파일 이름

    subj_morph_kl_divs : list
        면종, 형태소, KL 발산으로 이루어진 리스트를 원소로 갖는 리스트
    """

    with open(output_file_name, "w", encoding="utf-8") as output_file: #이건 한번 utf-8로 해보자.
        for output_elems in sorted(subj_morph_kl_divs,
                                   key=get_3rd_elem, reverse=True):
            output_elems = [str(e) for e in output_elems]
            output_file.write("{}\n".format("         \t".join(output_elems)))


def get_3rd_elem(seq):
    """
    주어진 시퀀스의 세 번째 원소를 돌려준다.
    """

    elem = seq[2]
    return elem


def main():

    input_file_name = "HyunEco_Season2/report_infomation.txt"
    output_file_name= "HyunEco_Season2/result_keywords.txt"
    w = open("HyunEco_Season2/keywords_num.txt",'w',encoding="utf-8")
    subjs_counts, num_counts = get_subj_morph_counts(input_file_name)
    subj_morph_kl_divs = get_subj_morph_kl_divs(subjs_counts)
    write_subj_morph_kl_divs(output_file_name, subj_morph_kl_divs)
    w.write(str(num_counts))
    w.close()

main()
