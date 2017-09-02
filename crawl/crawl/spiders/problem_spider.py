import scrapy,re
from scrapy.spiders import Spider
from scrapy.selector import Selector
from datetime import datetime
from crawl.items import ProblemItem
from lxml import etree


class HduProblemSpider(Spider):
    name = 'hdu_problem'
    #allowed_domains = ['acm.hdu.edu.cn']
    problem_id = '1000'

    def __init__(self, problem_id='1005', *args, **kwargs):
        self.problem_id = problem_id
        super(HduProblemSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'http://acm.hdu.edu.cn/showproblem.php?pid=%s' % problem_id
        ]

    def parse(self, response):
        #print("11111111111111111",type(response.body))
        
        html = (response.body).decode('gbk','ignore')
        sel = Selector(text=html)

        item = ProblemItem()
        item['originOj'] = 'HDU'
        item['problemId'] = self.problem_id
        item['problemUrl'] = response.url
        item['title'] = sel.xpath('//h1/text()').extract()[0]
        item['desc'] = sel.css('.panel_content').extract()[0]
        item['input'] = sel.css('.panel_content').extract()[1]
        item['output'] = sel.css('.panel_content').extract()[2]
        item['timeLimit'] = \
            sel.xpath('//b/span/text()').re('T[\S*\s]*S')[0][12:]
        item['memoryLimit'] = \
            sel.xpath('//b/span/text()').re('Me[\S*\s]*K')[0][14:]
        item['sampleInput'] = sel.xpath('//pre/div/text()').extract()[0]
        item['sampleOutput'] = sel.xpath('//pre/div/text()').extract()[1]
        item['updateTime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Ls = sel.xpath('//pre/div/div').extract()
        item['note'] = ''
        if len(Ls) > 0:
            item['note'] = Ls[0]
        
        return item


class PojProblemSpider(Spider):
    name = 'poj_problem'
    #allowed_domains = ['acm.hdu.edu.cn']
    problem_id = '1000'

    def __init__(self, problem_id='1000', *args, **kwargs):
        self.problem_id = problem_id
        super(PojProblemSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'http://poj.org/problem?id=%s' % problem_id
        ]

    def parse(self, response):
        html = (response.body).decode('gbk','ignore')        
        sel = Selector(text=html)


        item = ProblemItem()
        item['originOj'] = 'POJ'
        item['problemId'] = self.problem_id
        item['problemUrl'] = response.url
        item['title'] = sel.css('.ptt').xpath('./text()').extract()[0]
        item['desc'] = sel.css('.ptx').extract()[0]
        item['input'] = sel.css('.ptx').extract()[1]
        item['output'] = sel.css('.ptx').extract()[2]
        try:
            item['timeLimit'] = sel.css('.plm').\
                re('Case\sT[\S*\s]*MS')[0][21:]
        except:
            item['timeLimit'] = sel.css('.plm').re('T[\S*\s]*MS')[0][16:]
        item['memoryLimit'] = sel.css('.plm').re('Me[\S*\s]*K')[0]
        item['sampleInput'] = sel.css('.sio').extract()[0]
        item['sampleOutput'] = sel.css('.sio').extract()[1]
        item['updateTime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        item['note'] = ''
        
        return item

class ZojProblemSpider(Spider):
    name = 'zoj_problem'
    problem_id = '1001'

    def __init__(self, problem_id='1001', *args, **kwargs):
        self.problem_id = problem_id
        super(ZojProblemSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode=%s' % problem_id
        ]

    def getDetail(self,html):
        L = len(html)
        left = right = cnt = 0
        for i in range(0,L-4):
            if html[i:i+4] == '<hr>':
                cnt = cnt + 1
                print("find a <hr>")
                if cnt == 2 :
                    left = i+4
                elif cnt == 3:
                    right = i+1
                    break
        return html[left:right]

    def moreProcess(self,text):
        for i in range(0,len(text)):
            if text[i] == '>':
                return text[i+2:]

    def parse(self,response):
        html = (response.body).decode('gbk','ignore')
        sel = Selector(text=html)

        item = ProblemItem()
        item['originOj'] = 'ZOJ'
        item['problemId'] = self.problem_id
        item['problemUrl'] = response.url
        
        item['title'] = sel.css('.bigProblemTitle').xpath('./text()').extract()[0]
        item['desc'] = self.getDetail(html)
        item['input'] = item['output'] = item['sampleInput'] = item['sampleOutput'] = item['note'] = ''
        item['timeLimit'] = self.moreProcess(str(sel.xpath('//center[2]').re('T[\S*\s]*s')[0]))
        item['memoryLimit'] = self.moreProcess(str(sel.xpath('//center[2]').re('M[\S*\s]*B')[0]))
        item['updateTime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yield item



class FzuProblemSpider(Spider):
    name = 'fzu_problem'
    #allowed_domains = ['acm.hdu.edu.cn']
    problem_id = '1000'

    def __init__(self, problem_id='1000', *args, **kwargs):
        self.problem_id = problem_id
        super(FzuProblemSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'http://acm.fzu.edu.cn/problem.php?pid=%s' % problem_id
        ]

    def parse(self, response):
        html = (response.body).decode('utf-8','ignore')
        sel = Selector(text=html)

        item = ProblemItem()
        item['originOj'] = 'FZU'
        item['problemId'] = self.problem_id
        item['problemUrl'] = response.url
        item['title'] = sel.xpath(
            '//div[contains(@class,\
            "problem_title")]/b/text()').extract()[0][14:].rstrip()
        item['desc'] = \
            sel.css('.pro_desc').extract()[0].\
            replace('<div class="data">', '<pre>').\
            replace('</div>', '</pre>')
        try:
            item['input'] = sel.css('.pro_desc').extract()[1]
        except:
            item['input'] = ''
        try:
            item['output'] = sel.css('.pro_desc').extract()[2]
        except:
            item['output'] = ''
        item['timeLimit'] = \
            sel.css('.problem_desc').re('T[\S*\s]*c')[0][12:]
        item['memoryLimit'] = \
            sel.css('.problem_desc').\
            re('M[\S*\s]*B')[0][15:]
        item['sampleInput'] = \
            sel.xpath('//div[@class="data"]/text()').extract()[-2]
        item['sampleOutput'] = \
            sel.xpath('//div[@class="data"]/text()').extract()[-1]
        item['updateTime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        item['note'] = ''
        
        return item
