from django.template import RequestContext
from django.shortcuts import render_to_response,Http404,HttpResponseRedirect
from django.contrib import auth


from django.db.models import Q

from OJ.models import *

def update_code(code):
    return
def update_file(file):
    return

def ren2res(template,req=None,dict={}):
    if req.user.is_authenticated():
        dict.update({'user':{'id':req.user.id,'name':req.user.username}})
    if req:
        return render_to_response(template,dict,context_instance=RequestContext(req))
    else:
        return render_to_response(template,dict)

# Create your views here.

def home(req):
    return ren2res("home.html",req)

def login(req):
    if req.method=='GET':
        return render_to_response("login.html",context_instance=RequestContext(req))
    elif req.method=='POST':
        user=auth.authenticate(username=req.POST.get('name'),password=req.POST.get('pw'))
        if user is not None:
            auth.login(req,user)
            return HttpResponseRedirect("/")
        else:
            return render_to_response("login.html",{'err': True},context_instance=RequestContext(req))

def problem(req):
    pg=int(req.GET.get('pg', 1))
    search=req.GET.get('search', "")
    if search:
        qs=Problem.objects.filter(Q(id__icontains=search)|Q(title__icontains=search)|Q(uid__name__contains=search))
    else:
        qs=Problem.objects.all()

    max=qs.count()//20+1

    if(pg>max):
        raise Http404("no such page")
    start=pg-7
    if start<1:
        start=1
    end =pg+7
    if end>max:
        end=max

    lst=qs[(pg-1)*20:pg*20]

    return render_to_response("problem.html",{'pg': pg,'page':list(range(start,end+1)),'list': lst})

def problem_detail(req,pid):
    smp=Answer.objects.filter(pid__exact=pid).filter(example__exact=True)
    return render_to_response("problem/problem_detail.html",{'problem': Problem.objects.get(id=pid),'sample': smp})

def problem_submit(req,pid):
    if req.method=='GET':
        return render_to_response("problem/problem_submit.html",{'problem': Problem.objects.get(id=pid)},context_instance=RequestContext(req))
    elif req.method=='POST':
        if req.POST.get('code'):
            update_code(req.POST.get('code'))
        elif req.FILES:
            update_file(req.FILES['file'])
        return HttpResponseRedirect("/problem/"+pid+"/status")