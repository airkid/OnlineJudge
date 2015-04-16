from os import cpu_count
from subprocess import check_call,DEVNULL,CalledProcessError
from threading import Thread,Event
from queue import Queue
from tempfile import TemporaryFile
from models import Submit,TestCase

SOURCE_PATH='../submit/source'
BINARY_PATH='../submit/binary'
ANSWER_PATH='../submit/answer'
RESULT_PATH='../submit/result'

class Daemon:
    DAEMON_MAX=cpu_count()
    
    def __init__(self):
        self.ev=Event()
        self.add(self)

    def _run(self):
        raise NotImplementedError()

    @classmethod
    def init(cls):
        cls.__queue=Queue()
        for i in range(cls.DAEMON_MAX):
            th=Thread(target=cls.daemon,name=cls.__name__)
            th.daemon=True
            th.start()

    @classmethod
    def _add(cls,self):
        cls.queue.put(self)

    @classmethod
    def __daemon(cls):
        while True:
            self=cls.queue.get();
            self.run()
            self.ev.set()

class Complier(Daemon):
    
    @staticmethod
    def c(id):
        cmd='gcc -o {bindir}/{id} {srcdir}/{id}.c'.format(
                srcdir=SOURCE_PATH,bindir=BINARY_PATH,id=id)
        err=open(RESULT_PATH+'/'+id,mode='w+')
        try:
            check_call(cmd.split(' '),stdout=DEVNULL,stderr=err)
        except CalledProcessError as err:
            if err.returncode >0:
                return 
            pass
    @staticmethod
    def cxx():
        pass
    @staticmethod
    def java():
        pass
    @staticmethod
    def python():
        pass

    compliers=[
            None,
            c,
            cxx,
            ]

    def __init__(self,submit):
        self.id=int(submit.id)
        self.type=int(submit.type)
        Daemon.__init__(self)

    def _run(self,type,id):
        fun=self.compliers[type]
        fun(id)

#ComplieDaemon.init()

class Tester(Daemon):
    pass

class Judger(Daemon):
    pass

class Retester(Daemon):
    pass
#JudgeDaemon.init()
