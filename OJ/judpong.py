# -*- coding: utf-8 -*-

# Judger for SDUOJ
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from OJ.models import *
from subprocess import call, DEVNULL, Popen
import threading
import psutil
import lorun
import os
import getpass
import codecs
import resource as res
from threading import Thread, Event
from queue import Queue
from tempfile import TemporaryFile, NamedTemporaryFile
from django.core.files.base import ContentFile


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

def runone(p_path, in_path, out_path, user_path, time_limit, memory_limit, lang):
    fin = open(in_path)
    ftemp = open(user_path, 'w')
    if type(p_path)==str:
        p_path=[p_path]

    
    runcfg = {
        'args':p_path,
        'fd_in':fin.fileno(),
        'fd_out':ftemp.fileno(),
        'timelimit':int(time_limit*1000), #in MS
        'memorylimit':int(memory_limit*2/1024+1024), #in KB
    }
    if lang!='Java':
        runcfg['trace'] = True
        runcfg['calls'] = [0,1,2,3,5,9,10,11,12,21,59,158,231]
        runcfg['files'] = {}
    else:
        runcfg['memorylimit']=0x3f3f3f3f3f3f3f3f
    # print('Runone Config:')
    # print(runcfg)
    rst = lorun.run(runcfg)
    # print('Runone Result:')
    # print(rst)
    fin.close()
    ftemp.close()
    
    if rst['result'] == 0:
        if rst['memoryused']>memory_limit/1024:
            rst['memoryused']=memory_limit/1024
            rst['result']=3 #MLE


    if rst['result'] == 0:
        ftemp = open(user_path, 'r')
        output = ftemp.read().strip()
        ftemp.close()
        output = output.replace(chr(13),'')

        fout = open(out_path,'r')
        right = fout.read().strip()
        fout.close()
        right = right.replace(chr(13),'')

        if right != output:
            if ''.join(output.split()) == ''.join(right.split()):
                rst['result'] = 1   #PE
            else:
                rst['result'] = 4   #WA
    return rst


class Complier():
    def c(self):
        ori = ORIGIN_PATH + self.id
        src = SOURCE_PATH + self.id + '.c'
        if self.aa:
            dst = ANSWER_PATH + self.id
        else:
            dst = BINARY_PATH + self.id
        try:
            os.mkdir(dst)
            os.system("sudo chmod 777 %s"%dst)
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
        cmd = 'gcc %s -o %s -fno-asm -Wall -lm -std=c99 -DONLINE_JUDGE -O2'%(src,dst)
        sudocmd = 'sudo su compileuser -c \'%s\''%cmd
        self.result = call(sudocmd, stdout=DEVNULL, stderr=open(RESULT_PATH + self.id, mode='w+'),shell=True)
        if self.result > 0:
            # syntax error
            self.result = -1
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
            os.system("sudo chmod 777 %s"%dst)
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
        cmd = 'g++ %s -o %s -fno-asm -Wall -lm -std=c++0x -DONLINE_JUDGE -O2'%(src,dst)
        sudocmd = 'sudo su compileuser -c \'%s\''%cmd
        self.result = call(sudocmd, stdout=DEVNULL, stderr=open(RESULT_PATH + self.id, mode='w+'),shell=True)
        if self.result > 0:
            self.result = -1
        elif self.result < 0:
            self.result = -1
        else:
            #cmd = ['sudo','jk_cp','-j','/jail',dst]
            #print(cmd)
            #cp = Popen(cmd)
            #cp.wait()
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
        cmd = ['javac', '-J-Duser.language=en ', '-d', dst, src]
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
        #Daemon.__init__(self)

    def compile(self):
        fun = self.compliers[self.lang]
        fun(self)


#Complier.init()


