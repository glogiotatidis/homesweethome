# -*- coding: utf-8 -*-

# Scrapy settings for home project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'home'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
DOWNLOAD_DELAY = 0.8
LOG_FILE = 'scrapy.log'

SPIDER_MODULES = ['home.spiders']
NEWSPIDER_MODULE = 'home.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'home (+http://www.yourdomain.com)'
