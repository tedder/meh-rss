#!/usr/bin/python

import boto
import requests
from lxml import html
import PyRSS2Gen
import datetime
import StringIO

LINK = "https://meh.com/" # probably clicktrack this later.

page = requests.get('https://meh.com/')
tree = html.fromstring(page.text)

feat = tree.xpath('//section[@class="features"]/h2/text()')[0]
price = tree.xpath('//button[@class="buy-button"]/span/text()')[0]
img = tree.xpath('//div[@class="photos"]/div')[0]
img_url = img.attrib.get('style').replace("background-image: url('", '').replace("')", '')
item = tree.xpath('//div[@class="front"]/form/@action')[0][1:][:-5]

rss = PyRSS2Gen.RSS2(
  title = "meh.com scraped feed",
  link = LINK,
  ttl = 300, # cache 300sec
  docs = "https://github.com/tedder/meh-rss",
  description = "daily deal from meh.com",
  lastBuildDate = datetime.datetime.now(),
  items = [
    PyRSS2Gen.RSSItem(
      title = feat,
      link = LINK + item,
      #description = """ <![CDATA[ %s<br />price: %s<br /><img src="%s" /> ]]> """ % (feat, price, img_url)
      description = """item: <b><a href="%s">%s</a></b>  <br />price: <b>%s</b><br /><img src="%s" />""" % (LINK + item, feat, price, img_url)
    )
  ]
)

rssfile = StringIO.StringIO()
rss.write_xml(rssfile)

s3bucket = boto.connect_s3().get_bucket('tedder')
s3key =  s3bucket.new_key('rss/meh.xml')
s3key.set_metadata('Content-Type', 'application/rss+xml')
s3key.set_contents_from_string(rssfile.getvalue(), replace=True, reduced_redundancy=True, headers={'Cache-Control':'public, max-age=300'}, policy="public-read")


