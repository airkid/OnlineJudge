from django.db import models
from django.contrib.auth.models import User as AuthUser

# Create your models here.

class User(models.Model):
    id=models.OneToOneField(AuthUser,primary_key=True)
    school=models.CharField(max_length=50,blank=True)

    def __str__(self):
        return str(self.name)

class Problem(models.Model):
    uid=models.ForeignKey(AuthUser)
    time=models.DateTimeField(auto_now_add=True)
    limit_time=models.PositiveIntegerField(default=1000)
    limit_memory=models.PositiveIntegerField(default=1024*1024*128)
    title=models.CharField(max_length=254)
    content=models.TextField()
    input=models.TextField()
    output=models.TextField()
    note=models.TextField(blank=True)
    source=models.TextField(blank=True)
    submitted=models.PositiveIntegerField(default=0)
    acceptted=models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.title)

    class Meta:
        ordering=['time']

class Answer(models.Model):
    pid=models.ForeignKey(Problem)
    uid=models.ForeignKey(AuthUser)
    time=models.DateTimeField(auto_now_add=True)
    example=models.BooleanField(default=False)
    input=models.TextField()
    output=models.TextField()

    def __str__(self):
        return str(self.pid)

    class Meta:
        ordering=['time']

class Submit(models.Model):

    TYPE_CHOICE=(
        (0, 'UNKNOWN'),
        (1, 'C'),
        (2, 'C++'),
        (3, 'Java'),
        (4, 'Python'),
        (5, 'Pascal'),
        (6, 'FORTRAN'),
    )

    STATUS_CHOICE=(
        (0, 'Accepted'),
        (1, 'Waiting'),
        (2, 'Compiling'),
        (3, 'Running'),
        (-1, 'Compilation Error'),
        (-2, 'Wrong Answer'),
        (-3, 'Presentation Error'),
        (-4, 'Output Limit Exceeded'),
        (-5, 'Time Limit Exceeded'),
        (-6, 'Memory Limit Exceeded'),
        (-7, 'Runtime Error'),
    )

    pid=models.ForeignKey(Problem)
    uid=models.ForeignKey(AuthUser)
    time=models.DateTimeField(auto_now_add=True)
    type=models.PositiveSmallIntegerField(choices=TYPE_CHOICE)
#    code=models.FileField(upload_to='submit')
    status=models.SmallIntegerField(choices=STATUS_CHOICE,default=1)
    run_time=models.PositiveSmallIntegerField(null=True)
    run_memory=models.PositiveIntegerField(null=True)

    def __str__(self):
        return str(self.pid)+'  '+str(self.uid)+'  '+str(self.type)

    class Meta:
        ordering=['time']
