from django.test import TestCase
from django.contrib.auth.models import User
from OJ.models import *
import OJ.judger as judger
from django.core.files.base import ContentFile
class SubmitTest(TestCase):
    def setUp(self):
        print("setUp start")
        p1=Problem(uid=User())
        t1=TestCase(pid=p1,uid=User())
        t1.input='1 2'
        t1.output='3'
        p1.save()
        t1.save()
        print("setUp finish")
        

    def test_submit(self):
        print("test start")
    	sub = Submit(pid=Problem.objects.all()[0], uid=User(), lang=2)
        sub.save()
        content_file = ContentFile("#include <iostream>\nusing namespace std;\nint main()\n{\n    int a,b;\n    cin >> a >> b;\n    cout << a+b << endl;\n    return 0;\n}")
        sub.source_code.save(name=str(sub.id), content=content_file)
        sub.save()
        judger.Judger(sub);
        print("test finish")

