#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
fileName = "testtest.txt"
title_string = u"<dt>작성일</dt>\n\n\t\t\t\t<dd>(.*?)</dd>"
f = open(fileName, "r")
fTxt = f.read()
rx_sequence=re.compile(title_string,re.MULTILINE)
rx_blanks=re.compile(r"\W+") # to remove blanks and newlines
for match in rx_sequence.finditer(fTxt):
    title = match.group(1)
    title = title.strip()
    #title = rx_blanks.sub("",title)
    print (title)
f.close()
