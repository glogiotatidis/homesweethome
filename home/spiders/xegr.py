# -*- coding: utf-8 -*-

import re
from datetime import datetime

import scrapy

from ..items import Home

calendar = {
    u'Ιανουαρίου': 'Jan',
    u'Φεβρουαρίου': 'Feb',
    u'Μαρτίου': 'Mar',
    u'Απριλίου': 'Apr',
    u'Μαΐου': 'May',
    u'Ιουνίου': 'Jun',
    u'Ιουλίου': 'Jul',
    u'Αυγούστου': 'Aug',
    u'Σεπτεμβρίου': 'Sep',
    u'Οκτωβρίου': 'Oct',
    u'Νοεμβρίου': 'Nov',
    u'Δεκεμβρίου': 'Dec'
}

def parse_date(date):
    date = date.xpath('text()').extract()[0]
    date = date.split(',')[1]
    date = date.split()
    date[1] = calendar[date[1]]
    date = ' '.join(date)
    return datetime.strptime(date, '%d %b %Y')

class HomeSpider(scrapy.Spider):
    name = 'home'
    allowed_domains = ['xe.gr']
    start_urls = [
        # Βόρεια προάστεια, άνω πατήσια αμπελόκηποι, κτλ
        'http://www.xe.gr/property/search?System.item_type=re_residence&Transaction.type_channel=117518&Geo.area_id_new__hierarchy=82272,82487,82482,82488,82489,82342,82353,82355,82349,82352,82320,82323&page=1&per_page=50'
        ]

    def parse_listing(self, response):
        for url in response.css('a').xpath('@href').extract():
            if re.match('^/property/poliseis\|katoikies\|\w+\|\d+\.html$', url):
                yield scrapy.http.Request(url='http://www.xe.gr' + url)
                if self.crawler.settings.get('DEBUG', False):
                    return
        try:
            next_url = response.css('.white_button.right').xpath('@href').extract()[0]
        except IndexError:
            return
        yield scrapy.http.Request(url='http://www.xe.gr' + next_url)

    def parse_entry_details(self, response):
        t = response.css('#box_ad_details_actions').xpath('div/script/text()').extract()
        data = eval(t[0].replace('\n','').replace('\t','')[12:])
        home = response.meta['home']
        home['origin'] = 'xe.gr'
        home['id'] = data['id']
        home['area'] = data['area']
        home['image'] = data['social_networking_image']
        home['url'] = data['social_networking_url']
        home['title'] = data['title']
        home['description'] = data['social_networking_desc']
        home['price'] = data['price'].replace('&euro;', '').replace('.', '')

        for row in response.css('#box_ad_characteristics').xpath('div/table/tr'):
            th = row.xpath('th/text()').extract()[0]
            td = row.xpath('td/text()').extract()[0]

            mapping = {
                u'Είδος:': 'type',
                u'Κατάσταση:': 'state',
                u'Έτος Κατασκευής:': 'buildon',
                u'Προσανατολισμός:': 'direction',
                u'Υπνοδωμάτια:': 'rooms',
                u'Μπάνια/ WC:': 'bathrooms',
                u'Πάρκιν:': 'parking',
                u'Είδος Πάρκιν:': 'parkingtype',
                u'Με αποθήκη:': 'storageroom',
                u'Αυτόνομη θέρμανση:': 'heating',
                u'Κλιματισμός:': 'airconditioning',
                u'Πόρτα ασφαλείας:': 'securedoor',
                u'Τζάκι:': 'fireplace',
                u'Κήπος:': 'garden'
            }

            mapped = mapping.get(th)
            if mapped:
                home[mapped] = td

        yield home

    def parse_location(self, response):
        home = response.meta['home']
        home['lat'] = float(response.css('#lat').xpath('@value').extract()[0])
        home['lon'] = float(response.css('#lng').xpath('@value').extract()[0])

        if u'Φωτογραφίες' in response.css('.tabs2').extract()[0]:
            request = scrapy.http.Request(response.url[:-42] + '|%CF%86%CF%89%CF%84%CE%BF%CE%B3%CF%81%CE%B1%CF%86%CE%B9%CE%B5%CF%82.html')
        else:
            request = scrapy.http.Request(response.url[:-42] + '.html?mode=spec')

        request.meta['home'] = home
        yield request

    def parse_images(self, response):
        home = response.meta['home']
        home['images'] = response.css('#adg_cycle').xpath('img/@src').extract()

        request = scrapy.http.Request(response.url[:-72] + '.html?mode=spec')
        request.meta['home'] = home
        yield request

    def parse_entry(self, response):
        home = Home()
        home['last_cralwed'] = datetime.now()
        mapping = {
            u'Δημιουργία αγγελίας:': {
                'key': 'created_on',
                'function': parse_date
            },
            u'Tελευταία τροποποίηση αγγελίας:': {
                'key': 'updated_on',
                'function': parse_date
            },
            u'Αγγελία από:': {
                'key': 'adowner_type',
                'function': lambda x: x.xpath('text()').extract()[0]
            },
            u'Η αγγελία έχει έως τώρα:': {
                'key': 'views',
                'function': lambda x: x.css('.counter').xpath('strong/text()').extract()[0]
            },
            u'Η σελίδα του επαγγελματία': {
                'key': 'adowner',
                'function': lambda x: x.css('a').xpath('@href').extract()[0]
            },
        }

        for table in response.css('.ad_details_table'):
            for th, td in zip(table.css('th').xpath('text()').extract(),
                              table.css('td')):
                mapped = mapping.get(th)
                if mapped:
                    home[mapped['key']] = mapped['function'](td)

        if u'Χάρτης' in response.css('.tabs2').extract()[0]:
            request = scrapy.http.Request(response.url[:-5] + '|%CF%87%CE%B1%CF%81%CF%84%CE%B7%CF%82.html')
        else:
            request = scrapy.http.Request(response.url + '?mode=spec')
        request.meta['home'] = home
        yield request

    def parse(self, response):
        if response.url.startswith('http://www.xe.gr/property/search'):
            return self.parse_listing(response)
        elif response.url.startswith('http://www.xe.gr/property/poliseis|katoikies|'):
            if response.url.endswith('spec'):
                return self.parse_entry_details(response)
            elif response.url.endswith('|%CF%87%CE%B1%CF%81%CF%84%CE%B7%CF%82.html'):
                return self.parse_location(response)
            elif response.url.endswith('|%CF%86%CF%89%CF%84%CE%BF%CE%B3%CF%81%CE%B1%CF%86%CE%B9%CE%B5%CF%82.html'):
                return self.parse_images(response)
            else:
                return self.parse_entry(response)
