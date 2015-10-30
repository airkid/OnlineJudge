# coding=utf-8
from subprocess import call, DEVNULL, Popen
from threading import Thread, Event
from queue import Queue
from tempfile import TemporaryFile
from OJ.models import TestCase, Submit

import os
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
            if cls.__queue == None:
                cls.__daemon_num -= 1
                break
            self = cls.__queue.get();
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
        print("compling cxx")
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
        cmd = ['javac', '-d', dst, src]
        self.result = call(cmd, stdout=DEVNULL, stderr=open(RESULT_PATH + self.id, mode='w+'))
        if self.result > 0:
            self.result = -2
        elif self.result < 0:
            self.result = -1
        pass

    def python(self):
        from py_compile import compile, PyCompileError

        ori = ORIGIN_PATH + self.id
        src = SOURCE_PATH + self.id + '.py'
        if self.aa:
            dst = ANSWER_PATH + self.id
        else:
            dst = BINARY_PATH + self.id
        try:
            os.mkdir(dst)
        except:
            pass
        dst += '/' + self.id + '.pyc'
        try:
            os.remove(src)
        except:
            pass
        try:
            os.symlink(ori, src)
        except:
            pass

        self.result = 0
        try:
            compile(src, dst, doraise=True, optimize=0)
        except PyCompileError as err:
            f = open(RESULT_PATH + self.id, mode='w+')
            f.write(str(err))  # try try try wtf the error output is?
            self.result = -2;

    compliers = [
        None,
        c,
        cxx,
        java,
        python,
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
        def __init__(self, cpu, mem):
            self.cpu = cpu
            self.mem = mem

        def __call__(self):
            import resource as res

            res.setrlimit(res.RLIMIT_CORE, (0, 0))
            res.setrlimit(res.RLIMIT_MEMLOCK, (0, 0))
            # res.setrlimit(res.RLIMIT_MSGQUEUE,(0,0))
            res.setrlimit(res.RLIMIT_NPROC, (0, 0))
            res.setrlimit(res.RLIMIT_FSIZE, (Tester.OUTPUT_MAX, Tester.OUTPUT_MAX))
            res.setrlimit(res.RLIMIT_CPU,(self.cpu,self.cpu))
            file = open('/tmp/out','w')
            print('mem='+str(self.mem),file=file)
            file.close()
            res.setrlimit(res.RLIMIT_AS,(self.mem,self.mem))
            res.setrlimit(res.RLIMIT_DATA,(self.mem,self.mem))

            ##os.chroot(CHROOT_PATH)
            os.nice(10)

    def c(self):
        ofile = TemporaryFile('w+t')
        if self.ua:
            bin = ANSWER_PATH + self.id + '/c' + self.id
        else:
            bin = BINARY_PATH + self.id + '/c' + self.id
        p = Popen(bin, stdin=self.ifile, stdout=ofile, universal_newlines=True,
                  preexec_fn=Tester.Limiter(self.lcpu, self.lmem), stderr=DEVNULL)
        p.wait()
        # accepted
        self.result = 0
        if p.returncode == -9:
            # time limit exceeded
            self.result = -5
        elif p.returncode == -11:
            # memory limit exceeded
            self.result = -6
        elif p.returncode == -25:
            # output limit exceeded
            self.result = -4
        elif p.returncode < 0:
            # run time error
            self.result = -3
        else:
            ofile.seek(0)
            if self.output != ofile.read(-1):
                # wrong answer
                self.result = -7

    def cxx(self):
        print("running cxx")
        ofile = TemporaryFile('w+t')
        if self.ua:
            bin = ANSWER_PATH + self.id + '/x' + self.id
        else:
            bin = BINARY_PATH + self.id + '/x' + self.id
        # preexec_fn=Tester.Limiter(self.lcpu, self.lmem)()
        p = Popen(bin, stdin=self.ifile, stdout=ofile, preexec_fn=Tester.Limiter(self.lcpu, self.lmem),
                  universal_newlines=True, stderr=DEVNULL)

        p.wait()
        #
        self.return_code = p.returncode
        print(self.return_code)
        #
        self.result = 0
        if p.returncode == -9:
            self.result = -5
        elif p.returncode == -11:
            self.result = -6
        elif p.returncode == -25:
            self.result = -4
        elif p.returncode < 0:
            self.result = -3
        else:
            ofile.seek(0)
            if self.output != ofile.read(-1):
                self.result = -7


    def java(self):
        ofile = TemporaryFile('w+t')
        if self.ua:
            dst = ANSWER_PATH + self.id
        else:
            dst = BINARY_PATH + self.id
        cmd = ['java', '-cp', dst, 'Main']
        p = Popen(cmd, stdin=self.ifile, stdout=ofile, universal_newlines=True,
                  preexec_fn=Tester.Limiter(self.lcpu, self.lmem), stderr=DEVNULL)
        p.wait()

        self.result = 0
        if p.returncode == -9:
            self.result = -5
        elif p.returncode == -11:
            self.result = -6
        elif p.returncode == -25:
            self.result = -4
        elif p.returncode < 0:
            self.result = -3
        else:
            ofile.seek(0)
            if self.output != ofile.read(-1):
                self.result = -7

    def pyc(self):
        ofile = TemporaryFile('w+t')
        if self.ua:
            dst = ANSWER_PATH + self.id + '.pyc'
        else:
            dst = BINARY_PATH + self.id + '.pyc'
        cmd = ['python', dst]
        p = Popen(cmd, stdin=self.ifile, stdout=ofile, universal_newlines=True,
                  preexec_fn=Tester.Limiter(self.lcpu, self.lmem), stderr=DEVNULL)
        p.wait()

        self.result = 0
        if p.returncode == -9:
            self.result = -5
        elif p.returncode == -11:
            self.result = -6
        elif p.returncode == -25:
            self.result = -4
        elif p.returncode < 0:
            self.result = -3
        else:
            # 文件定位到开头
            ofile.seek(0)
            if self.output != ofile.read(-1):
                self.result = -7

        pass

    testers = [
        None,
        c,
        cxx,
        java,
        pyc,
    ]

    def __init__(self, id, lang, input, output, cpu, mem, use_answer=False):
        self.id = str(id)
        self.lang = int(lang)
        self.ifile = TemporaryFile(mode='w+t')
        self.ifile.write(input)
        self.ifile.seek(0)
        self.output = str(output)
        self.lcpu = cpu
        self.lmem = mem
        self.ua = use_answer
        #
        self.return_code = 1024
        #
        Daemon.__init__(self)

    def _run(self):
        fun = self.testers[self.lang]
        fun(self)


Tester.init()


class Judger(Daemon):
    def __init__(self, submit):
        self.__submit = submit

        prob = submit.pid
        self.id = str(submit.id)
        self.lang = int(submit.lang)
        self.lcpu = int(prob.limit_time)
        self.lmem = int(prob.limit_memory)
        Daemon.__init__(self)

    def _run(self):
        c = Complier(self.id, self.lang)
        c.wait()
        if c.result:
            self.__submit.status = c.result
            self.__submit.save()
            return

        tlist = []
        for case in TestCase.objects.filter(pid__exact=self.__submit.pid):
            tlist.append(Tester(self.id, self.lang, case.input, case.output, self.lcpu, self.lmem))

        over = False
        for t in tlist:
            if over:
                t.cancel()
                continue
            t.wait()
            if t.result:
                over = True
                self.__submit.status = t.result
                self.__submit.save()

        if not over:
            self.__submit.status = 0
            self.__submit.save()
        # 递归删除二进制目录
        from shutil import rmtree

        rmtree(BINARY_PATH + self.id)
        #######
        print("over")
        print("test"+str(self.__submit.id)+"  "+str(tlist[0].return_code))
        self.__submit.return_code = tlist[0].return_code
        self.__submit.save()


Judger.init()


class Hacker(Daemon):
    def __init__(self, submit, case, success_save=False, hack_all=True):
        self.result = 0
        if submit.status != 0:
            self.result = 1
            return
        if submit.pid != case.pid:
            self.result = 2;
            return
        self.__case = case
        self.__submit = submit

        prob = submit.pid
        self.id = str(submit.id)
        self.lang = int(submit.lang)
        self.input = str(case.input)
        self.output = str(case.output)
        self.lcpu = int(prob.limit_time)
        self.lmem = int(prob.limit_memory)
        self.ss = success_save
        self.ha = hack_all
        Daemon.__init__(self)

    def _run(self):
        if self.result > 0:
            return
        c = Complier(self.id, self.lang)
        c.wait()
        if c.result != 0:
            self.result = c.result
            self.__submit.status = c.result
            self.__submit.save()
            return
        t = Tester(self.id, self.lang, self.input, self.output, self.lcpu, self.lmem)
        t.wait()
        if t.result == 0:
            self.result = 3
            return

        if self.ss:
            self.__case.save()
        self.__submit.status = t.result
        self.__submit.return_code = t.return_code
        self.__submit.save()

        if not self.ha:
            return
        for sub in Submit.objects.filter(pid__exact=self.__submit.pid, status__exact=0):
            Hacker(sub, self.__case, hack_all=False)

