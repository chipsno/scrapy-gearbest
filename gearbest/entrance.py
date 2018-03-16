# -*- coding: utf-8 -*-

from scrapy import cmdline

if __name__ == '__main__':

    cmdline.execute("scrapy crawl gearbest_commodity_spider -L INFO".split())