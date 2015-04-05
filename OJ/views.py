from django.shortcuts import render_to_response,Http404
from django.db.models import Q

from OJ.models import *



# Create your views here.

def home(req):
    return render_to_response("home.html")

def problem(req):
    pg=int(req.GET.get('pg', 1))
    search=req.GET.get('search', "")
    if search:
        qs=Problem.objects.filter(Q(id__icontains=search)|Q(title__icontains=search)|Q(uid__name__contains=search))
    else:
        qs=Problem.objects.all()

    max=qs.count()//20+1

    if(pg>max): raise Http404("no such page")
    start=pg-7
    if start<1:start=1
    end =pg+7
    if end>max:end=max

    lst=qs[(pg-1)*20:pg*20]

    return render_to_response("problem.html",{'pg': pg,'page':list(range(start,end+1)),'list': lst})

def problem_detail(req,pid):
    smp=Answer.objects.filter(pid__exact=pid).filter(example__exact=True)
    return render_to_response("problem/problem_detail.html",{'problem': Problem.objects.get(id=pid),'sample': smp})

def problem_submit(req,pid):
    return render_to_response("problem/problem_submit.html",{'problem': Problem.objects.get(id=pid)})