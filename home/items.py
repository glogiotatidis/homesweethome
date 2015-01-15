# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Home(scrapy.Item):
    id = scrapy.Field()
    origin = scrapy.Field()
    title = scrapy.Field()
    area = scrapy.Field()
    location = scrapy.Field()
    floor = scrapy.Field()
    full_location = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    image = scrapy.Field()
    url = scrapy.Field()
    type = scrapy.Field()
    state = scrapy.Field()
    buildon = scrapy.Field()
    direction = scrapy.Field()
    rooms = scrapy.Field()
    bathrooms = scrapy.Field()
    parking = scrapy.Field()
    parkingtype = scrapy.Field()
    storageroom = scrapy.Field()
    heating = scrapy.Field()
    airconditioning = scrapy.Field()
    securedoor = scrapy.Field()
    fireplace = scrapy.Field()
    garden = scrapy.Field()
    created_on = scrapy.Field()
    updated_on = scrapy.Field()
    views = scrapy.Field()
    adowner_type = scrapy.Field()
    adowner = scrapy.Field()
    lat = scrapy.Field()
    lon = scrapy.Field()
    images = scrapy.Field()
    last_cralwed = scrapy.Field()
