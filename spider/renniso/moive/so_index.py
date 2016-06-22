# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import socket
import re
import time
import os
from bs4 import BeautifulSoup
import MySQLdb
import hashlib
import urlparse
import redis
import logging
import urllib2
import smtplib
from email.mime.text import MIMEText
import sys
reload(sys)
sys.setdefaultencoding('utf8')

db = MySQLdb.connect("localhost","root", "root@123", "youyou")
cursor = db.cursor()

chromedriver = "/usr/local/bin/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver

browser = webdriver.Chrome(chromedriver)

redis = redis.Redis("localhost", 6379, 1)

socket.setdefaulttimeout(60)

log_filename = "/data/www/study/python/spider/renniso/moive/result.log"
logging.basicConfig(filename=log_filename, filemode="a", level=logging.DEBUG)

now = time.strftime('%Y-%m-%d %X', time.localtime() )

#显示下载进度
def schedule(a,b,c):
    per = 100.0 * a * b / c
    if per > 100 :
        per = 100
    print '%.2f%%' % per


def get_html_urllib(url,i):

    try:
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        html = response.read()
        print url

    except socket.error:
        redis.set("urllib:", i)
        print "urllib request timeout"

    return html


def get_html(url):

    browser.set_page_load_timeout(30)
    try:
        browser.get(url)
        print url
    except TimeoutException:
        print "browser request timeout 30s"
        browser.quit()

    return browser.page_source


def is_exist_uid(uid):
    data = redis.get(uid)
    if data:
        return True
    else:
        return False


#添加百度云用户信息
def insert_baidu_user(user_info,url):

    if is_exist_uid(user_info['uid']):
        return "redis uid exist uid="+user_info['uid']+" url="+url

    now = int(time.time())
    data = (
        str(user_info['uid']),str(user_info['username']),str(user_info['user_avatar']),
        str(user_info['share_num']),str(user_info['special_num']),str(user_info['sign_num']),
        str(user_info['fans_num']), str(now),'0'
    )

    sql = "insert into so_baidu_user (`uid`,`username`,`user_avatar`,`share_num`,`special_num`," \
          "`sign_num`,`fans_num`,`create_time`,`status`) values (%s,%s,%s, %s,%s,%s,%s,%s,%s)"

    cursor.execute(sql,data)
    result = db.commit()

    if result is not None:
        db.rollback()

        log = "mysql:error rollback uid="+user_info['uid']+" url="+url
    else:
        redis.set(user_info['uid'], 1)
        log = "mysql:ok result="+str(result)+" url="+url

    return log



def get_baidu_user_info(url):
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser", from_encoding="utf-8")

    user = soup.find(name='div', attrs={"class":"info"})

    user_info = {}

    user_info['user_avatar'] = user.find("img").attrs['src']
    user_info['username'] = user.find("b").getText()

    url = user.find("a").attrs['href']
    user_info['uid'] = url.split("?")[-1]
    user_info['uid'] = user_info['uid'].split("=")[-1]

    num_list = user.findAll(name="div", attrs={"class","num"})

    item_list = []
    for item in num_list:
        item_list.append(item.find("span").getText())

    user_info['share_num'] = item_list[0]
    user_info['special_num'] = item_list[1]
    user_info['sign_num'] = item_list[2]
    user_info['fans_num'] = item_list[3]

    return user_info



if __name__ == '__main__':

    while True:
        i = redis.get("end")
        print "start:"+str(i)
        url = "http://www.bdsola.com/d/"+str(i)+".html"
        user_info = get_baidu_user_info(url)
        result = insert_baidu_user(user_info,url)
        if int(user_info['share_num']) > 0 :
            increment = int(user_info['share_num'])
        else:
            increment = 1

        next_start = int(i) + increment

        redis.set("end", next_start)

        logging.info(now+"  start:"+str(i)+"next:"+str(next_start))
        print 'next_start:'+str(next_start)
        time.sleep(1)

    db.close()

    browser.close()
    print "Download has finished."

