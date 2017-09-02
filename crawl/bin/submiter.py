# coding:utf-8
from base64 import b64decode
import requests,re,time
import urllib.request  
import urllib.parse  
import http.cookiejar 
import re
import urllib  
from scrapy.http import FormRequest

LANGUAGE = {
        'G++' : '0',
        'GCC' : '1',
        'C++' : '2',
        'C' : '3',
        'Pascal' : '4',
        'Java' : '5',
        'C#' : '6',
        'Python2' : '7',
        'Python3' : '8'
    }

class HduSubmiter:
    #G++ GCC C++ C Pascal Java C#
    loginURL = 'http://acm.hdu.edu.cn/userloginex.php?action=login'
    submitURL = 'http://acm.hdu.edu.cn/submit.php?action=submit'

    mapLang = {
        '0' : '0',
        '1' : '1',
        '2' : '2',
        '3' : '3',
        '4' : '4',
        '5' : '5',
        '6' : '6'
    }
    def __init__(self,Prob,User,Code,Lang):
        self.Prob = str(Prob)
        self.User = str(User)
        self.Code = str(Code)
        self.Lang = str(Lang)
        cj = http.cookiejar.CookieJar()  
        cookie_support = urllib.request.HTTPCookieProcessor(cj)  
        opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)  
        urllib.request.install_opener(opener)
        print("Prob:%s,User:%s,Lang:%s\nCode:%s\n"%(Prob,User,Lang,self.Code))

    def login(self):
        postDict={
            'username': self.User,
            'userpass': "2017shixun"+self.User,
            'login': 'Sign+In',
            }
        postData = urllib.parse.urlencode(postDict).encode()
        request = urllib.request.Request(self.loginURL, postData)
        response = urllib.request.urlopen(request)
        text = response.read()
        text = text.decode('gb2312')
        print("after login -> ",response.url)
        return not re.search(r'No such user or wrong password.', text)


    def submit(self):
        postDict={
            'problemid': self.Prob,
            'language': self.mapLang[self.Lang],
            'usercode': self.Code,
            'check': '0'
            }
        postData = urllib.parse.urlencode(postDict).encode()
        request = urllib.request.Request(self.submitURL, postData)
        response = urllib.request.urlopen(request)
        
        print("after submit ->",response.url)
        if 'status' not in response.url:
            return False
        return True
    def submit2OJ(self):
        if self.login():
            print("login success")
            try:
                if self.submit():
                    return True
                else:
                    return False
            except:
            	print("submit fail")
            	return False
            print("submit success")
            return True
        else:
            print("login fail")
            return False


class ZojSubmiter:
    # G++ GCC Java Python2
    loginURL = 'http://acm.zju.edu.cn/onlinejudge/login.do'
    mapLang = {
        '0' : '2',
        '1' : '1',
        '5' : '4',
        '7' : '5'
    }
    def __init__(self,Prob,User,Code,Lang):
        self.Prob = str(Prob)
        self.User = str(User)
        self.Code = str(Code)
        self.Lang = str(Lang)
        cj = http.cookiejar.CookieJar()  
        cookie_support = urllib.request.HTTPCookieProcessor(cj)  
        opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)  
        urllib.request.install_opener(opener)
        print("Prob:%s,User:%s,Lang:%s\nCode:%s\n"%(Prob,User,Lang,self.Code))

    def login(self):
        postDict={
            'handle': self.User,
            'password': "2017shixun"+self.User,
            }
        postData = urllib.parse.urlencode(postDict).encode()
        request = urllib.request.Request(self.loginURL, postData)
        response = urllib.request.urlopen(request)
        text = response.read()
        text = text.decode('utf-8')
        print("after login -> ",response.url)
        return not re.search(r'Handle or password is invalid.', text)
    
    def getSubmitURL(self):
        ProbelmURL = 'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode=%s' % self.Prob
        try:
            response = urllib.request.urlopen(ProbelmURL,timeout=2)
            data = response.read().decode('utf-8')
        except:
            pass
        linkre = re.compile('href=\"(.+?)\"')
        for x in linkre.findall(data):  
            if '/onlinejudge/submit.do' in x:
                return x
    
    def submit(self):
        postDict={
            'languageId': self.mapLang[self.Lang],
            'source': self.Code,
            }
        postData = urllib.parse.urlencode(postDict).encode()
        request = urllib.request.Request(self.submitURL, postData)
        response = urllib.request.urlopen(request)
        text = response.read()
        text = text.decode('utf-8')
        print("after submit ->",response.url)
        return re.search(r'Your source has been submitted.', text)

    def submit2OJ(self):
        self.submitURL = 'http://acm.zju.edu.cn'+self.getSubmitURL()
        if self.login():
            print("login success")
            try:
                if self.submit():
                    pass
                else:
                    print("submit fail")
                    return False
            except:
                print("submit fail")
                return False
            print("submit success")
            return True
        else:
            print("login fail")
            return False

class FzuSubmiter:
    #G++ GCC C++ C Pascal Java
    loginURL = 'http://acm.fzu.edu.cn/login.php?act=1&dir='
    submitURL = 'http://acm.fzu.edu.cn/submit.php?act=5'

    mapLang = {
        '0' : '0',
        '1' : '1',
        '2' : '4',
        '3' : '5',
        '4' : '2',
        '5' : '3'
    }
    def __init__(self,Prob,User,Code,Lang):
        self.Prob = str(Prob)
        self.User = str(User)
        self.Code = str(Code)
        self.Lang = str(Lang)
        cj = http.cookiejar.CookieJar()  
        cookie_support = urllib.request.HTTPCookieProcessor(cj)  
        opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)  
        urllib.request.install_opener(opener)
        print("Prob:%s,User:%s,Lang:%s\nCode:%s\n"%(Prob,User,Lang,self.Code))

    def login(self):
        postDict={
            'uname': self.User,
            'upassword': "2017shixun"+self.User,
            'submit': 'Submit',
            }
        postData = urllib.parse.urlencode(postDict).encode()
        request = urllib.request.Request(self.loginURL, postData)
        response = urllib.request.urlopen(request)
        text = response.read()
        text = text.decode('utf-8')
        print("after login -> ",response.url)
        return not re.search(r'Please Check Your UserID And Password', text)


    def submit(self):
        postDict={
            'pid': self.Prob,
            'lang': self.mapLang[self.Lang],
            'code': self.Code,
            'submit': 'Submit'
            }
        postData = urllib.parse.urlencode(postDict).encode()
        request = urllib.request.Request(self.submitURL, postData)
        response = urllib.request.urlopen(request)
        text = response.read()
        text = text.decode('utf-8')
        print("after submit ->",response.url)
        return re.search(r'Your Program have been saved.', text)
        
    def submit2OJ(self):
        if self.login():
            print("login success")
            try:
                if self.submit():
                    pass
                else:
                    print("submit fail")
                    return False
            except:
                print("submit fail")
                return False
            print("submit success")
            return True
        else:
            print("login fail")
            return False