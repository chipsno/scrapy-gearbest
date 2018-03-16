# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GearbestItem(scrapy.Item):
    # define the fields for your item here like:
    sku = scrapy.Field()
    page_url = scrapy.Field()
    category = scrapy.Field()
    title = scrapy.Field()
    subtitle = scrapy.Field()
    brand = scrapy.Field()
    currency = scrapy.Field()
    price = scrapy.Field()
    stock_status = scrapy.Field()
    props = scrapy.Field()
    main_image_urls = scrapy.Field()
    main_video_urls = scrapy.Field()
    descriptions = scrapy.Field()
    specifications = scrapy.Field()
    additional_image_urls = scrapy.Field()
