# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, Http404, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.template import Context, RequestContext, loader
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Q
from django.core.files.base import ContentFile
from OJ.models import *
from vj.models import UserInfo as vjInfo
from OJ.tasks import judge_delay
from django.utils import timezone
from collections import OrderedDict
import datetime
import pytz
import re
import json
import OJ.judger as judger

LIST_NUMBER_EVERY_PAGE = 20
PAGE_NUMBER_EVERY_PAGE = 7


def ren2res(template, req, dict={}):
    if req.user.is_authenticated():
        p = re.compile('^[0-9a-zA-Z_]+$')
        dict.update({'user': {  'id': req.user.id, 
                                'name': req.user.get_username(),
                                'is_staff':req.user.is_staff,
                                'sid':req.user.info.sid,
                                'nickname':req.user.info.nickname,
                                'school':req.user.info.school}})
    else:
        dict.update({'user': False})
    if req:
        return render_to_response(template, dict, context_instance=RequestContext(req))
    else:
        return render_to_response(template, dict)


# Create your views here.

def home(req):
    return ren2res("home.html", req, {})


def login(req):
    if req.method == 'GET':
        if req.user.is_anonymous():
            if req.GET.get('next'):
                req.session['next'] = req.GET.get('next')
            return ren2res("login.html", req, {})
        else:
            return HttpResponseRedirect("/")
    elif req.method == 'POST':
        user = auth.authenticate(username=req.POST.get('name'), password=req.POST.get('pw'))
        if user is not None:
            auth.login(req, user)
            next = req.session.get('next')
            if next:
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect('/')
        else:
            return ren2res("login.html", req, {'err': "Wrong Username or Password!"})


def register(req):
    if req.method == 'GET':
        if req.user.is_anonymous():
            if req.GET.get('next'):
                req.session['next'] = req.GET.get('next')
            return ren2res('register.html', req, {})
        else:
            return HttpResponseRedirect('/')
    elif req.method == 'POST':
        name = req.POST.get('name')
        nickname = req.POST.get('nickname')
        result = User.objects.filter(username=name);
        p = re.compile('^[0-9a-zA-Z_]+$')
        if len(name) == 0 or p.match(name)==None:
            return ren2res('register.html', req, {'err': "Invalid account name"})
        elif len(nickname) == 0:
            return ren2res('register.html', req, {'err': "Nickname can't be null"})
        elif len(result) != 0:
            return ren2res('register.html', req, {'err': "This account has been registered! Try another"})
        else:
            pw1 = req.POST.get('pw1')
            if pw1 == "":
                return ren2res('register.html', req, {'err': "Password can't be null", 'name': name})
            pw2 = req.POST.get('pw2')
            if pw1 != pw2:
                return ren2res('register.html', req, {'err': "Password not consistent", 'name': name})
            else:
                newuser = User()
                newuser.username = name
                newuser.set_password(pw1)
                newuser.save()
                newinfo = UserInfo(id=newuser)
                newinfo.nickname = nickname 
                newinfo.sid = req.POST.get('sid')
                newinfo.save()
                vjinfo = vjInfo(id=newuser)
                vjinfo.sid = req.POST.get('sid')
                vjinfo.nickname = nickname 
                vjinfo.save()

                newuser = auth.authenticate(username=name, password=pw1)
                auth.login(req, user=newuser)
                next = req.session.get('next')
                if next:
                    return HttpResponseRedirect(next)
                else:
                    return HttpResponseRedirect('/')


def logout(req):
    auth.logout(req)
    return HttpResponseRedirect('/')


