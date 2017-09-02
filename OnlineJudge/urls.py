from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

from OJ import views
from vj import views as vjviews
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
    #url(r'^contest/([0-9]+)/clar/$', views.contest_clar),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^rank/$', views.rank),
    url(r'^about/$', views.about),
    url(r'^show_source/$', views.show_source),
    url(r'^change_name/$', views.change_name),
    url(r'^profile/$', views.profile),
    #VJ folow
    url(r'^vj/$', vjviews.home),
    url(r'^vj/login/$', vjviews.login),
    url(r'^vj/accounts/login/$',vjviews.login),
    url(r'^vj/register/$', vjviews.register),
    url(r'^vj/logout/$', vjviews.logout),
    url(r'^vj/problem/$', vjviews.problem),
    url(r'^vj/problem/([0-9]+)/$', vjviews.problem_detail),
    url(r'^vj/problem/([0-9]+)/submit/$', vjviews.problem_submit),
    url(r'^vj/problem/([0-9]+)/discuss/$', vjviews.problem_discuss),
    url(r'^vj/status/$', vjviews.status),
    url(r'^vj/show_source/$', vjviews.show_source),
    url(r'^vj/admin/', admin.site.urls),
    url(r'^vj/profile/$', vjviews.profile),
    url(r'^vj/contest/$', vjviews.contest),
    url(r'^vj/contest/addcontest/$', vjviews.contest_add),
    url(r'^vj/contest/addcontest/get_problem_title/$',vjviews.addcontest_get_problem_title),
    url(r'^vj/contest/addcontest/submit/$', vjviews.contest_add_process),
    url(r'^vj/contest/([0-9]+)/$', vjviews.contest_detail),
    url(r'^vj/contest/([0-9]+)/modify/$', vjviews.contest_modify),
    url(r'^vj/contest/([0-9]+)/modify/submit/$', vjviews.contest_modify_process),
    url(r'^vj/contest/([0-9]+)/get_problem$', vjviews.contest_get_problem),
    url(r'^vj/contest/([0-9]+)/status/$', vjviews.contest_status),
    url(r'^vj/contest/([0-9]+)/submit/$', vjviews.contest_submit),
    url(r'^vj/contest/([0-9]+)/time/$', vjviews.contest_time),
    url(r'^vj/contest/([0-9]+)/rank/$', vjviews.contest_rank),
    url(r'^vj/contest/([0-9]+)/clarification/$', vjviews.contest_clarification),
    url(r'^vj/rank/$', vjviews.rank),
    url(r'^vj/about/$', vjviews.about),
]
