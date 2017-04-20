from django.contrib import admin

from .models import *


class SubmitAdmin(admin.ModelAdmin):
    list_display = ('id','pid','uid','time','lang','status','cid','return_code','score',)
    list_filter = ('status','pid','uid',)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('id','title','visible','numberOfContest','isCCF',)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('id','pid','sample','score',)
    list_filter = ('pid','sample',)
class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('id','nickname','sid','school','problem_ac','problem_try',)
    list_filter = ('school',)

# Register your models here.

admin.site.register(UserInfo,UserInfoAdmin)
admin.site.register(Problem,ProblemAdmin)
admin.site.register(TestCase,TestCaseAdmin)
admin.site.register(Submit,SubmitAdmin)
admin.site.register(Contest)

