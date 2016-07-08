from django.conf.urls import include, url
from django.contrib import admin

from OJ import views

handler404 = 'OJ.views.page_not_found'

urlpatterns = [
    # Examples:
    # url(r'^$', 'OnlineJudge.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.home),
    url(r'^login/$', views.login),
    url(r'^register/$', views.register),
    url(r'^logout/$', views.logout),
    url(r'^problem/$', views.problem),
    url(r'^problem/([0-9]+)/$', views.problem_detail),
    url(r'^problem/([0-9]+)/submit/$', views.problem_submit),
    url(r'^status/$', views.status),
    url(r'^contest/$', views.contest),
    url(r'^contest/([0-9]+)/$', views.contest_detail),
    url(r'^contest/([0-9]+)/get_problem$', views.contest_get_problem),
    url(r'^contest/([0-9]+)/status/$', views.contest_status),
    url(r'^contest/([0-9]+)/submit/$', views.contest_submit),
    url(r'^contest/([0-9]+)/time/$', views.contest_time),
    url(r'^contest/([0-9]+)/rank/$', views.contest_rank),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^rank/$', views.rank),
    url(r'^about/$', views.about),
]
