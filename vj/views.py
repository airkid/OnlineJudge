# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, Http404, HttpResponseRedirect, render
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.template import Context, RequestContext, loader
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Q,Max
from django.core.files.base import ContentFile
from datetime import timedelta
from vj.models import *
from OJ.models import UserInfo as ojInfo
from django.utils import timezone
from collections import OrderedDict
import datetime
import pytz
import re
import json
import pymysql
import time
import base64,os,sys
project_path = os.path.abspath('/home/sduacm/OnlineJudge')
sys.path.append(project_path)
code_path = project_path+'/JudgeFiles/codes/'

LIST_NUMBER_EVERY_PAGE = 20
PAGE_NUMBER_EVERY_PAGE = 7

LANG_DICT = {0: 'G++', 1: 'GCC', 2: 'C++', 3: 'C', 4: 'Pascal', 5: 'Java', 6: 'C#', 7: 'Python'}
LANGUAGE = {
        'G++' : '0',
        'GCC' : '1',
        'C++' : '2',
        'C' : '3',
        'Pascal' : '4',
        'Java' : '5',
        'C#' : '6',
        'Python' : '7',
        }

def is_valid_date(strdate):  
    try:  
        time.strptime(strdate, "%Y-%m-%d %H:%M:%S")  
        return True  
    except:
        return False  


def ren2res(template, req, dict={}):
    if req.user.is_authenticated():
        p = re.compile('^[0-9a-zA-Z_]+$')
        dict.update({'user': {  'id': req.user.id, 
                                'username': req.user.get_username(),
                                'is_staff':req.user.is_staff,
                                #'sid':req.user.vj_info.sid,
                                #'nickname':req.user.vj_info.nickname,
                                #'school':req.user.vj_info.school
                                }})
    else:
        dict.update({'user': False})
    """
    if req:
        return render_to_response(template, dict, context_instance=RequestContext(req))
    else:
        return render_to_response(template, dict)
        """
    return render(req,template,dict);
def home(req):
    return ren2res("vj/home.html", req, {})

def login(req):
    if req.method == 'GET':
        if req.user.is_anonymous():
            if req.GET.get('next'):
                req.session['next'] = req.GET.get('next')
            return ren2res("vj/login.html", req, {})
        else:
            return HttpResponseRedirect("/vj/")
    elif req.method == 'POST':
        user = auth.authenticate(username=req.POST.get('username'), password=req.POST.get('password'))
        if user is not None:
            auth.login(req, user)
            next = req.session.get('next')
            if next:
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect('/vj/')
        else:
            return ren2res("vj/login.html", req, {'err': "Wrong Username or Password!"})

def register(req):
    if req.method == 'GET':
        if req.user.is_anonymous():
            if req.GET.get('next'):
                req.session['next'] = req.GET.get('next')
            return ren2res('vj/register.html', req, {})
        else:
            return HttpResponseRedirect('/vj/')
    elif req.method == 'POST':
        username = req.POST.get("username")
        school = req.POST.get('school')
        sid = req.POST.get('sid')
        nickname = req.POST.get('nickname')
        result = User.objects.filter(username=username);
        p = re.compile('^[0-9a-zA-Z_]+$')
        if len(username) == 0 or p.match(username)==None:
            return ren2res('vj/register.html', req, {'err': "Invalid username"})
        elif len(result) != 0:
            return ren2res('vj/register.html', req, {'err': "This username has been registered! Try another"})
        else:
            pw1 = req.POST.get('pw1')
            if pw1 == "":
                return ren2res('vj/register.html', req, {'err': "Password can't be null", 'account': account})
            pw2 = req.POST.get('pw2')
            if pw1 != pw2:
                return ren2res('vj/register.html', req, {'err': "Password not consistent", 'account': account})
            else:
                newuser = User()
                newuser.username = username
                newuser.set_password(pw1)
                newuser.is_staff = 0
                newuser.is_active = 1
                newuser.is_superuser = 0
                newuser.save()
                newuser = auth.authenticate(username=username, password=pw1)
                auth.login(req, newuser)

                newuserinfo = UserInfo(id=newuser)
                newuserinfo.school = school 
                newuserinfo.sid = sid 
                newuserinfo.nickname = nickname 
                newuserinfo.save()
                ojinfo = ojInfo(id=newuser)
                ojinfo.school = school 
                ojinfo.sid = sid 
                ojinfo.nickname = nickname 
                ojinfo.save()
                next = req.session.get('next')
                if next:
                    return HttpResponseRedirect(next)
                else:
                    return HttpResponseRedirect('/vj/')


