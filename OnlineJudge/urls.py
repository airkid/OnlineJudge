from django.conf.urls import include, url
from django.contrib import admin

from OJ import views


urlpatterns = [
    # Examples:
    # url(r'^$', 'OnlineJudge.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.home),
    url(r'^problem/$', views.problem),
    url(r'^problem/([0-9]+)/$',views.problem_detail),
    url(r'^problem/([0-9]+)/submit/$',views.problem_submit),
    url(r'^login/$',views.login),

    url(r'^admin/', include(admin.site.urls)),
]
