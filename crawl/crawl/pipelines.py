# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from crawl.items import ProblemItem,StatusItem
from vj.models import *
import traceback,sys,re,urllib,os
project_path = os.path.abspath('.')
sys.path.append(project_path)

BASE_URL = {
        'hdu':'http://acm.hdu.edu.cn/','HDU':'http://acm.hdu.edu.cn/',
        'zoj':'http://acm.zju.edu.cn/onlinejudge/','ZOJ':'http://acm.zju.edu.cn/onlinejudge/',
        'fzu':'http://acm.fzu.edu.cn/','FZU':'http://acm.fzu.edu.cn/',
        }

def hash(text):
    res = 0
    MOD = 512
    for i in range(0,len(text)):
        res = res*MOD + ord(text[i])
    res = res%1000000000000009
    return str(res)

def processImg(text,baseURL):
    print("processing image")
    global project_path
    imgre = re.compile(r'src="(.*?)"')
    imglist = imgre.findall(text)
    for imgurl in imglist:
        print("img URL : %s"%imgurl)
        prefix = 0
        while imgurl[prefix]=='.' or imgurl[prefix]=='/':
            prefix = prefix + 1
        suff = len(imgurl)-1
        while imgurl[suff]!='.':
            suff = suff - 1
        validURL = imgurl[prefix:]
        imgName = '/static/vj/img/problemimg/'+hash(baseURL+imgurl)+imgurl[suff:]
        #imgName = '/static/img/problemimg/a.jpg'
        print("new img name : %s"%imgName)
        try:
            urllib.request.urlretrieve(baseURL+validURL,project_path+('%s'%imgName))
        except Exception as e:
            print("save fail:",str(e))
            pass
        text = text.replace(imgurl,imgName)
    return text

def restoreSpecialChar(text):
    return text.\
            replace('<=', ' &le; ').\
            replace(' < ', ' &lt; ').\
            replace(' > ', ' &gt; ').\
            replace('>=', ' &ge; ').\
            replace(r'\n','\n').\
            replace(r'\r','\r').\
            replace(r'\t','\t').\
            replace(r'\"','\"').\
            replace(r'\'','\'').\
            replace(r'\\','\\')
            

class SolPipeline(object):

    def __init__(self):
        print("<<<<<<<<<<<<<<<pipeline init>>>>>>>>>>>>")

    def process_item(self, item, spider):
        print(">>>>pipeline process")
        if isinstance(item,ProblemItem):
            print(">>>>ProblemItem")
            self.processProblemItem(item)
        elif isinstance(item,StatusItem):
            print(">>>>StatusItem")
            self.processStatusItem(item)
        return item

    def processStatusItem(self,item):
        try:
            print("begin : %s)))"%(item['vjRunID']))
            sts = Status.objects.get(runid=int(item['vjRunID']))
            sts.result = item['result']
            sts.timec = item['timec']
            sts.memoryc = item['memoryc']
            print("end : %s,%s,%s)))"%(sts.result,sts.timec,sts.memoryc))
            sts.save()
            
            userinfo = UserInfo.objects.get(id=sts.user)
            ischange = False  
            try:
                userinfo.problems_try.add(sts.pro)
                userinfo.problem_try = userinfo.cnt_try()
                ischange = True
            except:
                pass
            try:
                if sts.result=='Accept' or sts.result=='Accepted' or sts.result=='Yes' or sts.result=='YES':
                    userinfo.problems_ac.add(sts.pro)
                    userinfo.problem_ac = userinfo.cnt_ac()
                    ischange = True
            except:
                pass
            if ischange:
                userinfo.save()
            
        except Exception as e:
            print("Error : sql execute failed")
            print(str(e))
            print('traceback.print_exc():%s'% traceback.print_exc())
            print('traceback.format_exc():\n%s' % traceback.format_exc())

    def processProblemItem(self,item):
        global BASE_URL
        need = ['desc','input','output','note']
        for k in need :
            str = item[k]
            L = 0
            R = len(str)
            while L < R:
                if str[L] == '>':
                    break
                else:
                    L+=1
            while L < R:
                if str[R-1] == '<':
                    break;
                else:
                    R-=1
            item[k] = str[L+1:R-1]
        """
        for k in item.keys():
            str = ""
            for i in range(0,len(item[k])):
                if item[k][i] == '\'':
                    str += '\\'
                str += item[k][i]
            item[k] = str
        """
        for k in item.keys():
            item[k] = restoreSpecialChar(item[k])
            item[k] = processImg(item[k],BASE_URL[item['originOj']])

        try:
            try:
                prob = Problem.objects.get(originoj=item['originOj'],problemid=item['problemId'])
                print("The problem is existed.")
                prob.originoj = item['originOj']
                prob.problemurl = item['problemUrl']
                prob.title = item['title']
                prob.timelimit = item['timeLimit']
                prob.memorylimit = item['memoryLimit']
                prob.description = item['desc']
                prob.input = item['input']
                prob.output = item['output']
                prob.sampleinput = item['sampleInput']
                prob.sampleoutput = item['sampleOutput']
                prob.updatetime = item['updateTime']
                prob.note = item['note']
                prob.save()

            except:
                print("The problem is not existed.")
                prob = Problem(originoj=item['originOj'],\
                    problemid=item['problemId'],\
                    problemurl=item['problemUrl'],\
                    title=item['title'],\
                    timelimit=item['timeLimit'],\
                    memorylimit=item['memoryLimit'],
                    description=item['desc'],\
                    input=item['input'],\
                    output=item['output'],\
                    sampleinput=item['sampleInput'],\
                    sampleoutput=item['sampleOutput'],\
                    updatetime=item['updateTime'],
                    note=item['note'])
                qs = Problem.objects.all()
                if not qs.exists():
                    prob.proid = 100000
                prob.save()
        except Exception as e:
            print.write("Error : sql execute failed")
            print.write(str(e))
            print.write('traceback.print_exc():%s'% traceback.print_exc())
            print.write('traceback.format_exc():\n%s' % traceback.format_exc())
            
