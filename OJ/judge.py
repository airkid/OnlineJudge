import subprocess
from tempfile import TemporaryFile

from OJ.models import Submit,Answer

ei = TemporaryFile(mode='w+')
ei.write('2 3\n')
ei.seek(0)

o = TemporaryFile('w+')

try:
    p = subprocess.Popen("./run.sh 1 100000 ./test",shell=True,stdin=ei,stdout=o,universal_newlines=True)
except:
    print("except happen")
p.wait()

print("end")

o.seek(0)
print(o.readline())

ei.close()
o.close()

class Judger:
    path="../submit"
    def __init__(self,id):
        self._id=int(id)
    def judge(self):
        pass
    def _complie(self):
        pass
