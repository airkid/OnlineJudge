
# coding=utf-8
from OJ.models import *
from subprocess import call, DEVNULL, Popen
import threading
import psutil
import lorun
import os
import getpass
import resource as res
from threading import Thread, Event
from queue import Queue
from tempfile import TemporaryFile, NamedTemporaryFile


FILE_PATH = '/home/sduacm/OnlineJudge/JudgeFiles/'
TEMP_PATH = '/tmp/sduoj/'

FILE_PATH = os.path.abspath(FILE_PATH)
TEMP_PATH = os.path.abspath(TEMP_PATH)
try:
    os.mkdir(FILE_PATH)
except:
    pass
try:
    os.mkdir(TEMP_PATH)
except:
    pass
# 源代码路径
ORIGIN_PATH = FILE_PATH + '/source/'
#
SOURCE_PATH = TEMP_PATH + '/source/'
# 可执行路径
BINARY_PATH = TEMP_PATH + '/binary/'
#
ANSWER_PATH = FILE_PATH + '/answer/'
#
RESULT_PATH = FILE_PATH + '/result/'

try:
    os.mkdir(ORIGIN_PATH)
except:
    pass
try:
    os.mkdir(SOURCE_PATH)
except:
    pass
try:
    os.mkdir(BINARY_PATH)
except:
    pass
try:
    os.mkdir(ANSWER_PATH)
except:
    pass
try:
    os.mkdir(RESULT_PATH)
except:
    pass

CHROOT_PATH = '/'

def runone(p_path, in_path, out_path, user_path, time_limit, memory_limit):
    fin = open(in_path)
    ftemp = open(user_path, 'w')
    print('p_path:')
    print(p_path)
    
    runcfg = {
        #'args':['sudo','su','nobody','-c',p_path],
        'args':[p_path],
        'fd_in':fin.fileno(),
        'fd_out':ftemp.fileno(),
        'timelimit':int(time_limit*1000), #in MS
        'memorylimit':int(memory_limit/1024+1024), #in KB
    }
    runcfg['trace'] = True
    runcfg['calls'] = [0,1,2,3,5,9,10,11,12,21,59,158,231]
    runcfg['files'] = {}
    print('runcfg')
    print(runcfg)
    rst = lorun.run(runcfg)
    print('result')
    print(rst)
    fin.close()
    ftemp.close()
    
    if rst['result'] == 0:
        ftemp = open(user_path, 'r')
        output = ftemp.read().strip()
        ftemp.close()
        output = output.replace(chr(13),'')

        fout = open(out_path,'r')
        right = fout.read().strip()
        fout.close()
        right = right.replace(chr(13),'')
        #os.remove('temp.out')
        if right != output:
            if ''.join(output.split()) == ''.join(right.split()):
                #print('PE')
                rst['result'] = 1
            else:
                rst['result'] = 4
    return rst

class Daemon:
    from os import cpu_count

    DAEMON_MAX = cpu_count()

    __initialled = None
    __queue = None

    @classmethod
    def __daemon(cls):
        while True:
            # print(cls)
            if cls.__queue == None:
                cls.__daemon_num -= 1
                break
            self = cls.__queue.get();
            # print(self)
            if self is None:
                cls.__daemon_num -= 1
                cls.__queue.task_done()
                break
            if not self.__cancel:
                self._run()
            self.__ev.set()
            cls.__queue.task_done()

    @classmethod
    def init(cls):
        if cls.__initialled:
            return
        cls.__queue = Queue()
        for i in range(cls.DAEMON_MAX):
            th = Thread(target=cls.__daemon, name=cls.__name__)
            th.daemon = True
            th.start()
        cls.__daemon_num = cls.DAEMON_MAX
        cls.__initialled = True

    @classmethod
    def exit(cls):
        if not cls.__initialled:
            return
        for i in range(cls.__daemon_num):
            cls.__queue.put(None)
        cls.__queue.join()
        cls.__queue = None
        cls.__initialled = False

    def __init__(self):
        self.__ev = Event()
        self.__add()
        self.__cancel = False

    def __add(self):
        if self.__queue:
            self.__queue.put(self)
        else:
            pass  # may raise an exception,but which?

    def _run(self):
        raise NotImplementedError()

    def wait(self):
        self.__ev.wait()

    def cancel(self):
        self.__cancel = True


