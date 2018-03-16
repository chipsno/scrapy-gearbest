# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
from scrapy.exceptions import IgnoreRequest


class IgnoreRequestMiddleware(object):

    def __init__(self):
        self.ids_seen = set()

    def process_request(self, request, spider):
        if request.url in self.ids_seen:
            spider.logger.info('ignore the request from: %s' % request.url)
            raise IgnoreRequest("IgnoreRequest : %s" % request.url)
        else:
            spider.logger.debug('Spider agree the request: %s' % request.url)
            self.ids_seen.add(request.url)