class Tester():
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


    def updateRst(self,rst):
        in_path = self.ifile.name
        out_path = self.ofile.name
        user_path = self.userofile.name
        if self.isSPJ:
            chkcmd = ['sudo','python3',self.checker.name,user_path]
            chkrst = call(chkcmd, stdin=self.ifile, stdout=open(self.check_rst.name, mode='w+'), stderr=DEVNULL)
            chkrst = chkrst if chkrst<128 else chkrst-256
            print("Check Result Path:")
            print(self.check_rst.name)
            print("Check Return Code:")
            print(chkrst)
        self.cpu_used = 0
        self.memory_used = 0
        self.cpu_used = rst['timeused']
        self.memory_used = rst['memoryused']
        if self.isSPJ:
            # print("rst['result']")
            # print(rst['result'])
            if rst['result'] == 2: 
                self.cpu_used = min(rst['timeused'],self.cpu_limit*1000)
                self.result = -5 #Time Limit Exceeded
            elif rst['result'] == 3: 
                self.memory_used = min(rst['memoryused'],self.memory_limit/1024)
                self.result = -6 #Memory Limit Exceeded
            elif rst['result'] == 5: 
                self.result = -3 #Runtime Error
            elif rst['result'] == 6: 
                self.result = -4 #Output Limit Exceeded
            elif rst['result'] == 7: 
                self.result = -1 #Compile Error
            elif rst['result'] == 0 or rst['result'] == 4:
                self.result = chkrst #Return from Special Judge
            else:
                pass    #TODO
        else:
            if rst['result'] == 0:
                self.result = 0 #Accept
            elif rst['result'] == 1: 
                self.result = -8 #Presentation Error
            elif rst['result'] == 2: 
                self.cpu_used = min(rst['timeused'],self.cpu_limit*1000)
                self.result = -5 #Time Limit Exceeded
            elif rst['result'] == 3: 
                self.memory_used = min(rst['memoryused'],self.memory_limit/1024)
                self.result = -6 #Memory Limit Exceeded
            elif rst['result'] == 4: 
                self.result = -7 #Wrong Answer
            elif rst['result'] == 5: 
                self.result = -3 #Runtime Error
            elif rst['result'] == 6: 
                self.result = -4 #Output Limit Exceeded
            elif rst['result'] == 7: 
                self.result = -1 #Compile Error
            else:
                pass    #TODO

    def c(self):
        #ofile = TemporaryFile('w+t')
        # if self.ua:
        #     bin = ANSWER_PATH + self.id + '/c' + self.id
        # else:
        bin = BINARY_PATH + self.id + '/c' + self.id

        in_path = self.ifile.name
        out_path = self.ofile.name
        user_path = self.userofile.name
        rst = runone(bin, in_path, out_path, user_path, self.cpu_limit, self.memory_limit,'C')
        self.updateRst(rst)




    def cxx(self):
        ofile = TemporaryFile('w+t')
        # if self.ua:
        #     bin = ANSWER_PATH + self.id + '/x' + self.id
        # else:
        bin = BINARY_PATH + self.id + '/x' + self.id

        in_path = self.ifile.name
        out_path = self.ofile.name
        user_path = self.userofile.name
        rst = runone(bin, in_path, out_path, user_path, self.cpu_limit, self.memory_limit,'C++')
        self.updateRst(rst)



    def java(self):
        ofile = TemporaryFile('w+t')
        # if self.ua:
        #     dst = ANSWER_PATH + self.id
        # else:
        dst = BINARY_PATH + self.id
        # careful about the maxheapsize for JVM,should be set
        cmd = ['java', '-XX:MaxHeapSize=1024m','-Djava.security.manager','-cp', dst, 'Main']


        in_path = self.ifile.name
        out_path = self.ofile.name
        user_path = self.userofile.name
        rst = runone(cmd, in_path, out_path, user_path, self.cpu_limit, self.memory_limit,'Java')
        self.updateRst(rst)

       

    testers = [
        None,
        c,
        cxx,
        java,
    ]

    # def __init__(self, id, lang, input, output, cpu_limit, memory_limit, score, use_answer=False):
    #submit.id, submit.lang, case.input, case.output, problem.limit_time, problem.limit_memory, case.score
    def __init__(self, problem, submit, case):
        self.id = str(submit.id)
        self.lang = int(submit.lang)
        self.ifile = NamedTemporaryFile(mode='w+',suffix='.in')
        self.ifile.write(case.input)
        self.ifile.seek(0)
        self.ofile = NamedTemporaryFile(mode='w+',suffix='.out')
        self.ofile.write(case.output)
        self.ofile.seek(0)
        self.isSPJ=problem.isSPJ
        if self.isSPJ:
            self.checker=problem.checker
            submit.check_rst.save(name=str(submit.id), content=ContentFile(''))
            self.check_rst=submit.check_rst
        self.userofile = NamedTemporaryFile(mode='w+',suffix='.out')
        self.userofile.seek(0)
        # self.output = str(case.output)
        self.cpu_limit = problem.limit_time
        self.memory_limit = problem.limit_memory
        self.score = case.score
        # for java, give extra 25M, double the original cpu time
        if self.lang == 3:
            self.memory_limit = problem.limit_memory + 26214400
            self.cpu_limit = problem.limit_time * 2
        #self.ua = use_answer
        # set the stauts for 'running'
        self.result = 3
        #Daemon.__init__(self)

    def testcase(self):
        fun = self.testers[self.lang]
        fun(self)


#Tester.init()

def judgePong(submit):
    print("New Pong Judger Thread judging %d"%int(submit.id))
    #codecs.open('demojudger.log', 'w', 'utf8').write("New Pong Judger Thread judging %d."%int(submit.id))
    problem = submit.pid
    #print("Begin Compiling...")
    c = Complier(submit.id, submit.lang)
    c.compile()
    #c.wait()
    
    if c.result:
        #print("Compile failed.")
        submit.status = c.result
        submit.save()
        return True
    #print("Compile finished.")
    caseList = TestCase.objects.filter(pid__exact=submit.pid)
    testList = []
    for case in caseList:
        # testList.append(Tester(submit.id, submit.lang, case.input, case.output, problem.limit_time, problem.limit_memory, case.score))
        testList.append(Tester(problem,submit,case))
    erroroccur = False
    for test in testList:
        test.testcase()
        if test.result:
            erroroccur = True
            errortest = test
            submit.status = test.result
            submit.run_time = max(submit.run_time,test.cpu_used)
            submit.run_memory = max(submit.run_memory,test.memory_used)
        else:
            submit.status = test.result
            submit.run_time = max(submit.run_time,test.cpu_used)
            submit.run_memory = max(submit.run_memory,test.memory_used)
            submit.score += test.score
    if erroroccur:
        submit.status = errortest.result
        submit.run_time = errortest.cpu_used
        submit.run_memory = errortest.memory_used
    for test in testList:
        test.ifile.close()
        test.ofile.close()
        test.userofile.close()
    from shutil import rmtree
    rmtree(BINARY_PATH + str(submit.id))
    problem_try = UserInfo.objects.get(id=submit.uid.info.id).problem_try
    submit.uid.info.problem_try = problem_try + 1
    submit.uid.info.problems_try.add(submit.pid)
    if (submit.status == 0):
        problem_ac=Submit.objects.filter(pid=submit.pid, uid=submit.uid, status=0).count()
        if(problem_ac != 0):
            print('problem %s has been ACed by %s for %s times'%(str(submit.pid),str(submit.uid),str(problem_ac)))
        else:
            print('adding num.ac')
            submit.uid.info.problem_ac += 1
            submit.uid.info.problems_ac.add(submit.pid)
    submit.uid.info.save()
    submit.save()
    return True
