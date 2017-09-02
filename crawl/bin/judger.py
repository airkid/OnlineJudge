#!/usr/bin/python3
#coding:utf-8
import os,sys,time,threading,pymysql,traceback,requests,json
project_path = os.path.abspath('../..')
code_path = project_path+'/JudgeFiles/codes/'
sys.path.append(project_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OnlineJudge.settings")
import django
django.setup()

from vj.models import *
from submiter import *

mutex = threading.Lock() #acc
submitMutex = threading.Lock()
account = {"sduvj1":True,"sduvj5":True,"sduvj3":True,"sduvj4":True}
threadID = 0
inProcess = set()
threadLog = open('log/thread.log','a+')
baseURL = 'http://127.0.0.1:6800/'
schURL = baseURL + 'schedule.json'
jobsURL = baseURL + 'listjobs.json?project=vjspider'
endStatus = ['Accept','Wrong','Error','Exceed','Fault','Exit','Call']

class JudgerThread(threading.Thread):
    def __init__(self,threadID,vjRunID,OJ,Prob,Code,Lang):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.vjRunID = vjRunID
        self.OJ = OJ
        self.Prob = Prob
        self.Code = Code
        self.Lang = Lang


    def run(self):
        global account,threadLog,schURL,jobsURL,endStatus
        acc = ""
        while acc == "":
            if mutex.acquire():
                for k in account.keys():
                    if account[k]:
                        acc = k
                        account[k] = False
                        threadLog.write("accquire account %s (vjRunID : %d threadID : %d\n"%(acc,self.vjRunID,self.threadID))
                        threadLog.flush()
                        break
                mutex.release()
            time.sleep(1)
        
        spider = ""


        print("!!!!!vjRunID:"+str(self.vjRunID))
        # print(self.vjRunID)
        # print(self.vjRunID)
        sub = False
        if submitMutex.acquire():
            submiter = None
            if (self.OJ == "hdu") or (self.OJ == 'HDU'):
                spider = "hdu_status"
                submiter = HduSubmiter(self.Prob,acc,self.Code,self.Lang)
            elif (self.OJ == 'fzu' ) or (self.OJ == 'FZU'):
                spider = 'fzu_status'
                submiter = FzuSubmiter(self.Prob,acc,self.Code,self.Lang)
            elif (self.OJ == 'zoj' ) or (self.OJ == 'ZOJ'):
                spider = 'zoj_status'
                submiter = ZojSubmiter(self.Prob,acc,self.Code,self.Lang)
            else:
                submitMutex.release()

            sub = submiter.submit2OJ()
            submitMutex.release()

        if sub:
            while True:
                time.sleep(1)
                dictdata = {"project":"vjspider","spider":spider,"vj_run_id":self.vjRunID,"user":acc}
                r = requests.post(schURL,data = dictdata)
                jobID = json.loads(r.text)['jobid']        
                while True:
                    fjobs = json.loads((requests.get(jobsURL)).text)['finished']
                    flag = False
                    for fjob in fjobs:
                        if fjob['id'] == jobID :
                            flag = True
                    if flag:
                        break
                    time.sleep(1)

                flag = False
                cs = str(Status.objects.get(runid=self.vjRunID).result)
                for st in endStatus:
                    if st in cs:
                        flag = True
                        break
                if flag:
                    break
                
        else:
            dictdata = {"project":"vjspider","spider":spider,"vj_run_id":self.vjRunID,"submit":"False"}
            r = requests.post(schURL,data = dictdata)
        
        print("Thread %d finished"%self.threadID)

        if mutex.acquire():
            account[acc] = True
            threadLog.write("release account %s (vjRunID : %d threadID : %d\n"%(acc,self.vjRunID,self.threadID))
            threadLog.flush()
            mutex.release()

def daemon_init(stdin='/log/null',stdout='/log/null',stderr='/log/null'):
    sys.stdin = open(stdin,'r')
    sys.stdout = open(stdout,'a+')
    sys.stderr = open(stderr,'a+')
    try:
        pid = os.fork()
        if pid > 0:        #parrent
            os._exit(0)
    except OSError as e:
        sys.stderr.write("first fork failed!!"+e.strerror)
        os._exit(1)

    # 子进程， 由于父进程已经退出，所以子进程变为孤儿进程，由init收养
    '''setsid使子进程成为新的会话首进程，和进程组的组长，与原来的进程组、控制终端和登录会话脱离。'''
    os.setsid()
    '''防止在类似于临时挂载的文件系统下运行，例如/mnt文件夹下，这样守护进程一旦运行，临时挂载的文件系统就无法卸载了，这里我们推荐把当前工作目录切换到根目录下'''
    os.chdir("/")
    '''设置用户创建文件的默认权限，设置的是权限“补码”，这里将文件权限掩码设为0，使得用户创建的文件具有最大的权限。否则，默认权限是从父进程继承得来的'''
    os.umask(0)

    try:
        pid = os.fork()     #第二次进行fork,为了防止会话首进程意外获得控制终端
        if pid > 0:
            os._exit(0)     #父进程退出
    except OSError as e:
        sys.stderr.write("second fork failed!!"+e.strerror)
        os._exit(1)

    # 孙进程
    #   for i in range(3,64):  # 关闭所有可能打开的不需要的文件，UNP中这样处理，但是发现在python中实现不需要。
    #       os.close(i)
    sys.stdout.write("Daemon has been created! with pid: %d\n" % os.getpid())
    sys.stdout.flush()  #由于这里我们使用的是标准IO，回顾APUE第五章，这里应该是行缓冲或全缓冲，因此要调用flush，从内存中刷入日志文件。

def getCode(source):
    global project_path
    try:
        print("Path : "+code_path+str(source))
        
        file_object = open(code_path+str(source))
        all_the_text = 'NULL'
        try:
            all_the_text = file_object.read( )
        finally:
            file_object.close( )
        return all_the_text
    except:
        print("The code file does not exist")

def main():
    global threadID,inProcess
    
    sys.stdout.write("main begin!\n")
    sys.stdout.flush()
    while True:
        try:

            results = Status.objects.filter(result='Waiting')
            for row in results:
                vjRunID = row.runid
                print("vjRunID : ",vjRunID)
                if vjRunID in inProcess:
                    print("inProcess")
                    continue
                inProcess.add(vjRunID)
                Code = getCode(row.source_code)
                Lang = row.lang
                
                OJ = row.pro.originoj
                Prob = row.pro.problemid
                
                threadID = threadID + 1
                print("Entering Thread %d"%(threadID))
                thd = JudgerThread(threadID,vjRunID,OJ,Prob,Code,Lang)
                thd.setDaemon(False)
                thd.start()
        except Exception as e:
            sys.stderr.write("Error : sql execute failed")
            sys.stderr.write(str(e))
            sys.stderr.write('traceback.print_exc():%s'% traceback.print_exc())
            sys.stderr.write('traceback.format_exc():\n%s' % traceback.format_exc())
        #db.commit()
        sys.stdout.flush()
        time.sleep(5)


if __name__ == '__main__':
    print ('========main function start!============') #在调用daemon_init函数前是可以使用print到标准输出的，调用之后就要用把提示信息通过stdout发送到日志系统中了
    #daemon_init('log/null','log/daemon.log','log/daemon.err')    # 调用之后，你的程序已经成为了一个守护进程，可以执行自己的程序入口了
    #time.sleep(10)
    main()
