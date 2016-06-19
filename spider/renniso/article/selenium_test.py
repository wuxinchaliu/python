# -*- coding: utf-8 -*-

from selenium import webdriver
import time
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

chromedriver = "/usr/local/bin/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver

browser = webdriver.Chrome(chromedriver)

# browser.get("http://www.baidu.com/")
#
# time.sleep(3)
#
# browser.find_element_by_id('kw').send_keys("zhangyanqing")
# browser.find_element_by_id('su').click()
# browser.get("http://www.hnebbs.com/")

url = "http://www.bdsola.com/d/9224.html"

browser.get(url)

print browser.page_source

browser.get("http://www.bdsola.com/d/9234.html")
print '2'
browser.get("http://www.bdsola.com/d/9244.html")
print '3'
browser.close()