def logout(req):
    auth.logout(req)
    return HttpResponseRedirect('/vj/')

def function():
    pass

def problem(req):
    pg = int(req.GET.get('pg', 1))
    originoj= req.POST.get('originoj',"")
    problemid=req.POST.get('problemid',"")
    title=req.POST.get('title',"")
    if originoj or problemid or title:
        qs = Problem.objects.filter(Q(originoj__icontains=originoj) & Q(problemid__icontains=problemid) & Q(title__icontains=title))
        pg = 1
    else:
        qs = Problem.objects.all()
    qs = qs.order_by('-updatetime')
    idxstart = (pg - 1) * LIST_NUMBER_EVERY_PAGE
    idxend = pg * LIST_NUMBER_EVERY_PAGE

    max = qs.count() // 20 + 1

    if (pg > max):
        raise Http404("no such page")
    start = pg - PAGE_NUMBER_EVERY_PAGE
    if start < 1:
        start = 1
    end = pg + PAGE_NUMBER_EVERY_PAGE
    if end > max:
        end = max

    lst = qs[idxstart:idxend]
    lst = list(lst)
    aclst = []
    trylst = []
    '''
    if req.user.is_authenticated():
        user = req.user
        for item in lst:
            if item.aceduser.filter(id=user.info.id):
                aclst.append(item.id)
            elif item.trieduser.filter(id=user.info.id):
                trylst.append(item.id)
    '''
#        print(aclst)
#        print('trylst')
#        print(trylst)
    return ren2res("vj/problem.html", req, {'pg': pg, 'page': list(range(start, end + 1)), 'list': lst, 'aclst':aclst, 'trylst':trylst
        ,'originoj':originoj ,'problemid':problemid ,'title':title })


#db = pymysql.connect("211.87.227.207","vj","vDpAZE74bJrYahZKmcvZxwc","vj")

def problem_detail(req, proid):
    problem = Problem.objects.get(proid=proid)
    #print("Requesting prob:%s %d"%(problem.title,problem.proid))
    return ren2res("vj/problem/problem_detail.html", req, {'problem': problem})

