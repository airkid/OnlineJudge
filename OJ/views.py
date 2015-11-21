from django.shortcuts import render_to_response, Http404, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.template import Context, RequestContext, loader
from django.http import HttpResponse
from django.db.models import Q
import datetime
from OJ.models import *
import pytz
import OJ.judge as judge

LIST_NUMBER_EVERY_PAGE = 20
PAGE_NUMBER_EVERY_PAGE = 7


def ren2res(template, req, dict={}):
    if req.user.is_authenticated():
        dict.update({'user': {'id': req.user.id, 'name': req.user.get_username()}})
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
        result = User.objects.filter(username=name);
        if len(result) != 0:
            return ren2res('register.html', req, {'err': "This email has been registered ! Try another"})
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
        qs = Problem.objects.filter(visible=True).filter(Q(id__icontains=search) | Q(title__icontains=search))
        # .select_related("uid__name").filter(uid__contains=search)
    else:
        qs = Problem.objects.filter(visible=True).all()

    max = qs.count() // 20 + 1

    if (pg > max):
        raise Http404("no such page")
    start = pg - PAGE_NUMBER_EVERY_PAGE
    if start < 1:
        start = 1
    end = pg + PAGE_NUMBER_EVERY_PAGE
    if end > max:
        end = max

    lst = qs[(pg - 1) * LIST_NUMBER_EVERY_PAGE:pg * LIST_NUMBER_EVERY_PAGE]

    return ren2res("problem.html", req, {'pg': pg, 'page': list(range(start, end + 1)), 'list': lst})


def problem_detail(req, pid):
    problem = Problem.objects.get(id=pid)
    if problem.visible:
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
            f = open('JudgeFiles/source/' + str(sub.id), 'w')
            f.write(req.POST.get('code'))
        elif req.FILES:
            f = open('JudgeFiles/source/' + str(sub.id), 'wb')
            f.write(req.FILES['file'].read())
        else:
            return ren2res("problem/problem_submit.html", req,
                           {'problem': Problem.objects.get(id=pid), 'err': "No Submit!"})
        f.close()
        judge.Judger(sub, False)
        return HttpResponseRedirect("/status/?pid=" + pid + "/")


def status(req):
    pid = req.GET.get('pid')
    problem = None
    if pid:
        problem = Problem.objects.ger(id=pid)
        query = Submit.objects.filter(pid=problem, cid=-1).all().order_by('-time')
    else:
        query = Submit.objects.filter(cid=-1).order_by('-time')

    search = req.GET.get('search')
    if search:
        query = query.filter(Q(pid__title__icontains=search) | Q(uid__username__icontains=search))

    pg = req.GET.get('pg')
    if not pg:
        pg = 1

    max_cnt = query.count()
    start = max(pg - PAGE_NUMBER_EVERY_PAGE, 1)
    end = min(pg + PAGE_NUMBER_EVERY_PAGE, max_cnt)

    lst = query[(pg - 1) * LIST_NUMBER_EVERY_PAGE:pg * LIST_NUMBER_EVERY_PAGE]

    return ren2res('status.html', req, {'problem': problem, 'page': range(start, end + 1), 'list': lst})


def contest(req):
    search = req.GET.get('search')
    if search:
        query = Contest.objects.filter(Q(name__icontains=search) | Q(uid__username__icontains=search))
    else:
        query = Contest.objects.all()
    pg = req.GET.get('pg')
    if not pg:
        pg = 1

    max_cnt = query.count()
    start = max(pg - PAGE_NUMBER_EVERY_PAGE, 1)
    end = min(pg + PAGE_NUMBER_EVERY_PAGE, max_cnt)

    lst = query[(pg - 1) * LIST_NUMBER_EVERY_PAGE:pg * LIST_NUMBER_EVERY_PAGE]

    return ren2res('contest.html', req, {'page': range(start, end + 1), 'list': lst})


def contest_detail(req, cid):
    contest = Contest.objects.get(id=cid)
    time = datetime.datetime.now(pytz.timezone(pytz.country_timezones('cn')[0]))
    if time > contest.start_time:
        start = True
    else:
        start = False
    if start:
        problems = contest.get_problem_list()
        return ren2res("contest/contest.html", req, {'contest': contest, 'problems': problems})
    else:
        return ren2res("contest/contest.html", req, {'contest': contest, 'err': "Contest not start yet!"})


def contest_get_problem(req, cid):
    if req.is_ajax():
        pid = req.GET.get('pid')
        t = loader.get_template('./contest/contest_problem.html')
        problem = Problem.objects.get(id=pid)
        content_html = t.render(Context({'problem': problem}))
        return HttpResponse(content_html)


def contest_status(req, cid):
    if req.is_ajax():
        t = loader.get_template('./contest/contest_status.html')
        status_list = Submit.objects.filter(cid=cid)
        content_html = t.render(Context({'status_list': status_list}))
        return HttpResponse(content_html)


def contest_submit(req, cid):
    contest = Contest.objects.get(id=cid)
    time = datetime.datetime.now(pytz.timezone(pytz.country_timezones('cn')[0]))
    if time > contest.start_time + contest.duration_time:
        finish = True
    else:
        finish = False
    if req.method == 'GET':
        return ren2res("contest/contest_submit.html", req, {'contest': contest, 'problems': contest.get_problem_list()})

    elif req.method == 'POST':
        pid = req.POST.get('pid')
        sub = Submit(pid=Problem.objects.get(id=pid), uid=req.user, lang=req.POST.get('lang'))
        if not finish:
            sub.cid = contest.id
        else:
            sub.cid = -1
        sub.save()
        if req.POST.get('code'):
            f = open('JudgeFiles/source/' + str(sub.id), 'w')
            f.write(req.POST.get('code'))
        elif req.FILES:
            f = open('JudgeFiles/source/' + str(sub.id), 'wb')
            f.write(req.FILES['file'].read())
        else:
            return ren2res("contest/contest_submit.html", req,
                           {'contest': contest, 'problems': contest.get_problem_list(), 'err': 'No Submit!'})
        f.close()
        judge.Judger(sub)
    # return ren2res()
    if not finish:
        return HttpResponseRedirect("/contest/" + cid + "/")
    else:
        return HttpResponseRedirect("/contest/"+cid+"/status?pid=" + pid)