# -*- coding: utf-8 -*-

import socket
import re
import time
import os
from bs4 import BeautifulSoup
import MySQLdb
import hashlib
import get_uid_data
import urllib
db = MySQLdb.connect("localhost","root", "root@123", "renniso")

cursor = db.cursor()

redis = get_uid_data.StrictRedis(host='127.0.0.1', port=6379)

socket.setdefaulttimeout(60)

#显示下载进度
def schedule(a,b,c):
    per = 100.0 * a * b / c
    if per > 100 :
        per = 100
    print '%.2f%%' % per

def get_html(url):
    try:
        page = urllib.urlopen(url)
        html = page.read()
    except socket.error:
        print "urllib request timeout"
    print 'read:'
    return html

def insert_category(cate_name, english_name):
    sql = "insert into so_image_category (`cate_name`,`english_name`,`tag`,`create_time`) values (%s,%s,%s, %s)"
    now = int(time.time())

    cursor.execute(sql, (cate_name, english_name, cate_name, now))
    return db.commit()


def get_cate_data():
    sql = "select * from so_image_category where cate_id>=3 and cate_id<=12"
    cursor.execute(sql)
    return cursor.fetchall()


def update_cate_status(cate_id):
    sql = " update so_image_category set status=1 where cate_id=%s"
    cursor.execute(sql,[cate_id])
    return db.commit()


def get_home_cate_name(url):
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser", from_encoding="utf-8")

    html = soup.find(name='div', attrs={"class":"nav"}).findAll("a")

    for item in html:
        english_name = item.attrs['href'].replace("/","")
        if english_name:
            insert_category(item.getText(), english_name)

    return html


def get_cate_page(url):
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser", from_encoding="utf-8")

    print soup.find(name='div', attrs={"id":"pageNum"})
    html = soup.find(name='div', attrs={"id":"pageNum"}).findAll("a")
    last_page = html[-1].attrs['href']

    num = filter(str.isdigit,str(last_page))
    num = int(num)
    for i in range(1,num+1):
        if i==1:
            str_page = "/index.html"
        else:
            str_page = "/index_"+str(i)+".html"
        list_url = url+str_page
        redis_list = get_uid_data.get(list_url)
        if not redis_list:
            get_page_article(list_url)
            get_uid_data.set(list_url, 1)


def insert_article(title, thumb_image, image_url,tag,cate_name,source):
    sql = "insert into so_image (`title`,`thumb_image`,`image_url`,`tag`,`cate_name`,`source`,`create_time`) values (%s,%s,%s,%s,%s,%s,%s)"
    now = int(time.time())

    cursor.execute(sql, (title, thumb_image, image_url,tag,cate_name,source, now))
    return db.commit()

def get_page_article(url):
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser", from_encoding="utf-8")

    article_list = soup.findAll(name='div', attrs={"class":"img"})
    for article in article_list:
        image_src =  article.find("img").attrs['data-original']
        #image_src = get_thumb_image(image_src)
        title = article.find("img").attrs['title']
        a1 = re.compile(r'\[.*?\]')
        title = a1.sub('',title)
        article_url = "http://www.996yx.com"+article.find("a").attrs['href']
        #image_url = get_article_detail(article_url)
        cate_name=url.split("/")[3]
        key = article.find("a").attrs['href']
        redis_data = get_uid_data.get(key)
        if not redis_data:
            insert_article(title, image_src, "","",cate_name,article_url)
            get_uid_data.set(key, 1)


def get_article_detail(url):
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser", from_encoding="utf-8")

    #获取标签列表
    tag_list = soup.find(name='div', attrs={"class":"fbl"})
    tag_arr = []
    for tag in tag_list.findAll("a"):
        tag_name = tag.get_text()
        if tag_name not in tag_arr:
            tag_arr.append(tag_name)

    tag_str =  ";".join(tag_arr)

    #获取列表最大分页
    article_list = soup.find(name="div", attrs={"class":"pages"})

    article_list = article_list.findAll("li")
    if not article_list:
        return ""
    last_page = article_list[-1].find("a").attrs['href']
    print last_page
    last_page = last_page.split("_")
    num = filter(str.isdigit,str(last_page[1]))
    num = int(num)

    img_list = ""
    for i in range(1,num+1):
        if i==1:
            url_detail  = url
        else:
            url_detail = url.replace(".html","_"+str(i)+".html")
        img_url = get_detail_image(url_detail)
        img_list +=img_url+";"

    return img_list[0:-1],tag_str

def get_detail_image(url):
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser", from_encoding="utf-8")

    article_list = soup.find(name='div', attrs={"id":"big-pic"}).find("img")

    image_url = article_list.attrs['src']

    return image_url

    md = hashlib.md5()
    md5_str = md.update(image_url)
    md5_str = md.hexdigest()

    picpath = "./image/aa76b20ff78e80"

    if not os.path.exists(picpath):   #路径不存在时创建一个
        os.makedirs(picpath)


    target = picpath+'/%s.jpg' % md5_str
    if not os.path.exists(target):
        urllib.urlretrieve(image_url, target, schedule)

    return target


def get_thumb_image(image_url):

    md = hashlib.md5()
    md5_str = md.update(image_url)
    md5_str = md.hexdigest()

    picpath = "./image/aa76b20ff78e80"

    if not os.path.exists(picpath):   #路径不存在时创建一个
        os.makedirs(picpath)

    target = picpath+'/%s.jpg' % md5_str
    if not os.path.exists(target):
        urllib.urlretrieve(image_url, target, schedule)

    return target


if __name__ == '__main__':
    #get_home_cate_name("http://www.996yx.com/")
    data = get_cate_data()

    for dd in data:
        url = "http://www.996yx.com/"+dd[2]
        print "start downloading:"+url
        get_cate_page(url)
        update_cate_status(dd[0])
        print "end downloading:"+url



    print "Download has finished."
