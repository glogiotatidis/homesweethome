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
    u'Μαίου': 'May',
    u'Ιουνίου': 'Jun',
    u'Ιουλίου': 'Jul',
    u'Αυγούστου': 'Aug',
    u'Σεπτεμβρίου': 'Sep',
    u'Οκτωβρίου': 'Oct',
    u'Νοεμβρίου': 'Nov',
    u'Δεκεμβρίου': 'Dec'
}

def parse_date(date):
    date = date.split(',')[1]
    date = date.split()
    date[1] = calendar[date[1]]
    date = ' '.join(date)
    return datetime.strptime(date, '%d %b %Y')

class HomeSpider(scrapy.Spider):
    name = 'home'
    allowed_domains = ['xe.gr']
    start_urls = [
        'http://www.xe.gr/property/search?Geo.area_id_new__hierarchy=82447&Geo.area_id_new__hierarchy=82433&Geo.area_id_new__hierarchy=82434&Geo.area_id_new__hierarchy=82448&Geo.area_id_new__hierarchy=82444&Geo.area_id_new__hierarchy=82442&Geo.area_id_new__hierarchy=82446&Item.area.from=160&Item.type=31947&Item.type=31946&System.item_type=re_residence&Transaction.price.to=500000&Transaction.type_channel=117518&page=1&per_page=50'
        ]

    def parse_listing(self, response):
        for url in response.css('a').xpath('@href').extract():
            if re.match('^/property/poliseis\|katoikies\|\w+\|\d+\.html$', url):
                yield scrapy.http.Request(url='http://www.xe.gr' + url)
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

    def parse_entry(self, response):
        request = scrapy.http.Request(response.url + '?mode=spec')
        home = Home()
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
                'key': 'adowner',
                'function': lambda x: x
            },
            u'Η αγγελία έχει έως τώρα:': {
                'key': 'views',
                'function': lambda x: x
            }
        }

        for table in response.css('.ad_details_table'):
            for th, td in zip(table.css('th').xpath('text()').extract(),
                              table.css('td').xpath('text()').extract()):
                mapped = mapping.get(th)
                if mapped:
                    home[mapped['key']] = mapped['function'](td)

        request.meta['home'] = home
        yield request

    def parse(self, response):
        if response.url.startswith('http://www.xe.gr/property/search'):
            return self.parse_listing(response)
        elif response.url.startswith('http://www.xe.gr/property/poliseis|katoikies|'):
            if response.url.endswith('spec'):
                return self.parse_entry_details(response)
            else:
                return self.parse_entry(response)