def problem(req):
    pg = int(req.GET.get('pg', 1))
    search = req.GET.get('search', "")
    if search:
        qs = Problem.objects.filter(visible=True).filter(numberOfContest=0).filter(Q(id__icontains=search) | Q(title__icontains=search) | Q(source__icontains=search))
        # .select_related("uid__name").filter(uid__contains=search)
    else:
        qs = Problem.objects.filter(visible=True).filter(numberOfContest=0).all()

    idxstart = (pg - 1) * LIST_NUMBER_EVERY_PAGE
    idxend = pg * LIST_NUMBER_EVERY_PAGE

    max = qs.count() // LIST_NUMBER_EVERY_PAGE + 1

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
    if req.user.is_authenticated():
        user = req.user
        for item in lst:
            if item.aceduser.filter(id=user.info.id):
                aclst.append(item.id)
            elif item.trieduser.filter(id=user.info.id):
                trylst.append(item.id)
#        print(aclst)
#        print('trylst')
#        print(trylst)

    return ren2res("problem.html", req, {'pg': pg, 'page': list(range(start, end + 1)), 'list': lst, 'aclst':aclst, 'trylst':trylst})


def problem_detail(req, pid):
    problem = Problem.objects.get(id=pid)
    if problem.visible and problem.numberOfContest == 0:
        smp = TestCase.objects.filter(pid__exact=pid).filter(sample__exact=True)
        return ren2res("problem/problem_detail.html", req, {'problem': problem, 'sample': smp})
    else:
        # 此处说明该题目处于比赛状态不可见
        return HttpResponseRedirect('/')


@login_required
def problem_submit(req, pid):
    if req.method == 'GET':
        return ren2res("problem/problem_submit.html", req, {'problem': Problem.objects.get(id=pid)})
    elif req.method == 'POST':
        sub = Submit(pid=Problem.objects.get(id=pid), uid=req.user, lang=req.POST.get('lang'))
        sub.save()
        if req.POST.get('code'):
            # f = open('JudgeFiles/source/' + str(sub.id), 'w')
            # f.write(req.POST.get('code'))
            content_file = ContentFile(req.POST.get('code'))
        elif req.FILES:
            # f = open('JudgeFiles/source/' + str(sub.id), 'wb')
            # f.write(req.FILES['file'].read())
            content_file = ContentFile(reILq.FES['file'].read())
        else:
            return ren2res("problem/problem_submit.html", req,
                           {'problem': Problem.objects.get(id=pid), 'err': "No Submit!"})
        # f.close()
        sub.source_code.save(name=str(sub.id), content=content_file)
        sub.save()
        #judger.Judger(sub);
        result=judge_delay.delay(sub)
        return HttpResponseRedirect("/status/")


def status(req):
    pid = req.GET.get('pid')
    problem = None
    if pid:
        problem = Problem.objects.get(id=pid)
        query = Submit.objects.filter(pid=problem, cid=-1).all().order_by('-id')
    else:
        query = Submit.objects.filter(cid=-1).order_by('-id')

    search = req.GET.get('search')
    if search:
        query = query.filter(Q(pid__title__icontains=search) | Q(uid__username__icontains=search))

    #print(len(query))

    pg = req.GET.get('pg')
    if not pg:
        pg = 1
    pg = int(pg)

    max_cnt = query.count() // LIST_NUMBER_EVERY_PAGE + 1
    start = max(pg - PAGE_NUMBER_EVERY_PAGE, 1)
    end = min(pg + PAGE_NUMBER_EVERY_PAGE, max_cnt)

    lst = query[(pg - 1) * LIST_NUMBER_EVERY_PAGE:pg * LIST_NUMBER_EVERY_PAGE]
    #print(len(lst))

    return ren2res('status.html', req, {'problem': problem, 'page': range(start, end + 1), 'list': lst})


def contest(req):
    search = req.GET.get('search')
    if search:
        query = Contest.objects.filter(Q(name__icontains=search) | Q(uid__username__icontains=search)).order_by('-start_time')
    else:
        query = Contest.objects.all().order_by('-start_time')
    pg = req.GET.get('pg')
    if not pg:
        pg = 1
    pg = int(pg)

    max_cnt = query.count() // LIST_NUMBER_EVERY_PAGE + 1
    start = max(pg - PAGE_NUMBER_EVERY_PAGE, 1)
    end = min(pg + PAGE_NUMBER_EVERY_PAGE, max_cnt)

    lst = query[(pg - 1) * LIST_NUMBER_EVERY_PAGE:pg * LIST_NUMBER_EVERY_PAGE]

    return ren2res('contest.html', req, {'page': range(start, end + 1), 'list': lst})


