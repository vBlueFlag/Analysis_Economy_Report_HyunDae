#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import urllib
import time

page_url = "http://home.ebs.co.kr/toeic/board/23/10052166/fileDownLoad?pstId=10007120957&pstAtchFileId=10000382884"

response = urllib.request.urlopen(page_url)
urllib.request.urlretrieve(page_url,str(int(time.time())))
#urllib.request.urlretrieve(page_url,"hh.hwp")
print()