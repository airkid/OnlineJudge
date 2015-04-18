from subprocess import call,DEVNULL
from threading import Thread,Event#,Lock
from queue import Queue
from tempfile import TemporaryFile
from OJ.models import Submit,TestCase

import os
import os.path

FILE_PATH='./JudgeFiles/'
TEMP_PATH='/tmp/sduoj/'

FILE_PATH=os.path.abspath(FILE_PATH)
TEMP_PATH=os.path.abspath(TEMP_PATH)

try:
    os.mkdir(FILE_PATH)
except:
    pass
try:
    os.mkdir(TEMP_PATH)
except:
    pass

ORIGIN_PATH=FILE_PATH+'/source/'
SOURCE_PATH=TEMP_PATH+'/source/'
BINARY_PATH=TEMP_PATH+'/binary/'
ANSWER_PATH=FILE_PATH+'/answer/'
RESULT_PATH=FILE_PATH+'/result/'

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

class Daemon:
    from os import cpu_count
    DAEMON_MAX=cpu_count()

    __initialled=None
    __queue=None

    @classmethod
    def __daemon(cls):
        while True:
            if cls.__queue==None:
                cls.__daemon_num-=1
                break
            self=cls.__queue.get();
            if self is None:
                cls.__daemon_num-=1
                cls.__queue.task_done()
                break
            self._run()
            self.__ev.set()
            cls.__queue.task_done()

    @classmethod
    def init(cls):
        if cls.__initialled:
            return
        cls.__queue=Queue()
        for i in range(cls.DAEMON_MAX):
            th=Thread(target=cls.__daemon,name=cls.__name__)
            th.daemon=True
            th.start()
        cls.__daemon_num=cls.DAEMON_MAX
        cls.__initialled=True

    @classmethod
    def exit(cls):
        if not cls.__initialled:
            return
        for i in range(cls.__daemon_num):
            cls.__queue.put(None)
        cls.__queue.join()
        cls.__queue=None
        cls.__initialled=False

    def __init__(self):
        self.__ev=Event()
        self.__add()

    def __add(self):
        if self.__queue:
            self.__queue.put(self)
        else:
            pass #may raise an exception,but which?

    def _run(self):
        raise NotImplementedError()

    def wait(self):
        self.__ev.wait()

class Complier(Daemon):
    
    def c(self,id):
        ori=ORIGIN_PATH+str(id)
        src=SOURCE_PATH+str(id)+'.c'
        dst=BINARY_PATH+str(id)
        try:
            os.remove(src)
        except:
            pass
        try:
            os.symlink(ori,src)
        except:
            pass
        cmd='gcc -o {dst} {src}'.format(src=src,dst=dst)
        self.result=call(cmd.split(' '),stdout=DEVNULL,stderr=open(RESULT_PATH+str(id),mode='w+'))
    def cxx(self,id):
        ori=ORIGIN_PATH+str(id)
        src=SOURCE_PATH+str(id)+'.cxx'
        dst=BINARY_PATH+str(id)
        try:
            os.remove(src)
        except:
            pass
        try:
            os.symlink(ori,src)
        except:
            pass
        cmd='g++ -o {dst} {src}'.format(src=src,dst=dst)
        self.result=call(cmd.split(' '),stdout=DEVNULL,stderr=open(RESULT_PATH+str(id),mode='w+'))
    def java(self,id):
        pass
    def python(self,id):
        pass

    compliers=[
            None,
            c,
            cxx,
            java,
            python,
            ]

    def __init__(self,id,type):
        self.id=int(id)
        self.type=int(type)
        Daemon.__init__(self)

    def _run(self):
        fun=self.compliers[self.type]
        fun(self,self.id)

Complier.init()

class Tester(Daemon):
    def __init(self,id,type,input,output):
        self.id=id
        self.type=type
        self.input=input
        self.output=output
        Daemon.__init__(self)

    def _run(self):
        fun=self.testers[type]
        fun(self,self.id,self.input,self.output)

class Judger(Daemon):
    pass

class Retester(Daemon):
    pass
#JudgeDaemon.init()
