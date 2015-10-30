from django.template import RequestContext
from django.shortcuts import render_to_response, Http404, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from django.db.models import Q

from OJ.models import *

import OJ.judge as judge


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
        qs = Problem.objects.filter(Q(id__icontains=search) | Q(title__icontains=search)).select_related(
            "uid__name").filter(uid__contains=search)
    else:
        qs = Problem.objects.all()

    max = qs.count() // 20 + 1

    if (pg > max):
        raise Http404("no such page")
    start = pg - 7
    if start < 1:
        start = 1
    end = pg + 7
    if end > max:
        end = max

    lst = qs[(pg - 1) * 20:pg * 20]

    return ren2res("problem.html", req, {'pg': pg, 'page': list(range(start, end + 1)), 'list': lst})


def problem_detail(req, pid):
    smp = TestCase.objects.filter(pid__exact=pid).filter(sample__exact=True)
    return ren2res("problem/problem_detail.html", req, {'problem': Problem.objects.get(id=pid), 'sample': smp})


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
        judge.Judger(sub)
        return HttpResponseRedirect("/problem/" + pid + "/")
