# coding=utf-8
from OJ.models import *
from subprocess import call, DEVNULL, Popen
import threading
import psutil
import resource as res
from threading import Thread, Event
from queue import Queue
from tempfile import TemporaryFile

import os,signal
import os.path

FILE_PATH = './JudgeFiles/'
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
        cmd = ['gcc', '-o', dst, src]
        self.result = call(cmd, stdout=DEVNULL, stderr=open(RESULT_PATH + self.id, mode='w+'))
        if self.result > 0:
            # syntax error
            self.result = -2
        elif self.result < 0:
            # compilation error
            self.result = -1
        else:
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
        cmd = ['g++', '-o', dst, src]
        self.result = call(cmd, stdout=DEVNULL, stderr=open(RESULT_PATH + self.id, mode='w+'))
        if self.result > 0:
            self.result = -2
        elif self.result < 0:
            self.result = -1
        else:
            os.remove(RESULT_PATH + self.id)

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
            self.result = -2
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
    OUTPUT_MAX = 1000

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
        p = Popen(bin, stdin=self.ifile, stdout=ofile, universal_newlines=True,
                  preexec_fn=Tester.Limiter(self.cpu_limit, self.memory_limit), stderr=DEVNULL)

        waitResult = os.wait4(p.pid,0)
        self.cpu_used = waitResult[2].ru_utime + waitResult[2].ru_stime
        self.memory_used = waitResult[2].ru_maxrss
        # print(str(self.cpu_used)+'  '+str(self.memory_used))
        self.return_status = waitResult[1]
        # print(waitResult)
        # end with a signal
        if os.WIFSIGNALED(self.return_status):
            self.return_code = os.WTERMSIG(self.return_status)
            if self.return_code == signal.SIGXCPU:
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


    def cxx(self):
        ofile = TemporaryFile('w+t')
        if self.ua:
            bin = ANSWER_PATH + self.id + '/x' + self.id
        else:
            bin = BINARY_PATH + self.id + '/x' + self.id
        p = Popen(bin, stdin=self.ifile, stdout=ofile, preexec_fn=Tester.Limiter(self.cpu_limit, self.memory_limit),
                  universal_newlines=True, stderr=DEVNULL)

        waitResult = os.wait4(p.pid,0)
        self.cpu_used = waitResult[2].ru_utime + waitResult[2].ru_stime
        self.memory_used = waitResult[2].ru_maxrss
        # print(str(self.cpu_used)+'  '+str(self.memory_used))
        self.return_status = waitResult[1]
        # print(waitResult)
        # end with a signal
        if os.WIFSIGNALED(self.return_status):
            self.return_code = os.WTERMSIG(self.return_status)
            if self.return_code == signal.SIGXCPU:
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

    def java(self):
        ofile = TemporaryFile('w+t')
        if self.ua:
            dst = ANSWER_PATH + self.id
        else:
            dst = BINARY_PATH + self.id
        # careful about the maxheapsize for JVM,should be set
        cmd = ['java', '-XX:MaxHeapSize=1024m','-cp', dst, 'Main']
        p = Popen(cmd, stdin=self.ifile, stdout=ofile,  preexec_fn=Tester.Limiter(self.cpu_limit, -1),universal_newlines=True,stderr=DEVNULL)

        waitResult = os.wait4(p.pid,0)
        self.cpu_used = waitResult[2].ru_utime + waitResult[2].ru_stime
        self.memory_used = waitResult[2].ru_maxrss
        # print(str(self.cpu_used)+'  '+str(self.memory_used))
        self.return_status = waitResult[1]
        # print(waitResult)
        # end with a signal
        if os.WIFSIGNALED(self.return_status):
            self.return_code = os.WTERMSIG(self.return_status)
            if self.return_code == signal.SIGXCPU:
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
        self.ifile = TemporaryFile(mode='w+t')
        self.ifile.write(input)
        self.ifile.seek(0)
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
                self.__submit.save()
        if not over:
            self.__submit.status = 0
            self.__submit.run_time = testList[-1].cpu_used
            self.__submit.run_memory = testList[-1].memory_used
        # print('over')
        # 递归删除二进制目录
        from shutil import rmtree

        rmtree(BINARY_PATH + self.id)
        # print('Result is '+str(self.status))
        self.__submit.save()

Judger.init()


# for test

# judger = Judger('javare',3,1,536870912)
# judger = Judger('javabigmem',3,1,268435456)
# judger = Judger('javabigtime',3,1,536870912)
# judger = Judger('javasmallmem',3,1,536870912)
# judger = Judger('normal',2,1,209715200)
# judger = Judger('re',2,1,209715200)
# judger = Judger('bigmem',2,1,400715200)
# judger = Judger('bigtime',2,1,209715200)
# judger = Judger('smallmem',2,1,209715200)
