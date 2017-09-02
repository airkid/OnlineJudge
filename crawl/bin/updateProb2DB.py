import os,sys,time,threading,pymysql,traceback,requests,json

def updateProb(OJ,Prob):
    baseURL = 'http://127.0.0.1:6800/'
    schURL = baseURL + 'schedule.json'
    spider = ''
    problem_id = str(Prob)
    if OJ == 'hdu' or OJ == 'HDU':
        spider = 'hdu_problem'
    elif OJ == 'fzu' or OJ == 'FZU':
        spider = 'fzu_problem'
    elif OJ == 'zoj' or OJ == 'ZOJ':
        spider = 'zoj_problem'
    else:
        spider = 'NULL'
    if spider != 'NULL':
        dictdata = {"project":"vjspider","spider":spider,"problem_id":problem_id}
        r = requests.post(schURL,data = dictdata)
