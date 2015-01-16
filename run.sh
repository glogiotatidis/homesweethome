#!/bin/bash

DATE=`date +%Y.%m.%d`
mkdir -p "data/$DATE"
scrapy crawl home -s JOBDIR=crawls/somespider-1 -s DOWNLOAD_DELAY=0.6 -o "data/$DATE/items.json"
