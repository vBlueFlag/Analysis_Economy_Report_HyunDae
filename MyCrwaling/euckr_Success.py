#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import urllib.request

page_url = "http://news.chosun.com/site/data/html_dir/2016/05/19/2016051903048.html"

response = urllib.request.urlopen(page_url)
response = response.read()
response = response.decode('euc-kr')

f = open('chosun_test.txt', "w", encoding="euc-kr")
print(response)
f.write(response)
f.close()
