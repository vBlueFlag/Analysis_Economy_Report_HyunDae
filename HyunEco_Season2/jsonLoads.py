import time
import re
import urllib.parse
import urllib.request
import math
import os
import ujson

pageInfo = []
start_time = time.time() 
print("Start! now.." + str(start_time))

information = []

w = open("HyundaeEconomy/report_infomation1.txt",'w',  encoding="euc-kr")  

with open("HyundaeEconomy/report_infomation.txt", 'r',  encoding="euc-kr") as f:
    #lines = f.readlines()
    information = ujson.load(f)
    print(len(information))
    
    for i in range(len(information)):
        information[i]['morphedName'] = str(information[i]['dateID']) +'['+str(information[i]['fileNum']) +'].txt'
        print(i)

    result = ujson.dumps(information,ensure_ascii=False,indent = 4)
    w.write(result)
w.close()
f.close()