class Complier(Daemon):
    def c(self):
        ori = ORIGIN_PATH + self.id
        src = SOURCE_PATH + self.id + '.c'
        if self.aa:
            dst = ANSWER_PATH + self.id
        else:
            dst = BINARY_PATH + self.id
        try:
            os.mkdir(dst)
        except:
            pass
        dst += '/c' + self.id
        try:
            os.remove(src)
        except:
            pass
        try:
            os.symlink(ori, src)
        except:
            pass
        cmd = ['gcc', '-o', dst, src, '-O2']
        self.result = call(cmd, stdout=DEVNULL, stderr=open(RESULT_PATH + self.id, mode='w+'))
        if self.result > 0:
            # syntax error
            self.result = -1
        elif self.result < 0:
            # compilation error
            self.result = -1
        else:
            cmd = ['sudo','jk_cp','-j','/jail',dst]
            cp = Popen(cmd)
            cp.wait()
            os.remove(RESULT_PATH + self.id)

    def cxx(self):
        # print("compling cxx")
        ori = ORIGIN_PATH + self.id
        src = SOURCE_PATH + self.id + '.cxx'
        if self.aa:
            dst = ANSWER_PATH + self.id
        else:
            dst = BINARY_PATH + self.id
        try:
            os.mkdir(dst)
        except:
            pass
        dst += '/x' + self.id
        try:
            os.remove(src)
        except:
            pass
        try:
            os.symlink(ori, src)
        except:
            pass
        cmd = ['g++', '-o', dst, src, '-O2']
        self.result = call(cmd, stdout=DEVNULL, stderr=open(RESULT_PATH + self.id, mode='w+'))
        if self.result > 0:
            self.result = -1
        elif self.result < 0:
            self.result = -1
        else:
            cmd = ['sudo','jk_cp','-j','/jail',dst]
            print(cmd)
            cp = Popen(cmd)
            cp.wait()

    def java(self):
        ori = ORIGIN_PATH + self.id
        src = SOURCE_PATH + self.id
        try:
            os.mkdir(src);
        except:
            pass
        src += '/Main.java'
        try:
            os.remove(src)
        except:
            pass
        try:
            os.symlink(ori, src)
        except:
            pass
        if self.aa:
            dst = ANSWER_PATH + self.id
        else:
            dst = BINARY_PATH + self.id
        try:
            os.mkdir(dst)
        except:
            pass
        # print(dst)
        # print(src)
        cmd = ['javac', '-d', dst, src]
        self.result = call(cmd, stdout=DEVNULL, stderr=open(RESULT_PATH + self.id, mode='w+'))
        if self.result > 0:
            self.result = -1
        elif self.result < 0:
            self.result = -1
        pass

    compliers = [
        None,
        c,
        cxx,
        java,
    ]

    def __init__(self, id, lang, as_answer=False):
        self.id = str(id)
        self.lang = int(lang)
        self.aa = as_answer
        Daemon.__init__(self)

    def _run(self):
        fun = self.compliers[self.lang]
        fun(self)


Complier.init()