@login_required
def contest_detail(req, cid):
    contest = Contest.objects.get(id=cid)
    # time = datetime.datetime.now(pytz.timezone(pytz.country_timezones('cn')[0]))
    # time = datetime.datetime.now()
    time = timezone.now()
    if time > contest.start_time:
        start = True
    else:
        start = False
    if contest.private:
        # print('contest.accounts')
        # print(contest.accounts.all())
        if req.user.info not in contest.accounts.all():
            return ren2res("contest/contest.html", req, {'contest': contest, 'err': "You do not have access to this contest."})
    if start:
        problems = contest.get_problem_list()
        length = len(problems)
        problems_status = [0 for i in range(length)]

        for i in range(length):
            problems[i].append(len(Submit.objects.filter(uid = req.user).filter(pid = problems[i][2]).filter(status = 0)))
        return ren2res("contest/contest.html", req, {'contest': contest, 'problems': problems, 'problem': problems[0][2]})
    else:
        return ren2res("contest/contest.html", req, {'contest': contest, 'err': "Just wait."})


@login_required
def contest_get_problem(req, cid):
    if req.is_ajax():
        contest = Contest.objects.get(id=cid)
        pid = req.GET.get('pid')
        t = loader.get_template('contest/contest_problem.html')
        problem = Problem.objects.get(id=pid)
        if contest.private:
            if req.user.info not in contest.accounts.all():
                problem = []
        content_html = t.render(Context({'problem': problem, 'user' : req.user}))
        return HttpResponse(content_html)


@login_required
def contest_status(req, cid):
    if req.is_ajax():
        contest = Contest.objects.get(id=cid)
        t = loader.get_template('contest/contest_status.html')
        status_list = Submit.objects.filter(cid=cid).order_by('-time')
        if contest.private:
            if req.user.info not in contest.accounts.all():
                status_list = []
        pg = req.GET.get('pg')
        if not pg:
            pg = 1
        pg = int(pg)

        max_cnt = status_list.count() // LIST_NUMBER_EVERY_PAGE + 1
        start = max(pg - PAGE_NUMBER_EVERY_PAGE, 1)
        end = min(pg + PAGE_NUMBER_EVERY_PAGE, max_cnt)

        lst = status_list[(pg - 1) * LIST_NUMBER_EVERY_PAGE:pg * LIST_NUMBER_EVERY_PAGE]

        content_html = t.render(Context({'status_list': lst, 'page': range(start, end + 1), 'contest_id': cid, 'user': req.user}))
        return HttpResponse(content_html)
    else:
        raise Http404


@login_required
def contest_submit(req, cid):
    contest = Contest.objects.get(id=cid)
    time = datetime.datetime.now(pytz.timezone(pytz.country_timezones('cn')[0]))
    if time > contest.start_time + contest.duration_time:
        finish = True
    else:
        finish = False

    if contest.private:
        if req.user.info not in contest.accounts.all():
            return HttpResponseRedirect("/contest/" + cid + "/")

    if req.method == 'GET':
        return ren2res("contest/contest_submit.html", req, {'contest': contest, 'problems': contest.get_problem_list()})
    elif req.method == 'POST':
        pid = req.POST.get('pid')
        sub = Submit(pid=Problem.objects.get(id=pid), uid=req.user, lang=req.POST.get('lang'))
        if not finish:
            sub.cid = contest.id
        else:
            sub.cid = -1
        
        code=req.POST.get('code');
        if code:
            if len(code)>=10:
                content_file = ContentFile(req.POST.get('code'))
            else:
                return HttpResponseRedirect("/contest/" + cid + "/")
        elif req.FILES:
            content_file = ContentFile(req.FILES['file'].read())
        else:
            return ren2res("contest/contest_submit.html", req,
                           {'contest': contest, 'problems': contest.get_problem_list(), 'err': 'No Submit!'})
        sub.save()
        sub.source_code.save(name=str(sub.id), content=content_file)
        sub.save()
        #judger.Judger(sub)
        result=judge_delay.delay(sub)
    return HttpResponseRedirect("/contest/" + cid + "/")

