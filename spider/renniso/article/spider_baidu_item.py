# -*- coding: utf-8 -*-

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
import urllib
import smtplib
import json
from email.mime.text import MIMEText
import sys
reload(sys)
sys.setdefaultencoding('utf8')

db = MySQLdb.connect("localhost","root", "root@123", "23")
cursor = db.cursor()

redis = redis.Redis("localhost", 6379)

socket.setdefaulttimeout(60)

log_filename = "/data/www/python/spider/renniso/article/item.log"
logging.basicConfig(filename=log_filename, filemode="a", level=logging.DEBUG)

now = time.strftime('%Y-%m-%d %X', time.localtime() )

#显示下载进度
def schedule(a,b,c):
    per = 100.0 * a * b / c
    if per > 100 :
        per = 100
    print '%.2f%%' % per


def getHtml(url):
    page = urllib.urlopen(url)
    html = page.read()
    return html

def is_exist_uid(uid):
    data = redis.get(uid)
    if data:
        return True
    else:
        return False


#添加百度云用户信息
def insert_baidu_user(data):

    sql = "insert into so_baidu_user (`uid`,`create_time`) values (%s,%s)"

    cursor.executemany(sql,data)
    result = db.commit()

    return result


def insert_into_item(item_list):
    sql = "insert into so_baidu_resource (`uid`,`share_id`,`category`,`title`,`file_info`," \
          "`user_info`,`create_time`,`feed_type`,`file_ext`)" \
          " values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    cursor.executemany(sql, item_list)
    return db.commit()


def get_all_user():

    sql = "select uid from so_baidu_user where status=0"

    cursor.execute(sql)
    return cursor.fetchall()


def update_user(uid):

    # data = (
    #     user_info['username'],user_info['user_avatar'],
    #     user_info['share_num'], user_info['special_num'],user_info['sign_num'],
    #     user_info['fans_num'],1, uid
    # )

    sql = "update so_baidu_user set status=%s where uid=%s"

    cursor.execute(sql,('1', uid))
    result = db.commit()

    return result


def send_email(content):
    sender = '123123123'
    receiver = '123123123@qq.com'

    smtp_server = 'smtp.163.com'
    username = '123123'
    password = '123123'

    subject = 'spider pan error'
    msg = MIMEText('<html><h1>hello windgo</h1><div>'+content+'</div></html>','html','utf-8')

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    smtp = smtplib.SMTP()
    smtp.connect(smtp_server)
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, msg.as_string())
    smtp.quit()


def spider_baidu_pan(uid):

    time_now = time.time()
    time_now = int(time_now*1000)
    url = "http://pan.baidu.com/pcloud/feed/getsharelist?" \
            "t="+str(time_now)+"&category=0&auth_type=1" \
            "&request_location=share_home&start=0&limit=60&query_uk="+str(uid)+ \
            "&channel=chunlei&clienttype=0&web=1&bdstoken=9b1b19e4686b887994c4bb425beb54d4"
    content = getHtml(url)
    content = json.loads(content)
    print url
    total_count = content['total_count']
    if content.has_key('records'):
        print 'first one:'
        download_pan_item(content['records'])

    page = int(total_count/60)+1

    if page > 1 :
        for i in range(2,page+1):
            start = 60 * (i-1)
            url = "http://pan.baidu.com/pcloud/feed/getsharelist?" \
                "t="+str(time_now)+"&category=0&auth_type=1" \
                "&request_location=share_home&start="+str(start)+"&limit=60&query_uk="+str(uid)+ \
                "&channel=chunlei&clienttype=0&web=1&bdstoken=9b1b19e4686b887994c4bb425beb54d4"
            content = getHtml(url)
            content = json.loads(content)
            if content.has_key('records'):
                download_pan_item(content['records'])

            print 'page:'+str(i)


def download_pan_item(records):

    user_info = {}
    file_info = {}
    item_list = []
    if records:
        for record in records:
            if not record.has_key('username'):
                continue
            user_info['avatar_url'] = record['avatar_url']
            user_info['username'] = record['username']
            user_info['desc'] = record['desc']

            if record.has_key("shareid"):
                share_id = record['shareid']
            elif record.has_key("album_id"):
                share_id = record['album_id']
            else:
                share_id = 0

            file_info['source_id'] = record['source_id']
            if record.has_key("filelist"):
                if len(record['filelist']) > 0:
                    file_list = record['filelist'][0]
                    file_info['fs_id'] = file_list['fs_id']
                    file_info['size'] = file_list['size']
                    file_info['isdir'] = file_list['isdir']
                    file_info['share_time'] = record['feed_time']

                if record.has_key('shorturl'):
                    file_info['shorturl'] = record['shorturl']
            elif record.has_key("operation"):
                if len(record['operation'])>0:
                    file_list = record['operation'][0]
                    file_info['file_count'] = record['filecount']
                    file_info['isdir'] = 1
                    file_info['share_time'] = file_list['op_time']
            file_ext = os.path.splitext(record['title'])[1]
            if len(file_ext)>10:
                file_ext = file_ext[0:10]
            user_resource = (
                record['uk'],share_id,record['category'],record['title'],json.dumps(user_info),
                json.dumps(file_info),int(time.time()),record['feed_type'],file_ext
            )
            item_list.append(user_resource)

    return insert_into_item(item_list)


def get_baidu_user_info(url):
    html = getHtml(url)
    soup = BeautifulSoup(html, "html.parser", from_encoding="utf-8")

    user = soup.find(name='div', attrs={"class":"avatar"})

    user_info = {}

    user_info['user_avatar'] = user.find("img").attrs['src']
    user_info['username'] = soup.find(name='div', attrs={"class":"username"}).getText().replace("点击进入TA的百度云盘首页","")

    num_list = soup.find(name="div", attrs={"class","num"})

    item_list = re.findall(r'(\w*[0-9]+)\w*',num_list.getText())

    user_info['share_num'] = item_list[0]
    user_info['special_num'] = item_list[1]
    user_info['sign_num'] = item_list[2]
    user_info['fans_num'] = item_list[3]

    return user_info


if __name__ == '__main__':

   data = get_all_user()

   for dd in data:
       spider_baidu_pan(dd[0])
       result = update_user(dd[0])
       time.sleep(3)
       print result