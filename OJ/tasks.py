# -*- coding: utf-8 -*-
from djcelery import celery
from OJ.models import *
import OJ.judpong as judger
@celery.task
def judge_delay(sub):
	if(judger.judgePong(sub)):
		print("judeged.")
	else:
		print("judge failed.")