@login_required
def problem_discuss(req,proid):
    #pid=req.GET.get("proid")
    pro = Problem.objects.get(proid=proid)
    if req.method == 'GET' :
         return render(req,'vj/problem/problem_discuss.html',{'problem':pro,'list': Discuss.objects.filter(proid=proid)})
    elif req.method == 'POST' :
        discuss = Discuss(uid = req.user,proid=pro, content = req.POST.get('content'), time=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        discuss.save()
        return HttpResponseRedirect("vj/problem/%s/discuss/"%proid)

@login_required
def problem_submit(req, proid):
    global project_path
    if req.method == 'GET':
        return ren2res("vj/problem/problem_submit.html", req, {'problem': Problem.objects.get(proid=proid)})
    elif req.method == 'POST':
        status = Status(user=req.user, pro=Problem.objects.get(proid=proid), lang=req.POST.get('lang'), result='Waiting', \
            cid=-1,time=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        temp = Status.objects.aggregate(maxRunid=Max('runid'))
        # if temp['maxRunid']==None:
        #     temp['maxRunid']=1000
        status.source_code = str(temp['maxRunid']+1)
        if req.POST.get('code'):
            f = open(code_path + str(status.source_code), 'w')
            f.write(req.POST.get('code'))
            f.close()
            #status.code = base64.b64encode(bytes(req.POST.get('code'), 'utf-8'))
        else:
            return ren2res("vj/problem/problem_submit.html", req,
                           {'problem': Problem.objects.get(proid=proid), 'err': "No Submit!"})
        
        status.save()
        #sub.source_code.save(name=str(sub.id), content=content_file)
        #sub.save()

        return HttpResponseRedirect("/vj/status/")

def status(req):
    pro_id = req.GET.get('pro_id')

    runid= req.POST.get('runid',"")
    if runid=='':
        runid = req.GET.get('runid',"")
    #以post为主
    originoj= req.POST.get('originoj',"")
    problemid= req.POST.get('problemid',"")
    title= req.POST.get('title',"")
    result= req.POST.get('result',"")
    lang= req.POST.get('lang',"")
    uid= req.POST.get('uid',"")
    if pro_id:
        query = Status.objects.filter(pro_id=pro_id).all().order_by('-runid')
    elif runid or originoj or problemid or title or result or lang or uid:
        query = Status.objects.filter(Q(runid__icontains=runid) & Q(pro__originoj__icontains=originoj) & Q(pro__problemid__icontains=problemid)
            & Q(pro__title__icontains=title) & Q(result__icontains=result) & Q(lang__icontains=lang) & Q(user__username__icontains=uid) ).order_by('-runid')
    else:
        query = Status.objects.all().order_by('-runid')

    #print(len(query))

    pg = req.GET.get('pg')
    if not pg:
        pg = 1
    pg = int(pg)

    max_cnt = query.count() // 20 + 1
    start = max(pg - PAGE_NUMBER_EVERY_PAGE, 1)
    end = min(pg + PAGE_NUMBER_EVERY_PAGE, max_cnt)

    lst = query[(pg - 1) * LIST_NUMBER_EVERY_PAGE:pg * LIST_NUMBER_EVERY_PAGE]
    #print(len(lst))

    return ren2res('vj/status.html', req, {'pro_id': pro_id, 'page': range(start, end + 1), 'list': lst , 'LANG_DICT':LANG_DICT
        , 'runid':runid, 'originoj':originoj, 'problemid':problemid, 'title':title
        , 'result':result, 'lang':lang, 'uid':uid})


@login_required
def profile(req):
    userinfo = UserInfo.objects.get(id=req.user)
    if req.method == 'GET':
        return ren2res('vj/profile.html',req,{"userinfo":userinfo})
    else:
        user = req.user
        if not user:
            return ren2res('vj/profile.html',req,{})
        else:
            pw = req.POST.get('password')
            if not user.check_password(pw):
                return ren2res('vj/profile.html', req, {'err': "Wrong password", "userinfo":userinfo})
            
            userinfo.nickname = req.POST.get('nickname')
            if len(user.info.nickname)==0:
                return ren2res('vj/profile.html', req, {'err': "Nickname can't be null", "userinfo":userinfo})
            userinfo.school = req.POST.get('school')
            userinfo.sid = req.POST.get('sid')
            userinfo.save()
            
            npw1 = req.POST.get('npw1')
            if npw1 == "":
                return ren2res('vj/profile.html', req, {'err': "User Profile Updated", "userinfo":userinfo})
            npw2 = req.POST.get('npw2')
            if npw1 != npw2:
                return ren2res('vj/profile.html', req, {'err': "New Password not consistent", "userinfo":userinfo})
            else:
                user.set_password(npw1)
                user.save()
                return ren2res("vj/login.html", req, {"userinfo":userinfo})
        return HttpResponseRedirect('/vj/')

@login_required
def show_source(req):
    solution_id = req.GET.get('solution_id')
    query = Status.objects.filter(runid=solution_id)
    if len(query) == 0:
        raise Http404
    elif query[0].user.id != req.user.id and not req.user.is_staff:
        raise Http404
    else:
        status = query[0]
        
        f = open(code_path + str(status.source_code), 'r')
        code = f.read()
        DISP_LANG_DICT = {0: 'cpp', 1: 'c', 2: 'cpp', 3: 'c', 4: 'pascal', 5: 'java', 6: 'C#', 7: 'python'}
        return ren2res('vj/show_source.html', req, {'status': status, 'code': code, 'lang': DISP_LANG_DICT[status.lang]})

#new add ,need change

def contest(req):
    name = req.POST.get('name',"")
    username = req.POST.get('username',"")
    if name or username:
        query = Contest.objects.filter(Q(name__icontains=name) & Q(uid__username__icontains=username)).order_by("-start_time")
    else:
        query = Contest.objects.all().order_by("-start_time")
    pg = req.GET.get('pg')
    if not pg:
        pg = 1
    pg = int(pg)

    max_cnt = query.count()
    start = max(pg - PAGE_NUMBER_EVERY_PAGE, 1)
    end = min(pg + PAGE_NUMBER_EVERY_PAGE, max_cnt)

    lst = query[(pg - 1) * LIST_NUMBER_EVERY_PAGE:pg * LIST_NUMBER_EVERY_PAGE]

    return ren2res('vj/contest.html', req, {'page': range(start, end + 1), 'list': lst ,'name': name, 'username':username})

@login_required
def contest_add(req):
    return render(req,'vj/contest/contest_add.html',{'user':req.user})
    #return ren2res('/contest/contest_add.html',req,{'user':req.user})

def addcontest_get_problem_title(req):
    originoj = req.GET.get('originoj')
    probid = req.GET.get('probid')
    try:
        result = Problem.objects.get(originoj=originoj,problemid=probid)
        if result:
            return HttpResponse(result.title)
        else:
            return HttpResponse("No Such Problem")    
    except:
        return HttpResponse("No Such Problem")


regex = re.compile(r'((?P<hours>\d+?)hr)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')

def parse_time(time_str):
    parts = regex.match(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for (name, param) in parts.iteritems():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)

@login_required
def contest_add_process(req):
    #author type openness title begin duration problems
    author = req.POST.get("author")
    typec = req.POST.get("type")
    openness = req.POST.get("openness")
    password = req.POST.get("password")
    title = req.POST.get("title")
    begin = req.POST.get("begin")
    duration = req.POST.get("duration")
    problems = req.POST.get("problems")
    description = req.POST.get("description")

    if openness=='private' and password=='':
        return HttpResponse('password error')
    elif openness=='public':
        password = ''

    if not is_valid_date(begin):
        return HttpResponse("begin error")
    
    point = 0
    for i in range(0,len(duration)):
        if duration[i] == ':':
            point = i
    if duration[0:point].isdigit() and duration[point+1:].isdigit():
        duration = timedelta(hours=int(duration[0:point]),minutes=int(duration[point+1:]))
    else:
        return HttpResponse("duration error")

    problemsArr = []
    scoreArr = []
    originoj = ""
    problemid = ""
    score = ""
    for i in range(0,len(problems)-1):
        if problems[i] == '$':
            j = i
            while problems[j] != '|':
                j = j+1
            originoj = problems[i+1:j]
            i = j
            j = j+1
            while problems[j] != '|':
                j = j+1
            problemid = problems[i+1:j]
            i = j
            j = j+1
            while problems[j] != '$':
                j = j+1
            score = problems[i+1:j]
            if typec == 'icpc':
                score = '1'
            i = j
            problemsArr.append(Problem.objects.get(originoj=originoj,problemid=problemid))
            scoreArr.append(score)
        else:
            continue


    cont = Contest(uid=req.user,name=title,typec=typec,start_time=begin,duration_time=duration, private=(openness=='private'),
     password=password, description=description)
    cont.save()
    cont.accounts.add(req.user.vj_info)
    cont.save()

    # print(cont)
    
    for i in range(0,len(problemsArr)):
        cp = Contest_problems(contest=cont,problem=problemsArr[i],score=scoreArr[i],order=i)
        cp.save()

    return HttpResponse("/vj/contest/")

@login_required
def contest_modify(req,cid):
    contest = Contest.objects.get(id=cid)
    if req.user != contest.uid:
        return HttpResponse("No Permission!")
    problems = contest.get_problem_list()
    return ren2res("vj/contest/contest_modify.html", req, {'contest': contest,'problems': problems})
@login_required
def contest_modify_process(req,cid):
    author = req.POST.get("author")
    typec = req.POST.get("type")
    openness = req.POST.get("openness")
    password = req.POST.get("password")
    title = req.POST.get("title")
    begin = req.POST.get("begin")
    duration = req.POST.get("duration")
    problems = req.POST.get("problems")
    description=req.POST.get("description")
    #print("Clar ",clarification)

    if openness=='private' and password=='':
        return HttpResponse('password error')
    elif openness=='public':
        password = ''

    if not is_valid_date(begin):
        return HttpResponse("begin error")
    
    point = 0
    for i in range(0,len(duration)):
        if duration[i] == ':':
            point = i
    if duration[0:point].isdigit() and duration[point+1:].isdigit():
        duration = timedelta(hours=int(duration[0:point]),minutes=int(duration[point+1:]))
    else:
        return HttpResponse("duration error")

    problemsArr = []
    scoreArr = []
    originoj = ""
    problemid = ""
    score = ""
    for i in range(0,len(problems)-1):
        if problems[i] == '$':
            j = i
            while problems[j] != '|':
                j = j+1
            originoj = problems[i+1:j]
            i = j
            j = j+1
            while problems[j] != '|':
                j = j+1
            problemid = problems[i+1:j]
            i = j
            j = j+1
            while problems[j] != '$':
                j = j+1
            score = problems[i+1:j]
            if typec == 'icpc':
                score = '1'
            i = j
            problemsArr.append(Problem.objects.get(originoj=originoj,problemid=problemid))
            scoreArr.append(score)
        else:
            continue

    cont = Contest.objects.get(id=cid)
    cont.name = title
    cont.typec = typec
    cont.start_time = begin
    cont.duration_time = duration
    cont.private =(openness=='private')
    cont.password=password
    cont.description=description
    cont.last_submit_id=0
    cont.rank=json.loads("{}")
    cont.save()
    cont.problems.clear()
    cont.save()
    for i in range(0,len(problemsArr)):
        cp = Contest_problems(contest=cont,problem=problemsArr[i],score=scoreArr[i],order=i)
        cp.save()
    return HttpResponse("/vj/contest/"+cid+"/")

@login_required
def contest_detail(req, cid):
    contest = Contest.objects.get(id=cid)
    password = ""
    if req.POST.get('password'):
        password = req.POST.get('password')
    # time = datetime.datetime.now(pytz.timezone(pytz.country_timezones('cn')[0]))
    # time = datetime.datetime.now()
    time = timezone.now()
    if time > contest.start_time:
        start = True
    else:
        start = False
    if contest.private:
        #print(problems)
        # print('contest.accounts')
        # print(contest.accounts.all())
        if str(contest.password) == password :
            try:
                contest.accounts.add(req.user.vj_info)
                contest.save()
            except Exception as e:
                print(str(e))
        if req.user.is_superuser==False and req.user.vj_info not in contest.accounts.all() :
            return ren2res("vj/contest/contest.html", req, {'contest': contest, 'err': "You do not have access to this contest."})
    if start:
        problems = contest.get_problem_list()
        length = len(problems)
        problems_status = [0 for i in range(length)]

        for i in range(length):
            problems[i].append(len(Status.objects.filter(user = req.user,cid = cid,pro = problems[i][2],result = 'Accepted')))#changes
        # print(problems)
        return ren2res("vj/contest/contest.html", req, {'contest': contest, 'problems': problems,'isAuthor':(req.user==contest.uid)})
    else:
        return ren2res("vj/contest/contest.html", req, {'contest': contest, 'err': "Just wait."})


@login_required
def contest_get_problem(req, cid):
    if req.is_ajax():
        contest = Contest.objects.get(id=cid)
        pid = req.GET.get('pid')
        t = loader.get_template('vj/contest/contest_problem.html')
        problem = Problem.objects.get(proid=pid)
        if contest.private:
            if req.user.is_superuser==False and req.user.vj_info not in contest.accounts.all() :
                problem = []
        #content_html = t.render(Context({'problem': problem, 'user' : req.user}))
        # return HttpResponse(content_html)
        return render(req,'vj/contest/contest_problem.html',{'problem': problem, 'user' : req.user})

def get_contest_status_list(req,cid,pg):
    contest = Contest.objects.get(id=cid)
    t = loader.get_template('vj/contest/contest_status.html')
    status_list = Status.objects.filter(cid=cid).order_by('-runid')
    if contest.private:
        if req.user.is_superuser==False and req.user.vj_info not in contest.accounts.all() :
            status_list = []
    max_cnt = status_list.count() // 20 + 1
    start = max(pg - PAGE_NUMBER_EVERY_PAGE, 1)
    end = min(pg + PAGE_NUMBER_EVERY_PAGE, max_cnt)

    lst = status_list[(pg - 1) * LIST_NUMBER_EVERY_PAGE:pg * LIST_NUMBER_EVERY_PAGE]
    return lst,start,end

@login_required
def contest_status(req, cid):#has understood
    if req.is_ajax():
        pg = req.GET.get('pg')
        if not pg:
            pg = 1
        pg = int(pg)
        lst,start,end = get_contest_status_list(req,cid,pg)
        
        # content_html = t.render(Context({'status_list': lst, 'page': range(start, end + 1), 'contest_id': cid, 'user': req.user}))
        # return HttpResponse(content_html)
        return render(req,'vj/contest/contest_status.html',{'status_list': lst, 'page': range(start, end + 1), 'contest_id': cid, 'user': req.user})
    else:
        raise Http404


@login_required
def contest_submit(req, cid):
    contest = Contest.objects.get(id=cid)
    #time = datetime.datetime.now(pytz.timezone(pytz.country_timezones('cn')[0]))
    # time1=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    time=timezone.now()
    # print(contest.start_time + contest.duration_time)
    if time > contest.start_time + contest.duration_time:
        finish = True
    else:
        finish = False

    if contest.private:
        if req.user.is_superuser==False and req.user.vj_info not in contest.accounts.all() :
            return HttpResponseRedirect("/vj/contest/%d/status/"%int(cid))
            #return HttpResponseRedirect("/contest/" + cid + "/")

    if req.method == 'GET':
        return HttpResponseRedirect("/vj/contest/%d/status/"%int(cid))
        #return ren2res("contest/contest_submit.html", req, {'contest': contest, 'problems': contest.get_problem_list()})
    elif req.method == 'POST':
        proid = req.POST.get('proid')
        status = Status(user=req.user, pro=Problem.objects.get(proid=proid), lang=req.POST.get('lang'), result='Waiting', time=time)

        if not finish:
            status.cid = contest.id
        else:
            status.cid = -1

        status.save()
        temp = Status.objects.aggregate(maxRunid=Max('runid'))
        status.source_code = str(temp['maxRunid']+1)

        if req.POST.get('code') :
            f = open(code_path + str(status.source_code), 'w')
            f.write(req.POST.get('code'))
            f.close()

        status.save()
    if not finish:
        lst,start,end = get_contest_status_list(req,cid,1)
        return render(req,'vj/contest/contest_status.html',{'status_list': lst, 'page': range(start, end + 1), 'contest_id': cid, 'user': req.user})
        #return HttpResponseRedirect("/contest/%d/"%int(cid))
        """
        status_list = Status.objects.filter(cid=cid).order_by('-runid')
        pg = 1
        max_cnt = status_list.count() // 20 + 1
        start = max(pg - PAGE_NUMBER_EVERY_PAGE, 1)
        end = min(pg + PAGE_NUMBER_EVERY_PAGE, max_cnt)

        lst = status_list[(pg - 1) * LIST_NUMBER_EVERY_PAGE:pg * LIST_NUMBER_EVERY_PAGE]
        return render(req,'contest/contest_status.html',{'status_list': lst, 'page': range(start, end + 1), 'contest_id': cid, 'user': req.user})
        #return HttpResponseRedirect("../status/")
        """
    else:
        #return HttpResponseRedirect("/status/")
        return HttpResponseRedirect("/vj/status/?runid=" + str(status.runid))
        #need change end

def contest_time(req, cid):#don't need change
    if req.is_ajax():
        contest = Contest.objects.get(id = cid)
        startTime = contest.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')

        days = contest.duration_time.days
        seconds = contest.duration_time.seconds

        durationTime = days * 3600 * 24 + seconds;

        timeData = {'start' : startTime,
                    'duration' : durationTime}

        print(timeData)
        return JsonResponse(timeData)

@login_required
def contest_clarification(req,cid):
    #pid=req.GET.get("proid")
    #pro = Problem.objects.get(proid=proid)
    contest = Contest.objects.get(id = cid)
    isAuthor = req.user == contest.uid
    print('OUT POST clar', req.POST.get('clar')) 
    print('OUT GET clar', req.GET.get('clar')) 
    if not req.POST.get('clar') :
        #print('GET count', Contest_clarification.objects.filter(contest=contest).count())
        return render(req,'vj/contest/contest_clar.html',{'contest':contest,'list': Contest_clarification.objects.filter(contest=contest).order_by('-time'), 'isAuthor':isAuthor})
    else :
        #print('POST count', Contest_clarification.objects.filter(contest=contest).count())
        #print('POST clar', req.POST.get('clar')) 
        if isAuthor:
            contest_clarification = Contest_clarification(contest = contest, clarification = req.POST.get('clar'),
                time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
            contest_clarification.save()
        return render(req,'vj/contest/contest_clar.html',{'contest':contest, 'list': Contest_clarification.objects.filter(contest=contest).order_by('-time'), 'isAuthor':isAuthor })

def dateToInt(date, field):
     if field == 0:
         return date.days * 24 * 60 + date.seconds // 60
     else:
         return date.days * 24 * 60 *60  + date.seconds

@login_required
def contest_rank(req, cid):
    try:
        if req.is_ajax():
            contest = Contest.objects.get(id = cid)
            if contest.private:
                if req.user.is_superuser==False and req.user.vj_info not in contest.accounts.all() :
                    return JsonResponse(json.loads("{}"))
            rank_cache = contest.rank
            # print("rank_cache:")
            # print(rank_cache)
            status_list = Status.objects.filter(cid = cid).filter(runid__gt = contest.last_submit_id).order_by("time")
            # print("status_list")
            # print(status_list)
            rank_dict = json.loads(rank_cache)
            # print("rank_dict")
            # print(rank_dict)
            statsinfo = {}
            pos = 0
            problem_list = contest.get_problem_list()
            length = len(problem_list)
            print(problem_list)

            
            if contest.last_submit_id==0:
                rank_dict["statsinfo"] = [{} for i in range(length)]
                for item in problem_list:
                    rank_dict["statsinfo"][pos] = {"probid" : chr(pos + 65) ,"acNum" : 0, "tryNum" : 0}
                    statsinfo[item[2].title] = {"pos" : pos}
                    pos += 1
            else:
                for item in problem_list:
                    statsinfo[item[2].title] = {"pos" : pos}
                    pos += 1
            print("Contest last id:%d"%(int(contest.last_submit_id)))
            for item in status_list:
                if item.user.is_staff :
                    continue
                name = item.user.username
                print(item.runid)
                contest.last_submit_id = max(contest.last_submit_id, item.runid)
                if name not in rank_dict.keys():
                    rank_dict[name] = {"name" : name, "solved":0, "penalty":0, "probs" : [{"failNum" : 0, "acNum" : 0, "acTime" : 0} for i in range(length)]}

                if item.pro.title not in statsinfo:
                    continue
                pos = statsinfo[item.pro.title]["pos"]

                if item.result == 'Waiting': #Waiting
                    break
                if item.result == 'Accepted' or item.result == 'Accept' or item.result == 'Yes' or item.result == 'YES': #Accepted
                    rank_dict["statsinfo"][pos]["acNum"] += 1
                rank_dict["statsinfo"][pos]["tryNum"] += 1

                if rank_dict[name]["probs"][pos]["acNum"] == 0:
                    if item.result == 'Accepted' or item.result == 'Accept' or item.result == 'Yes' or item.result == 'YES':
                        rank_dict[name]["probs"][pos]["acNum"] += 1
                        rank_dict[name]["probs"][pos]["acTime"] = dateToInt(item.time - contest.start_time, 1)
                        #rank_dict[name]["penalty"] += 20 * rank_dict[name]["probs"][pos]["failNum"] + dateToInt(item.time - contest.start_time, 0)
                        #rank_dict[name]["solved"] += 1
                        #print(contest.typec)
                        if contest.typec == 'icpc':
                            rank_dict[name]["penalty"] += 20 * rank_dict[name]["probs"][pos]["failNum"] + dateToInt(item.time - contest.start_time, 0)
                            rank_dict[name]["solved"] += 1
                        else:
                            rank_dict[name]["penalty"] += dateToInt(item.time - contest.start_time, 0)
                            cont_pro = Contest_problems.objects.get(contest=contest,problem=item.pro)
                            rank_dict[name]["solved"] += cont_pro.score
                    else:
                        rank_dict[name]["probs"][pos]["failNum"] += 1
            contest.rank = json.dumps(rank_dict)
            print("contest.rank")
            print(contest.rank)
            contest.save()
    except Exception as e:
        print("Error at contest rank:")
        print(e)
    return JsonResponse(json.loads("{}"))

def page_not_found(req):
    return ren2res("404.html", req, {})

def rank(req):
    pg = int(req.GET.get('pg', 1))
    qs = UserInfo.objects.all().order_by('-problem_ac','problem_try')
    #qs = UserInfo.objects.all().order_by('-problem_ac','problem_try')
    max = qs.count() // LIST_NUMBER_EVERY_PAGE + 1

    if (pg > max):
        raise Http404("no such page")
    start = pg - PAGE_NUMBER_EVERY_PAGE
    if start < 1:
        start = 1
    end = pg + PAGE_NUMBER_EVERY_PAGE
    if end > max:
        end = max

    lst = qs[(pg - 1) * LIST_NUMBER_EVERY_PAGE:pg * LIST_NUMBER_EVERY_PAGE]
    idx = (pg - 1) * LIST_NUMBER_EVERY_PAGE

    return ren2res("vj/rank.html", req, {'pg': pg, 'page': list(range(start, end + 1)), 'list': lst, 'idx': idx, 'rank':rank})


def about(req):
    return ren2res("vj/about.html", req, {})