def dateToInt(date, field):
     if field == 0:
         return date.days * 24 * 60 + date.seconds // 60
     else:
         return date.days * 24 * 60 *60  + date.seconds

@login_required
def contest_rank(req, cid):
    if req.is_ajax():
        try:
            contest = Contest.objects.get(id = cid)
            if contest.private:
                if req.user.info not in contest.accounts.all():
                    return JsonResponse("{}")
            rank_cache = contest.rank
            status_list = Submit.objects.filter(cid = cid).filter(id__gt = contest.last_submit_id).order_by("time")
            rank_dict = json.loads(rank_cache)
            statsinfo = {}
            pos = 0
            problem_list = contest.get_problem_list()
            length = len(problem_list)

            
            if contest.last_submit_id==0:
                rank_dict = {}
                rank_dict["statsinfo"] = [{} for i in range(length)]
                for item in problem_list:
                    rank_dict["statsinfo"][pos] = {"probid" : chr(pos + 65) ,"acNum" : 0, "tryNum" : 0, "fbTime" : -1}
                    statsinfo[item[2].title] = {"pos" : pos}
                    pos += 1
            else:
                for item in problem_list:
                    statsinfo[item[2].title] = {"pos" : pos}
                    pos += 1

            for item in status_list:
                if item.uid.is_staff :
                    continue
                name = item.uid.username
                contest.last_submit_id = max(contest.last_submit_id, item.id)
                if name not in rank_dict.keys():
                    rank_dict[name] = {"name" : name, "solved":0, "penalty":0, "probs" : [{"failNum" : 0, "acNum" : 0, "acTime" : 0} for i in range(length)]}
                pos = statsinfo[item.pid.title]["pos"]
                if item.status == 3: #Waiting
                    break

                if item.status == 0: #Accepted
                    rank_dict["statsinfo"][pos]["acNum"] += 1
                rank_dict["statsinfo"][pos]["tryNum"] += 1

                if rank_dict[name]["probs"][pos]["acNum"] == 0:
                    if item.status == 0:
                        rank_dict[name]["probs"][pos]["acNum"] += 1
                        acTime = dateToInt(item.time - contest.start_time, 1)
                        rank_dict[name]["probs"][pos]["acTime"] = dateToInt(item.time - contest.start_time, 1)
                        if rank_dict["statsinfo"][pos]["fbTime"] == -1 or rank_dict["statsinfo"][pos]["fbTime"] >= acTime:
                            rank_dict["statsinfo"][pos]["fbTime"] = acTime
                            rank_dict[name]["probs"][pos]["fb"] = 1
                        else:
                            rank_dict[name]["probs"][pos]["fb"] = 0
                        rank_dict[name]["penalty"] += 20 * rank_dict[name]["probs"][pos]["failNum"] + dateToInt(item.time - contest.start_time, 0)
                        rank_dict[name]["solved"] += 1
                    else:
                        rank_dict[name]["probs"][pos]["failNum"] += 1
                        rank_dict[name]["probs"][pos]["fb"] = 0
            #print(rank_dict)
            contest.rank = json.dumps(rank_dict)
            contest.save()
            return JsonResponse(rank_dict)
        except Exception as e:
            print(e)
            raise e

def page_not_found(req):
    return ren2res("404.html", req, {})


@login_required
def contest_time(req, cid):
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

