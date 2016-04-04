from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserInfo(models.Model):
    id = models.OneToOneField(User, primary_key=True, related_name='info')
    school = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return str(self.id)


LANG_CHOICE = (
    (0, 'NONE'),
    (1, 'C'),
    (2, 'C++'),
    (3, 'Java'),
    # (4, 'Python'),
    # (5, 'Pascal'),
    # (6, 'FORTRAN'),
)


class Problem(models.Model):
    uid = models.ForeignKey(User)
    create_time = models.DateTimeField(auto_now_add=True)
    limit_time = models.PositiveIntegerField(default=1)
    limit_memory = models.PositiveIntegerField(default=1024 * 1024 * 128)
    answer_lang = models.PositiveSmallIntegerField(choices=LANG_CHOICE, default=0)
    title = models.CharField(max_length=254)
    content = models.TextField()
    input = models.TextField(default='')
    output = models.TextField(default='')
    # sample_input = models.TextField()
    # sample_output = models.TextField()
    # file_input = models.FileField()
    #file_output = models.FileField()
    note = models.TextField(blank=True)
    source = models.TextField(blank=True)
    # True表示该题目可见， False表示用于比赛，不可见
    visible = models.BooleanField(default=True)
    # CCF题目专用
    isCCF = models.BooleanField(default=False)

    def accepted(self):
        query = Submit.objects.filter(pid=self, status=0)
        return query.count()

    def submitted(self):
        query = Submit.objects.filter(pid=self)
        return query.count()

    def samples(self):
        query = TestCase.objects.filter(pid=self, sample=True)
        return query

    def __str__(self):
        return str(self.title)

    class Meta:
        ordering = ['create_time']


class TestCase(models.Model):
    pid = models.ForeignKey(Problem)
    uid = models.ForeignKey(User)
    time = models.DateTimeField(auto_now_add=True)
    sample = models.BooleanField(default=False)
    input = models.TextField()
    output = models.TextField()
    # CCF专用
    score = models.IntegerField(default=0)

    def __str__(self):
        return ('Sample ' if self.sample else '')+str(self.pid)

    class Meta:
        ordering = ['time']


class Contest(models.Model):
    uid = models.ForeignKey(User)
    name = models.CharField(max_length=254)
    start_time = models.DateTimeField()
    duration_time = models.DurationField()
    problems = models.ManyToManyField(Problem, related_name="contests")

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['start_time']

    def get_submits(self):
        return Submit.objects.filter(cid=self.id)

    def get_problem_list(self):
        problems = self.problems.all()
        lst = []
        cnt = 0
        for problem in problems:
            lst.append([cnt, chr(cnt + 65), problem])
            cnt += 1
        return lst


class Submit(models.Model):
    STATUS_CHOICE = (
        (0, 'Accepted'),
        (1, 'Waiting'),
        (2, 'Compiling'),
        (3, 'Running'),
        (-1, 'Compilation Error'),
        (-2, 'Syntax Error'),
        (-3, 'Runtime Error'),
        (-4, 'Output Limit Exceeded'),
        (-5, 'Time Limit Exceeded'),
        (-6, 'Memory Limit Exceeded'),
        (-7, 'Wrong Answer'),
        (-8, 'Presentation Error'),
    )

    pid = models.ForeignKey(Problem)
    uid = models.ForeignKey(User)
    time = models.DateTimeField(auto_now_add=True)
    lang = models.PositiveSmallIntegerField(choices=LANG_CHOICE)
    status = models.SmallIntegerField(choices=STATUS_CHOICE, default=1)
    run_time = models.PositiveSmallIntegerField(null=True, default=0)
    run_memory = models.PositiveIntegerField(null=True, default=0)
    source_code = models.FileField(default=None, upload_to='JudgeFiles/source/')
    # -1表示非比赛提交, 其余为比赛提交
    cid = models.IntegerField(default=-1)
    return_code = models.IntegerField(null=True)
    # CCF题目专用
    score = models.IntegerField(default=0)

    def __str__(self):
        return str(self.pid) + '  ' + str(self.uid) + '  ' + str(self.lang) + '  ' + str(self.cid)

    class Meta:
        ordering = ['time']