class Tester(Daemon):
    OUTPUT_MAX = 1024

    class Limiter:
        def __init__(self, cpu_limit, memory_limit):
            self.cpu_limit = cpu_limit
            self.memory_limit = memory_limit

        def __call__(self):
            # res.setrlimit(res.RLIMIT_CORE, (0, 0))
            # res.setrlimit(res.RLIMIT_MEMLOCK, (0, 0))
            # res.setrlimit(res.RLIMIT_FSIZE, (Tester.OUTPUT_MAX, Tester.OUTPUT_MAX))
            res.setrlimit(res.RLIMIT_CPU,(self.cpu_limit,-1))
            if self.memory_limit != -1:
                res.setrlimit(res.RLIMIT_AS,(2*self.memory_limit,-1))
            else:
                res.setrlimit(res.RLIMIT_AS,(-1,-1))
            os.nice(10)


    def c(self):
        ofile = TemporaryFile('w+t')
        if self.ua:
            bin = ANSWER_PATH + self.id + '/c' + self.id
        else:
            bin = BINARY_PATH + self.id + '/c' + self.id

        in_path = self.ifile.name
        out_path = self.ofile.name
        user_path = self.userofile.name
        rst = runone(bin, in_path, out_path, user_path, self.cpu_limit, self.memory_limit)

        self.cpu_used = 0
        self.memory_used = 0
        self.cpu_used = rst['timeused']
        self.memory_used = rst['memoryused']
        if rst['result'] == 0:
            self.result = 0 #Accept
        if rst['result'] == 1: 
            self.result = -8 #Presentation Error
        if rst['result'] == 2: 
            self.cpu_used = min(rst['timeused'],self.cpu_limit*1000)
            self.result = -5 #Time Limit Exceeded
        if rst['result'] == 3: 
            self.memory_used = min(rst['memoryused'],self.memory_limit/1024)
            self.result = -6 #Memory Limit Exceeded
        if rst['result'] == 4: 
            self.result = -7 #Wrong Answer
        if rst['result'] == 5: 
            self.result = -3 #Runtime Error
        if rst['result'] == 6: 
            self.result = -4 #Output Limit Exceeded
        if rst['result'] == 7: 
            self.result = -1 #Compile Error

#        cmd = ['sudo','su','nobody','-c',bin]
#        p = Popen(cmd, stdin=self.ifile, stdout=ofile, preexec_fn=Tester.Limiter(self.cpu_limit+0.5, self.memory_limit*2),universal_newlines=True, stderr=DEVNULL)
#        waitResult = os.wait4(p.pid,0)
#        self.cpu_used = waitResult[2].ru_utime + waitResult[2].ru_stime
#        self.memory_used = waitResult[2].ru_maxrss
#        # print(str(self.cpu_used)+'  '+str(self.memory_used))
#        self.return_status = waitResult[1]
#        print('WaitResult:')
#        print(waitResult)
#        # end with a signal
#        if os.WIFSIGNALED(self.return_status):
#            self.return_code = os.WTERMSIG(self.return_status)
#            if self.return_code == signal.SIGXCPU or self.cpu_used>self.cpu_limit :
#                self.cpu_used = self.cpu_limit
#                self.result = -5
#                # print('TLE')
#            elif self.return_code == signal.SIGSEGV:
#                if self.memory_used > self.memory_limit:
#                    self.result = -6
#                    # print('MLE')
#                else:
#                    self.result = -3
#                    # print('RE')
#            elif self.return_code == signal.SIGKILL:
#                # print('killed')
#                if self.memory_used > self.memory_limit:
#                    self.result = -6
#                    # print('MLE')
#                else:
#                    self.result = -3
#                    # print('RE')
#            else:
#                print('LOG NEW ERROR '+str(self.return_code))
#        # end with 0 or other error
#        else:
#            if self.return_status == 0:
#                if self.cpu_used>self.cpu_limit :
#                    self.cpu_used = self.cpu_limit
#                    self.result = -5
#                    # print('TLE')
#                elif self.memory_used > self.memory_limit:
#                    self.result = -6
#                    # print('MLE')
#                else:
#                    ofile.seek(0)
#                    ofile_string = str(ofile.read(-1)).strip()
#                    output_string = self.output.strip()
#                    ofile_string = ofile_string.replace(chr(13),'')
#                    output_string = output_string.replace(chr(13),'')
#                    # print(ofile_string+'  '+output_string)
#                    # for i in ofile_string:
#                        # print(ord(i))
#                    # for i in output_string:
#                        # print(ord(i))
#                    if ofile_string != output_string:
#                        if ''.join(ofile_string.split()) == ''.join(output_string.split()):
#                            self.result = -8
#                            # print('PE')
#                        else: 
#                            self.result = -7
#                            # print('WA')
#                    else:
#                        self.result = 0
#                        # print('AC')
#            else:
#                if self.memory_used > self.memory_limit:
#                    self.result = -6
#                    # print('MLE')
#                elif self.cpu_used>=self.cpu_limit :
#                    self.cpu_used = self.cpu_limit
#                    self.result = -5
#                    # print('TLE')
#                else:
#                    self.result = -3
#                    # print('RE')
#

    def cxx(self):
        ofile = TemporaryFile('w+t')
        if self.ua:
            bin = ANSWER_PATH + self.id + '/x' + self.id
        else:
            bin = BINARY_PATH + self.id + '/x' + self.id

        in_path = self.ifile.name
        out_path = self.ofile.name
        user_path = self.userofile.name
        print('memory:')
        print(self.memory_limit);
        rst = runone(bin, in_path, out_path, user_path, self.cpu_limit, self.memory_limit)
        print('rst')
        print(rst)


        self.cpu_used = 0
        self.memory_used = 0
       # print('time consume:')
       # print(rst['timeused'])
       # print('time limit:')
       # print(self.cpu_limit)
       # print('memory consume:')
       # print(rst['memoryused'])
       # print('memory limit:')
       # print(self.memory_limit)
        
        if rst['result'] == 0:
            self.cpu_used = int(rst['timeused'])
            self.memory_used = int(rst['memoryused'])
           # print('cpu_used:')
           # print(self.cpu_used)
           # print('memory_used:')
           # print(self.memory_used)
            self.result = 0 #Accept
        if rst['result'] == 1: 
            self.cpu_used = rst['timeused']
            self.memory_used = rst['memoryused']
            self.result = -8 #Presentation Error
        if rst['result'] == 2: 
            self.cpu_used = min(rst['timeused'],self.cpu_limit*1000)
            self.memory_used = rst['memoryused']
            self.result = -5 #Time Limit Exceeded
        if rst['result'] == 3: 
            self.cpu_used = rst['timeused']
            self.memory_used = min(rst['memoryused'],self.memory_limit/1024)
            self.result = -6 #Memory Limit Exceeded
        if rst['result'] == 4: 
            self.cpu_used = rst['timeused']
            self.memory_used = rst['memoryused']
            self.result = -7 #Wrong Answer
        if rst['result'] == 5: 
            self.result = -3 #Runtime Error
        if rst['result'] == 6: 
            self.result = -4 #Output Limit Exceeded
        if rst['result'] == 7: 
            self.result = -1 #Compile Error


