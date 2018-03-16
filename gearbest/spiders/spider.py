# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy import Request

import os
import json
import re
from urllib import parse as urlparse

from gearbest.items.items import *
from scrapy.utils.project import get_project_settings

class GearbestSpider(scrapy.spiders.Spider):
    # https://www.gearbest.com spider
    name = "gearbest_commodity_spider"

    allowed_domains = ["gearbest.com"]

    handle_httpstatus_list = [302, 301]

    def __init__(self, *args, **kwargs):
        pass

    def start_requests(self):
        self.logger.info('spider start')

        gearbest_home_url = 'https://www.gearbest.com'
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Host": "www.gearbest.com",
            "Upgrade-Insecure-Requests": "1"
        }

        yield Request(url=gearbest_home_url,
                      headers=headers,
                      callback=self.parse_homepage)

    def parse_homepage(self, response):
        is_testing = get_project_settings().getbool('ONLY_TEST', default=True)

        if response.status == 200:

            page_size = '120'
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Host": "www.gearbest.com",
                "Upgrade-Insecure-Requests": "1"
            }

            sel = Selector(response)

            categories_li_list = sel.xpath(
                '//ul[@class="categories-list-box"]/li')
            for categories_li in categories_li_list:
                url_params = {
                    'category_url': response.urljoin(categories_li.xpath('a/@href').extract_first().strip()),
                    'page_size': page_size,
                    'index': 1,
                }
                url = '%(category_url)s/?page_size=%(page_size)s' % url_params
                the_meta = {
                    'url_params': url_params,
                }

                yield Request(url,
                              headers=headers,
                              meta=the_meta,
                              callback=self.parse_category)

                if is_testing:
                    # testing: only crawl one category
                    break


    def parse_category(self, response):

        if response.status == 200:
            sel = Selector(response)
            the_meta = response.meta

            cate_page_list = sel.xpath(
                '//*[@id="catePageList"]/li[@class="c_cate"]')
            for c_cate in cate_page_list:
                a_ele = c_cate.xpath(
                    'div[@class="pro_inner logsss_event_ps"]/p[@class="all_proNam"]/span[contains(@class,"all_proNamContent")]/a[@class="logsss_event_cl"]')
                href = a_ele.xpath('@href').extract_first()
                link_params = self.seperate_url(href)
                self.logger.info('link_params=[%s]' % (link_params))
                # title = a_ele.xpath('@title').extract_first()
                # cat_id = a_ele.xpath('@cat_id').extract_first()
                # data_rank = a_ele.xpath('@data-rank').extract_first()
                # data_sku = a_ele.xpath('@data-sku').extract_first()
                # data_module = a_ele.xpath('@data-module').extract_first()
                # short_title = c_cate.xpath(
                #     'div[@class="pro_inner logsss_event_ps"]/p[@class="all_proNam"]/span[contains(@class,"all_proNamContent")]/span[@class="shortTitle"]/@text()').extract_first()

                # self.logger.info('title=[%s]' % (title))
                # self.logger.info('cat_id=[%s]' % (cat_id))
                # self.logger.info('data_rank=[%s]' % (data_rank))
                # self.logger.info('data_sku=[%s]' % (data_sku))
                # self.logger.info('data_module=[%s]' % (data_module))
                # self.logger.info('short_title=[%s]' % (short_title))

                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                    "Host": "www.gearbest.com",
                    "Upgrade-Insecure-Requests": "1"
                }

                url = '%(url)s?wid=21' % {'url': link_params['url']}
                yield Request(url,
                              headers=headers,
                              callback=self.parse_commodity)

            else:
                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "en",
                    "Connection": "keep-alive",
                    "Host": "www.gearbest.com",
                    "Upgrade-Insecure-Requests": "1"
                }
                url_params = the_meta['url_params']
                url_params['index'] += 1

                url = '%(category_url)s/%(index)s.html?page_size=%(page_size)s' % url_params
                yield Request(url,
                              headers=headers,
                              meta=the_meta,
                              callback=self.parse_category)

        elif response.status == 301:
            self.logger.info('status=[%s]' % (response.status))
            self.logger.info('location=[%s]' % (response.headers['Location']))

    def parse_commodity(self, response):

        if response.status == 200:
            sel = Selector(response)
            the_meta = response.meta

            item = GearbestItem()
            item['sku'] = self.extract_sku(sel)
            item['page_url'] = self.seperate_url(response.request.url)['url']
            item['category'] = self.extract_category(sel)
            item['title'], item['subtitle'] = self.extract_title(sel)
            item['brand'] = self.extract_brand(sel)
            item['currency'], item['price'] = self.extract_price(sel)
            item['main_image_urls'] = self.extract_main_image_urls(sel)
            item['main_video_urls'] = self.extract_main_video_urls(sel)
            item['additional_image_urls'] = self.extract_additional_image_urls(sel)
            item['specifications'] = self.extract_specifications(sel)
            item['descriptions'] = self.extract_descriptions(sel)
            item['stock_status'] = self.extract_stock_status(sel)

            props_dict = self.extract_props(sel)
            item['props'] = props_dict['true']

            for other_prop_url in props_dict['false']:
                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                    "Host": "www.gearbest.com",
                    "Upgrade-Insecure-Requests": "1"
                }

                url = '%(url)s?wid=21' % {'url': other_prop_url}
                yield Request(url,
                              headers=headers,
                              callback=self.parse_commodity)

            self.logger.info('crawled sku=[%s],title=[%s]' % (item['sku'], item['title']))
            yield item

    def seperate_url(self, url):
        try:
            url_parse = urlparse.urlparse(url)
            query_result = {
                'url': '%(scheme)s://%(domain)s%(path)s' % {'scheme': url_parse.scheme, 'domain': url_parse.netloc, 'path': url_parse.path},
                'params': urlparse.parse_qs(url_parse.query, True),
            }
        except Exception as e:
            self.logger.exception(e)

        return query_result

    def extract_sku(self, sel):
        try:
            return sel.xpath(
                '//meta[@name="GLOBEL:ksku"]/@content').extract_first().strip()
        except Exception as e:
            self.logger.exception(e)
            return None

    def extract_price(self, sel):
        try:
            data_text = ''.join([t.strip() for t in sel.xpath(
                '//*[@id="unit_price"]//text()').extract()])
            regex = r'([^\d,]{0,10})([\d,\.]{1,20})[^\d,\.]{0,20}'
            pattern = re.compile(regex)
            price = pattern.search(data_text)

            return price.group(1), price.group(2)
        except Exception as e:
            # try:
            #     if not sel.xpath('//*[@class="outoffstock-popup-hd"]'):
            #         self.logger.exception(e)
            # except Exception as e:
            #     self.logger.exception(e)
            
            return None, None

    def extract_category(self, sel):
        try:
            return ' > '.join([i.xpath('p/a/span/text()').extract_first().strip()
                               for i in sel.xpath('//li[@itemprop="itemListElement"]')])
        except Exception as e:
            self.logger.exception(e)
            return None

    def extract_title(self, sel):
        good_info_area = sel.xpath('//div[@class="goods-info-top"]')
        title = None
        subtitle = None

        try:
            title = good_info_area.xpath(
                'h1/text()').extract_first().strip()
        except Exception as e:
            self.logger.exception(e)

        try:
            subtitle = good_info_area.xpath(
                'p[@class="shortTitle"]/text()').extract_first().strip()
        except Exception as e:
            subtitle = ''

        return title, subtitle

    def extract_brand(self, sel):
        try:
            return sel.xpath(
                '//a[@class="brand-name"]/text()').extract_first().strip()
        except Exception as e:
            try:
                product_info_list = sel.xpath(
                    '//div[@class="product_pz_info product_pz_style2"]//text()').extract()
                for product_info in product_info_list:
                    brand_index = product_info.lower().find('brand:')
                    if brand_index >= 0:
                        return product_info[brand_index + 6:].strip()
            except Exception as e:
                self.logger.exception(e)
                return None

            return None

    def extract_props(self, sel):
        prop_result_dict = {}
        prop_result_dict['true'] = {}
        prop_result_dict['false'] = set()
        try:
            property_elements = sel.xpath('//*[@class="g_propert"]')
            for property_element in property_elements:
                prop_label = property_element.xpath(
                    '../label[@class="g_label"]/text()').extract_first().strip()[:-1]

                for content in property_element.xpath('a'):
                    prop_content = content.xpath(
                        'text()').extract_first().strip()
                    commodity_url = content.xpath(
                        '@data-href').extract_first().strip()
                    try:
                        is_checked = True if 'checked' == content.xpath(
                            '@class').extract_first().strip().lower() else False
                        prop_result_dict['true'][prop_label] = prop_content

                    except Exception as e:
                        is_checked = False
                        prop_result_dict['false'].add(commodity_url)

            return prop_result_dict

        except Exception as e:
            self.logger.exception(e)
            return None

    def extract_main_image_urls(self, sel):
        main_image_url_list = []
        try:
            image_li_list = sel.xpath(
                '//div[@class="n_thumbImg_item"]/ul[@class="js_scrollableDiv"]/li')

            for image_li in image_li_list:
                main_image_url_list.append(image_li.xpath(
                    'a/img/@data-normal-img').extract_first().strip())

        except Exception as e:
            self.logger.exception(e)

        return main_image_url_list

    def extract_main_video_urls(self, sel):
        main_video_list = []
        try:
            video_li_list = sel.xpath(
                '//li[@class="n_video"]')
            for video_li in video_li_list:
                main_video_list.append('https://www.youtube.com/embed/%s' % (video_li.xpath(
                    '@data-vide').extract_first().strip()))

        except Exception as e:
            self.logger.exception(e)

        try:
            video_li_list = sel.xpath(
                '//div[@class="video_img js_click_video"]')
            for video_li in video_li_list:
                main_video_list.append('https://www.youtube.com/embed/%s' % (video_li.xpath(
                    '@data-videonum').extract_first().strip()))

        except Exception as e:
            self.logger.exception(e)

        return main_video_list

    def extract_additional_image_urls(self, sel):
        additional_image_url_list = []
        try:
            image_li_list = sel.xpath(
                '//div[@class="self-adaption"]/p')

            for image_li in image_li_list:
                image_url_ele = image_li.xpath('img/@data-original')
                additional_image_url_list.append(
                    image_url_ele.extract_first().strip()) if image_url_ele else None

        except Exception as e:
            self.logger.exception(e)

        return additional_image_url_list

    def extract_descriptions(self, sel):
        try:
            descriptions_area = sel.xpath('//div[@class="product_pz_info mainfeatures"]')
            return descriptions_area.get('data') if descriptions_area else None
        except Exception as e:
            self.logger.exception(e)
            return ''

    def extract_specifications(self, sel):
        try:
            specifications_area = sel.xpath('//div[@class="product_pz_info product_pz_style2"]')
            return specifications_area.get('data') if specifications_area else None
        except Exception as e:
            self.logger.exception(e)
            return ''

    def extract_stock_status(self, sel):
        stock_status = ''

        if sel.xpath('//*[@id="new_addcart"]'):
            stock_status += 'instock'

        elif sel.xpath('//*[@class="no_addToCartBtn"]'):
            try:
                no_add_to_cart_btn_text = sel.xpath(
                    '//*[@class="no_addToCartBtn"]/text()').extract_first().strip().lower()

                if no_add_to_cart_btn_text.find('discontinued') >= 0:
                    stock_status += 'discontinued'
                elif no_add_to_cart_btn_text.find('out') >= 0 and no_add_to_cart_btn_text.find('of') > 0 and no_add_to_cart_btn_text.find('stock') > 0:
                    stock_status += 'outofstock'

            except Exception as e:
                stock_status += 'unknown'
                self.logger.exception(e)

        elif sel.xpath('//*[@id="js_arrival_new_addcart"]'):
            stock_status += 'pendingarrival'

        return stock_status
