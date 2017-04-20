#!/usr/bin/python3

import MySQLdb
import os
import getpass
 
try:
    pwd = getpass.getpass('Enter password:')
    conn = MySQLdb.connect(host='localhost',user='oj',passwd=pwd,db='oj',port=3306)
    cur = conn.cursor()
    curdir = os.listdir();
    curdir.sort()
    for dirr in curdir:
        if not os.path.isdir(dirr):
            continue
        if not dirr.isdigit():
            print('%s is not problem ID! Exit.....'%dirr)
            continue
        print('Entering %s'%dirr)
        curfile = os.listdir('./'+dirr)
        curfile.sort()
        for fname in curfile:
            if not fname.endswith('.in'):
                continue
            fname = fname.replace('.in','')
            pid = dirr
            casnum = fname.replace('data','')
            if int(casnum) == 0:
                sample = 1
            else:
                sample = 0
            inputdata = open('./'+dirr+'/'+fname+'.in').read()
            inputdata = inputdata.replace('\'','\\\'')
            outputdata = open('./'+dirr+'/'+fname+'.ans').read()
            outputdata = outputdata.replace('\'','\\\'')
            sql = "INSERT INTO OJ_testcase \
                    VALUES (null, now(), %d, '%s', '%s', 10, %d, %d )" % \
                    (sample, inputdata, outputdata, int(pid), 25)
            cur.execute(sql)
            #sql = "UPDATE OJ_problem set visible=1 where id=%s" % (int(pid))
            #cur.execute(sql)
            if sample < 1:
                print('problem %d testcase %s added'%(int(dirr),fname))
            else:
                print('problem %d sample %s added'%(int(dirr),fname))
        print('Exiting & Removing %s'%dirr)
        os.system('rm -r %s'%dirr)
    cur.close()
    conn.commit() #提交事务
    conn.close()
except MySQLdb.Error as e:
     print("Mysql Error %d: %s" % (e.args[0], e.args[1]))