def rank(req):
    pg = int(req.GET.get('pg', 1))
    search = req.GET.get('search', "")
    if search:
        qs = UserInfo.objects.filter(Q(nickname__icontains=search)|Q(id__username__icontains=search)|Q(id__id__icontains=search))
        # .select_related("uid__name").filter(uid__contains=search)
    else:
        qs = UserInfo.objects.all().order_by('-problem_ac','problem_try')

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

    return ren2res("rank.html", req, {'pg': pg, 'page': list(range(start, end + 1)), 'list': lst, 'idx': idx})


def about(req):
    return ren2res("about.html", req, {})


LANG_DICT = {0: 'none', 1: 'c', 2: 'cpp', 3: 'java'}


@login_required
def show_source(req):
    solution_id = req.GET.get('solution_id')
    query = Submit.objects.filter(id=solution_id)
    if len(query) == 0:
        raise Http404
    elif query[0].uid.id != req.user.id and not req.user.is_staff:
        raise Http404
    else:
        submit = query[0]
        file = submit.source_code.read(-1).decode('utf-8')
        err = ""
        try:
            f = open('/home/sduacm/OnlineJudge/JudgeFiles/result/' + str(submit.id), 'r')
            err = f.read()
            f.close()
        except IOError as e:
            print(e)
            pass
        
        err = err.replace("/tmp","...")
        err = err.replace("/sduoj/source","")

        if err == '':
            err = 'Successful'
        htmldict={'submit': submit, 'code': file, 'errinfo': err, 'lang': LANG_DICT[submit.lang]}
        if submit.pid.isSPJ:
            chkerr = ""
            try:
                f = open('/home/sduacm/OnlineJudge/JudgeFiles/checkresult/' + str(submit.id), 'r')
                chkerr = f.read()
                f.close()
            except IOError as e:
                print(e)
            chkerr = chkerr.replace("/tmp","...")
            chkerr = chkerr.replace("/sduoj/source","")
            htmldict['spjinfo'] = chkerr
        return ren2res('show_source.html', req, htmldict)

@login_required
def change_sid(req):
    user = req.user
    sid = req.POST.get('sid')
    if sid is None:
        return ren2res('temp_changesid.html',req,{})
    else:
        user.info.sid = sid
        user.info.save()
        return HttpResponseRedirect('/')


@login_required
def change_name(req):
    user = req.user
    name = req.POST.get('name')
    if name is None:
        return ren2res('temp_changename.html',req,{})
    else:
        result = User.objects.filter(username=name);
        p = re.compile('^[0-9a-zA-Z_]+$')
        if len(name) == 0 or p.match(name)==None:
            return HttpResponseRedirect('/')
        elif len(result) != 0:
            return HttpResponseRedirect('/')
        if p.match(user.get_username())!=None:
            return HttpResponseRedirect('/')
            
        user.username = name
        user.save()
        return HttpResponseRedirect('/')



@login_required
def profile(req):
    if req.method == 'GET':
        return ren2res('profile.html',req,{})
    else:
        user = req.user
        if not user:
            return ren2res('profile.html',req,{})
        else:
            pw = req.POST.get('pw')
            if not user.check_password(pw):
                return ren2res('profile.html', req, {'err': "Wrong password"})
            user.info.nickname = req.POST.get('nickname')
            if len(user.info.nickname)==0:
                return ren2res('profile.html', req, {'err': "Nickname can't be null"})
            user.info.school = req.POST.get('school')
            user.info.sid = req.POST.get('sid')
            user.info.save()
            npw1 = req.POST.get('npw1')
            if npw1 == "":
                return ren2res('profile.html', req, {'err': "User Profile Updated"})
            npw2 = req.POST.get('npw2')
            if npw1 != npw2:
                return ren2res('profile.html', req, {'err': "New Password not consistent"})
            else:
                user.set_password(npw1)
                user.save()
                return ren2res("login.html", req, {})
        return HttpResponseRedirect('/')