#        cmd = ['sudo','su','nobody','-c',bin]
#        p = Popen(cmd, stdin=self.ifile, stdout=ofile, preexec_fn=Tester.Limiter(self.cpu_limit+0.5, self.memory_limit*2),universal_newlines=True, stderr=DEVNULL)
#        waitResult = os.wait4(p.pid,0)
#        print(waitResult)
#        self.cpu_used = waitResult[2].ru_utime + waitResult[2].ru_stime
#        #  print(self.cpu_used)
#        self.memory_used = waitResult[2].ru_maxrss
#        self.return_status = waitResult[1]
#        # print(waitResult)
#        # end with a signal
#        if os.WIFSIGNALED(self.return_status):
#            self.return_code = os.WTERMSIG(self.return_status)
#            if self.return_code == signal.SIGXCPU or self.cpu_used>self.cpu_limit :
#                self.cpu_used = self.cpu_limit
#                self.result = -5
#                # print('TLE')
#            elif self.return_code == signal.SIGSEGV:
#                if self.memory_used > self.memory_limit:
#                    self.result = -6
#                    # print('MLE')
#                else:
#                    self.result = -3
#                    # print('RE')
#            elif self.return_code == signal.SIGKILL:
#                # print('killed')
#                if self.memory_used > self.memory_limit:
#                    self.result = -6
#                    # print('MLE')
#                else:
#                    self.result = -3
#                    # print('RE')
#            else:
#                print('LOG NEW ERROR '+str(self.return_code))
#        # end with 0 or other error
#        else:
#            if self.return_status == 0:
#                if self.cpu_used>self.cpu_limit :
#                    self.cpu_used = self.cpu_limit
#                    self.result = -5
#                    # print('TLE')
#                elif self.memory_used > self.memory_limit:
#                    self.result = -6
#                    # print('MLE')
#                else:
#                    ofile.seek(0)
#                    ofile_string = str(ofile.read(-1)).strip()
#                    output_string = self.output.strip()
#                    ofile_string = ofile_string.replace(chr(13),'')
#                    output_string = output_string.replace(chr(13),'')
#                    # print(ofile_string+'  '+output_string)
#                    # for i in ofile_string:
#                        # print(ord(i))
#                    # for i in output_string:
#                        # print(ord(i))
#                    if ofile_string != output_string:
#                        if ''.join(ofile_string.split()) == ''.join(output_string.split()):
#                            self.result = -8
#                            # print('PE')
#                        else: 
#                            self.result = -7
#                            # print('WA')
#                    else:
#                        self.result = 0
#                        # print('AC')
#            else:
#                if self.memory_used > self.memory_limit:
#                    self.result = -6
#                    # print('MLE')
#                elif self.cpu_used>=self.cpu_limit :
#                    self.cpu_used = self.cpu_limit
#                    self.result = -5
#                    # print('TLE')
#                else:
#                    self.result = -3
#                    # print('RE')

    def java(self):
        ofile = TemporaryFile('w+t')
        if self.ua:
            dst = ANSWER_PATH + self.id
        else:
            dst = BINARY_PATH + self.id
        # careful about the maxheapsize for JVM,should be set
        cmd = ['java', '-XX:MaxHeapSize=1024m','-cp', dst, 'Main']
        p = Popen(cmd, stdin=self.ifile, stdout=ofile,  preexec_fn=Tester.Limiter(self.cpu_limit*2, -1),universal_newlines=True,stderr=DEVNULL)

        waitResult = os.wait4(p.pid,0)
        self.cpu_used = waitResult[2].ru_utime + waitResult[2].ru_stime
        self.memory_used = waitResult[2].ru_maxrss
        # print(str(self.cpu_used)+'  '+str(self.memory_used))
        self.return_status = waitResult[1]
        # print(waitResult)
        # end with a signal
        if os.WIFSIGNALED(self.return_status):
            self.return_code = os.WTERMSIG(self.return_status)
            if self.return_code == signal.SIGXCPU or self.cpu_used>=self.cpu_limit :
                self.cpu_used = self.cpu_limit
                self.result = -5
                # print('TLE')
            elif self.return_code == signal.SIGSEGV:
                if self.memory_used > self.memory_limit/1024:
                    self.result = -6
                    # print('MLE')
                else:
                    self.result = -3
                    # print('RE')
            elif self.return_code == signal.SIGKILL:
                # print('killed')
                if self.memory_used > self.memory_limit/1024:
                    self.result = -6
                    # print('MLE')
                else:
                    self.result = -3
                    # print('RE')
            else:
                print('LOG NEW ERROR '+str(self.return_code))
        # end with 0 or other error
        else:
            if self.return_status == 0:
                if self.memory_used > self.memory_limit/1024:
                    self.result = -6
                    # print('MLE')
                else:
                    ofile.seek(0)
                    ofile_string = str(ofile.read(-1)).strip()
                    output_string = self.output.strip()
                    ofile_string = ofile_string.replace(chr(13),'')
                    output_string = output_string.replace(chr(13),'')
                    # print(ofile_string+'  '+output_string)
                    if ofile_string != output_string:
                        self.result = -7
                        # print('WA')
                    else:
                        self.result = 0
                        # print('AC')
            else:
                if self.memory_used > self.memory_limit/1024:
                    self.result = -6
                    # print('MLE')
                else:
                    self.result = -3
                    # print('RE')

    testers = [
        None,
        c,
        cxx,
        java,
    ]

    def __init__(self, id, lang, input, output, cpu_limit, memory_limit, use_answer=False):
        self.id = str(id)
        self.lang = int(lang)
        self.ifile = NamedTemporaryFile(mode='w+',suffix='.in')
        self.ifile.write(input)
        self.ifile.seek(0)
        self.ofile = NamedTemporaryFile(mode='w+',suffix='.out')
        self.ofile.write(str(output))
        self.ofile.seek(0)
        self.userofile = NamedTemporaryFile(mode='w+',suffix='.out')
        self.userofile.seek(0)
        self.output = str(output)
        self.cpu_limit = cpu_limit
        self.memory_limit = memory_limit
        # for java, give extra 25M, double the original cpu time
        if self.lang == 3:
            self.memory_limit = memory_limit + 26214400
            self.cpu_limit = cpu_limit * 2
        self.ua = use_answer
        # set the stauts for 'running'
        self.result = 3
        Daemon.__init__(self)

    def _run(self):
        fun = self.testers[self.lang]
        fun(self)


