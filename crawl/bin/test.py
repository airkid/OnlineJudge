"""
import os,sys,time,threading,pymysql,traceback,requests,json
project_path = os.path.abspath('../..')
sys.path.append(project_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SDUVJ.settings")
import django
django.setup()
from submiter import *


def getCode(source):
    global project_path
    try:
        print("Path : "+project_path+'/codes/'+str(source))
        
        file_object = open(project_path+'/codes/'+str(source))
        all_the_text = 'NULL'
        try:
            all_the_text = file_object.read( )
        finally:
            file_object.close( )
        return all_the_text
    except:
        print("The code file does not exist")
Prob = '1001'
acc = 'sduvj1'
Code = getCode('hdu1000')

submiter = ZojSubmiter(Prob,acc,Code,'0')

submiter.submit2OJ()

"""
from updateProb2DB import *

#updateProb('HDU','2996')
#updateProb('HDU','2270')
#updateProb('HDU','4396')
#updateProb('HDU','5111')
#updateProb('HDU','4453')
#updateProb('HDU','1166')

for i in range(1000,6033):
    updateProb('HDU',str(i))
for i in range(1015,2253):
    updateProb('FZU',str(i))
for i in range(1001,3971):
    updateProb('ZOJ',str(i))
    
