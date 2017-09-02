from django.test import TestCase
from django.contrib.auth.models import User
from OJ.models import *
import OJ.judger as judger
from django.core.files.base import ContentFile
class SubmitTest(TestCase):
    def setUp(self):
        p1=Problem()
        p1.input='1 2'
        p1.output='3'
        p1.save()
        

    def test_submit(self):
    	sub = Submit(pid=Problem.objects.all()[0], uid=User(), lang=2)
        sub.save()
        content_file = ContentFile("#include <iostream>\nusing namespace std;\nint main()\n{\n    int a,b;\n    cin >> a >> b;\n    cout << a+b << endl;\n    return 0;\n}")
        sub.source_code.save(name=str(sub.id), content=content_file)
        sub.save()
        judger.Judger(sub);

