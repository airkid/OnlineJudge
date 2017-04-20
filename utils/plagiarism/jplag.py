#!/usr/bin/python3
import MySQLdb
import os
import getpass
import shutil
import http.server
import socketserver
try:
    pwd = getpass.getpass('Enter password:')
    conn = MySQLdb.connect(host='localhost',user='oj',passwd=pwd,db='oj',port=3306)
    cur = conn.cursor()
    contestid=input("please input contest id: ")
    cur.execute('SELECT a.source_code, b.username, a.id, a.lang, a.pid_id from OJ_submit as a, \
            auth_user as b where a.uid_id=b.id and a.cid=%s and a.status=0'%(contestid))
    dirr = 'contest_%s'%(contestid)
    if not os.path.exists(dirr):
        os.mkdir(dirr)
    results=cur.fetchall()
    for submit in results:
#        print(submit)
        dirr_user = dirr+'/'+'%s_%s'%(submit[1],str(submit[2]))
        if not os.path.exists(dirr_user):
            os.mkdir(dirr_user)
        filename = str(submit[2])
        if submit[3]==3:
            filename = filename+'.java'
        elif submit[3]==2:
            filename = filename+'.cpp'
        elif submit[3]==1:
            filename = filename+'.c'
#        print(filename)
        shutil.copy(submit[0],dirr_user+'/'+filename)
    cur.close()
    conn.close()
    os.system('java -jar jplag-2.11.8.jar -l java17 -r result/java/ -s contest_%s/'%(contestid))
    os.system('java -jar jplag-2.11.8.jar -l c/c++ -r result/c_c++/ -s contest_%s/'%(contestid))
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", 8010), Handler)
    print("serving at 8010 ")
    httpd.serve_forever()
except MySQLdb.Error as e:
    print("Mysql Error %d: %s" % (e.args[0], e.args[1]))