Tester.init()


class Judger(Daemon):
    def __init__(self, submit):
        self.__submit = submit
        prob = self.__submit.pid
        self.id = str(self.__submit.id)
        # self.uid = str(self.__submit.uid)
        # self.pid = str(self.__submit.pid)
        self.lang = int(self.__submit.lang)
        self.lcpu = int(prob.limit_time)
        self.lmem = int(prob.limit_memory)
        Daemon.__init__(self)

    def _run(self):
        c = Complier(self.id, self.lang)
        self.status = 1
        c.wait()
        if c.result:
            print("compile result is"+str(c.result))
            self.__submit.status = c.result
            self.__submit.save()
            return
        caseList = TestCase.objects.filter(pid__exact=self.__submit.pid)
        testList = []
        for case in caseList:
            testList.append(Tester(self.id, self.lang, case.input, case.output, self.lcpu, self.lmem))
        over = False
        for test in testList:
            if over:
                test.cancel()
                continue
            test.wait()
            if test.result:
                over = True
                self.__submit.status = test.result
                self.__submit.run_time = test.cpu_used
                self.__submit.run_memory = test.memory_used
                # self.__submit.save()
        if not over:
            self.__submit.status = 0
            # use ms
            self.__submit.run_time = testList[-1].cpu_used
            # use kb
            self.__submit.run_memory = testList[-1].memory_used
            # print('save')
            # print(self.__submit.run_time)
            # print(self.__submit.run_memory)
            self.__submit.save()
        # print('over')
        # 递归删除二进制目录

        for test in testList:
            print('Removing tmpfile')
            test.ifile.close()
            test.ofile.close()
            test.userofile.close()
        from shutil import rmtree

        rmtree(BINARY_PATH + self.id)
        cmd = ['sudo','rm','-rf','/jail'+BINARY_PATH+self.id]
        cp = Popen(cmd)
        cp.wait()
        print('Result is '+str(self.status))
