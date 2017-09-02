import scrapy,time
from scrapy.spiders import Spider
from scrapy.selector import Selector
from datetime import datetime
from crawl.items import StatusItem

class HduStatusSpider(Spider):
    name = "hdu_status"
    user = "sduvj1"
    endStatus = ['Accept','Wrong','Error','Exceed']

    def __init__(self,vj_run_id="100000", user="sduvj1", submit="True", *args, **kwargs):
        self.user = user
        self.vj_run_id = vj_run_id
        super(HduStatusSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'http://acm.hdu.edu.cn/status.php?user=%s'%user
        ]
        self.submit = submit

    def parse(self, response):
        sel = Selector(response)

        item = StatusItem()
        item['vjRunID'] = self.vj_run_id
        item['result'] = "Crawling Failed"
        item['memoryc'] = ""
        item["timec"] = ""
        print("!!!!!!!!!!1",self.submit)
        if self.submit == "True":
            tr = sel.xpath('//table[@class="table_text"]/tr')[1]
            if tr :
                #print("find item!!!!!!!!!!!!!")
                item['result'] = tr.xpath('.//td').xpath('.//font/text()').extract()[0]
                try:
                    item['memoryc'] = tr.xpath('.//td')[5].xpath('./text()').extract()[0]
                    item['timec'] = tr.xpath('.//td')[4].xpath('./text()').extract()[0]
                except:
                    pass
                #print("%s,%s,%s\n"%(item['result'],item['memoryc'],item['timec']))
                yield item

                flag = False
                for st in self.endStatus:
                    if st in item['result']:
                        flag = True
                        break
                if not flag:
                    time.sleep(1)
                    yield scrapy.Request(response.url,callback=self.parse)
        else:
            item['result'] = "Submit Failed"
            yield item

class ZojStatusSpider(Spider):
    name = 'zoj_status'
    user = ''
    endStatus = ['Accept','Wrong','Error','Exceed','Fault','Exit']

    def __init__(self,vj_run_id="100000", user="sduvj1", submit="True", *args, **kwargs):
        self.user = user
        self.vj_run_id = vj_run_id
        super(ZojStatusSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'http://acm.zju.edu.cn/onlinejudge/showRuns.do?contestId=1&search=true&handle=%s'%user
        ]
        self.submit = submit

    def getValidStatus(self,result):
        res = ''
        for i in range(0,len(result)):
            if ((result[i] >= 'A') and (result[i]<='Z')) \
                or ((result[i] >= 'a') and (result[i]<='z')):
                res  = res + result[i]
        return res

    def parse(self, response):
        sel = Selector(response)

        item = StatusItem()
        item['vjRunID'] = self.vj_run_id
        item['result'] = "Crawling Failed"
        item['memoryc'] = ""
        item["timec"] = ""
        print("!!!!!!!!!!",self.submit)
        if self.submit == "True":
            tr = sel.xpath('//table[@class="list"]/tr')[1]
            if tr :
                #print("find item!!!!!!!!!!!!!")
                try:
                    item['result'] = tr.xpath('.//td[@class="runJudgeStatus"]/span/text()').\
                        extract()[0]
                    item['memoryc'] = \
                        tr.xpath('.//td')[6].xpath('./text()').extract()[0]
                    item['timec'] = \
                        tr.xpath('.//td')[5].xpath('./text()').extract()[0]
                except:
                    pass
                item['result'] = self.getValidStatus(item['result'])
                #print("%s,%s,%s\n"%(item['result'],item['memoryc'],item['timec']))
                yield item

                flag = False
                for st in self.endStatus:
                    if st in item['result']:
                        flag = True
                        break
                if not flag:
                    time.sleep(1)
                    yield scrapy.Request(response.url,callback=self.parse)
        else:
            item['result'] = "Submit Failed"
            yield item


class FzuStatusSpider(Spider):
    name = "fzu_status"
    user = "sduvj1"
    endStatus = ['Accept','Wrong','Error','Exceed','Call']

    def __init__(self,vj_run_id="100000", user="sduvj1", submit="True", *args, **kwargs):
        self.user = user
        self.vj_run_id = vj_run_id
        super(FzuStatusSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'http://acm.fzu.edu.cn/log.php?user=%s'%user
        ]
        self.submit = submit

    def parse(self, response):
        sel = Selector(response)

        item = StatusItem()
        item['vjRunID'] = self.vj_run_id
        item['result'] = "Crawling Failed"
        item['memoryc'] = ""
        item["timec"] = ""
        print("!!!!!!!!!!1",self.submit)
        if self.submit == "True":
            tr = sel.xpath('//table/tr')[1]
            if tr :
                #print("find item!!!!!!!!!!!!!")
                try:
                    item['result'] = tr.xpath('.//td/font/text()').\
                        extract()[0]
                except:
                    item['result'] = tr.xpath('.//td/font/a/text()').\
                        extract()[0]
                try:
                    item['memoryc'] = \
                        tr.xpath('.//td')[6].xpath('./text()').extract()[0]
                    item['timec'] = \
                        tr.xpath('.//td')[5].xpath('./text()').extract()[0]
                except:
                    pass
                #print("%s,%s,%s\n"%(item['result'],item['memoryc'],item['timec']))
                yield item

                flag = False
                for st in self.endStatus:
                    if st in item['result']:
                        flag = True
                        break
                if not flag:
                    time.sleep(1)
                    yield scrapy.Request(response.url,callback=self.parse)
        else:
            item['result'] = "Submit Failed"
            yield item
        



  