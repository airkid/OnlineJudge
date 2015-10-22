from django.contrib import admin

from .models import *


# Register your models here.

admin.site.register(UserInfo)
admin.site.register(Problem)
admin.site.register(TestCase)
admin.site.register(Submit)
admin.site.register(Contest)