#        cmd = ['rm','-r','/jail/tmp/sduoj/binary/'+self.id]
#        rm = Popen(cmd)
#        rm.wait()

        #try是尝试过的总次数，ac是正确的题目数

        # problem_try = Submit.objects.filter(uid=self.__submit.uid,status=1).count()
        print(self.__submit.uid.info)
        problem_try = UserInfo.objects.get(id=self.__submit.uid.info.id).problem_try
        self.__submit.uid.info.problem_try = problem_try + 1
        print("try is ")
        print(problem_try)

        if (self.__submit.status == 0):
            problem_ac = Submit.objects.filter(pid=self.__submit.pid, uid=self.__submit.uid, status=0).count()
            print("   ac is ")
            print(problem_ac)
            if(problem_ac == 0):
                self.__submit.uid.info.problem_ac = self.__submit.uid.info.problem_ac + 1

        self.__submit.uid.info.save()

        self.__submit.save()

Judger.init()


# for test

# judger = Judger('javare',3,1,5368.70912)
# judger = Judger('javabigmem',3,1,268435456)
# judger = Judger('javabigtime',3,1,536870912)
# judger = Judger('javasmallmem',3,1,536870912)
# judger = Judger('normal',2,1,209715200)
# judger = Judger('re',2,1,209715200)
# judger = Judger('bigmem',2,1,400715200)
# judger = Judger('bigtime',2,1,209715200)
# judger = Judger('smallmem',2,1,209715200)
