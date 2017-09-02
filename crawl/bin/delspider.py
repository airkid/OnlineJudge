import requests,json

baseURL = 'http://127.0.0.1:6800/'
delProUrl = baseURL + 'delproject.json'
dictdata = {"project":"vjspider"}
r = requests.post(delProUrl,data=dictdata)