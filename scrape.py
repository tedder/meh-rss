#!/usr/bin/python

import requests
from lxml import html
import PyRSS2Gen
import datetime
import StringIO

page = requests.get('https://meh.com/')
tree = html.fromstring(page.text)

feat = tree.xpath('//section[@class="features"]/h2/text()')[0]
print feat
price = tree.xpath('//button[@class="buy-button"]/span/text()')[0]
print price
img = tree.xpath('//div[@class="photos"]/div')[0]
img_url img.attrib.get('style').replace("background-image: url('", '').replace("')", '')

rss = PyRSS2Gen.RSS2(
  title = "meh.com scraped feed",
  link = "https://meh.com/",
  description = "daily deal from meh.com",
  lastBuildDate = datetime.datetime.now(),
  items = [
    PyRSS2Gen.RSSItem(
      title = feat,
      link = "https://meh.com/",
      description = """ <![CDATA[ %s<br />price: %s<br /><img src="%s" /> ]]> """ % (feat, price, img_url)
    )
  ]
)

rssfile = StringIO.StringIO()
rss.write_xml(rssfile)

s3bucket = boto.connect_s3().get_bucket('tedder')
s3key =  s3bucket.new_key('meh/rss.xml')
s3key.set_metadata('Content-Type', 'application/rss+xml')
s3key.set_contents_from_string(rssfile.getvalue(), replace=True, reduced_redundancy=True, headers={'Cache-Control':'public, max-age=3600'}, policy="public-read")


