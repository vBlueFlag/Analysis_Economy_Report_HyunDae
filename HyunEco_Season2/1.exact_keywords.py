#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os.path
from collections import Counter
import math
import ujson

''' 연금시장리뷰, 통일경제, 지식경제를 제외하고 출력'''

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
    chair_morph_counts = Counter()
    all_morphs = set()
    information = []
    subjs_counts = {}

    with open(input_file_name, 'r', encoding='utf-8') as f:
        information = ujson.load(f)
        for i in range(len(information)):
            subj_code = information[i][Subject_KEY]
            if subj_code == "Nowhere" or subj_code == "연금시장리뷰" or subj_code == "통일경제" or subj_code == "지식경제": #이건 pass!
                continue
            subj = MagazinID_MAP[subj_code]

            morphed_file = "HyunEco_Season2/morphed/" + information[i]['morphedName']
            try:
                with open(morphed_file, 'r', encoding='utf-8') as morphedReport:
                    morphedText = ujson.load(morphedReport)
                    morphs = []
                    for j in range(len(morphedText)):
                        morphs = ext_morphs(morphedText[j]['morphAnal'], morphs)

                    if subj == "VIP Report":
                        vip_morph_counts.update(morphs)
                    elif subj == "한국경제주평":
                        korea_morph_counts.update(morphs)
                    elif subj == "이슈리포트":
                        issue_morph_counts.update(morphs)
                    elif subj == "Chairperson Note":
                        chair_morph_counts.update(morphs)

                    all_morphs.update(morphs)
            except:
                pass

    subjs_counts = { "vip" : vip_morph_counts, "korea" : korea_morph_counts, "issue" : issue_morph_counts,\
                    "chair":chair_morph_counts, \
                     "all" : all_morphs}
    
    return subjs_counts


def ext_morphs(ma_res,morphs):

    for word in ma_res:
        #for word in sen:
        for morph_lex, morph_pos in word:
            if morph_pos not in FEATURE_POSES: #지금은 모든 MazagineID를 실험한다
                continue

            morphs.append(morph_lex)

    return morphs


def get_subj_morph_kl_divs(subjs_counts):

    sum_vip_morph_counts = 0
    sum_korea_morph_counts = 0
    sum_issue_morph_counts = 0
    sum_chair_morph_counts = 0

    for count in subjs_counts['vip'].values():
        sum_vip_morph_counts += count

    for count in subjs_counts['korea'].values():
        sum_korea_morph_counts += count

    for count in subjs_counts['issue'].values():
        sum_issue_morph_counts += count

    for count in subjs_counts['chair'].values():
        sum_chair_morph_counts += count

    #드디어 KL발산을 계산한다
    subj_morph_kl_divs = []

    for morph in subjs_counts['all']:
        for subj, morph_counts, sum_morph_counts in zip(["VIP Report","한국경제주평","이슈리포트",\
                                                            "Chairperson Note"],
                                         [subjs_counts['vip'],subjs_counts['korea'],subjs_counts['issue'],\
                                          subjs_counts['chair']],
                                                        [sum_vip_morph_counts,sum_korea_morph_counts,sum_issue_morph_counts,
                                                         sum_chair_morph_counts]):
            subj_morph_count = morph_counts[morph]
            subj_morph_prob = subj_morph_count / sum_morph_counts

            vip = subjs_counts['vip'][morph] / sum_vip_morph_counts
            korea = subjs_counts['korea'][morph] / sum_korea_morph_counts
            issue = subjs_counts['issue'][morph] / sum_issue_morph_counts
            chair = subjs_counts['chair'][morph] / sum_chair_morph_counts

            if subj == "VIP Report": # [ korea, vip, issue, chair ]
                other_subj_morph_probs = [ korea, issue, chair ]

            elif subj == "한국경제주평":
                other_subj_morph_probs = [ vip, issue, chair ]

            elif subj == "이슈리포트":
                other_subj_morph_probs = [ korea, vip, chair  ]

            elif subj == "Chairperson Note":
                other_subj_morph_probs = [ korea, vip, issue  ]

            avg_morph_prob = \
                (subj_morph_prob + sum(other_subj_morph_probs)) / 4

            try:
                kl_div = calc_kl_div(subj_morph_prob, avg_morph_prob)
            except:
                kl_div = 0.0

            subj_morph_kl_divs.append([subj, morph, kl_div])

    return subj_morph_kl_divs


def calc_kl_div(subj_morph_prob, avg_morph_prob):

    kl_div = subj_morph_prob * math.log(subj_morph_prob / avg_morph_prob)

    return kl_div


def write_subj_morph_kl_divs(output_file_name, subj_morph_kl_divs):

    with open(output_file_name, "w", encoding="utf-8") as output_file: 
        for output_elems in sorted(subj_morph_kl_divs,
                                   key=get_3rd_elem, reverse=True):
            output_elems = [str(e) for e in output_elems]
            output_file.write("{}\n".format("\t".join(output_elems)))


def get_3rd_elem(seq):

    elem = seq[2]
    return elem


def main():

    input_file_name = "HyunEco_Season2/report_infomation.txt"
    output_file_name= "HyunEco_Season2/result_keywords.txt"

    subjs_counts = get_subj_morph_counts(input_file_name)
    subj_morph_kl_divs = get_subj_morph_kl_divs(subjs_counts)
    write_subj_morph_kl_divs(output_file_name, subj_morph_kl_divs)

main()
