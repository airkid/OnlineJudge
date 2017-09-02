# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ProblemItem(scrapy.Item):
    originOj = scrapy.Field()
    problemId = scrapy.Field()
    problemUrl = scrapy.Field()
    title = scrapy.Field()
    timeLimit = scrapy.Field()
    memoryLimit= scrapy.Field()
    desc = scrapy.Field()
    input = scrapy.Field()
    output = scrapy.Field()
    sampleInput = scrapy.Field()
    sampleOutput = scrapy.Field()
    updateTime = scrapy.Field()
    note = scrapy.Field()

class StatusItem(scrapy.Item):
    vjRunID = scrapy.Field()
    result = scrapy.Field()
    timec = scrapy.Field()
    memoryc = scrapy.Field()