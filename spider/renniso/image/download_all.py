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


socket.setdefaulttimeout(60)

#显示下载进度
def schedule(a,b,c):
    per = 100.0 * a * b / c
    if per > 100 :
        per = 100
    print '%.2f%%' % per




def get_article_data():
    sql = "select image_id,thumb_image,image_url,source from so_image where status=1 limit 0, 1000"
    cursor.execute(sql)
    return cursor.fetchall()


def update_article(id,local_url,local_thumb_image):
    sql = "update so_image set status=%s,local_url=%s,local_thumb_image=%s where image_id=%s"
    cursor.execute(sql,(2,local_url, local_thumb_image,id))
    return db.commit()


def download_image(image_id,thumb_image,image_url,source):
    md = hashlib.md5()
    md5_source = md.update(source)
    md5_source = md.hexdigest()
    picpath = "./image/"

    id_len = str(image_id)
    id_len = 10-len(id_len)+10

    source = md5_source[10:id_len]

    picpath += source[:4] + str(image_id) + source[4:]

    if not os.path.exists(picpath):   #路径不存在时创建一个
        os.makedirs(picpath)

    image_list = image_url.split(",")


    local_url = "";

    md5_thumb = md.update(thumb_image)
    md5_thumb = md.hexdigest()

    #下载缩图
    local_thumb_image = picpath+'/%s.jpg' % md5_thumb
    if not os.path.exists(local_thumb_image):
        try:
            urllib.urlretrieve(thumb_image, local_thumb_image, schedule)
        except socket.error:
            os.remove(local_thumb_image)
            print "delete:"+local_thumb_image


    for img_url in image_list:
        md5_str = md.update(img_url)
        md5_str = md.hexdigest()
        target = picpath+'/%s.jpg' % md5_str
        local_url+=target+","

        if not os.path.exists(target):
            try:
                urllib.urlretrieve(img_url, target, schedule)
                print target
            except socket.error:
                os.remove(target)
                print "delete:"+target
        else:
            print img_url+"已下载"

    update_article(image_id,local_url[0:-1],local_thumb_image)

    return True



if __name__ == '__main__':

    data = get_article_data()
    for dd in data:
        url = dd[3]
        print "start downloading:"+url
        #image_id,thumb_image,image_url,source
        download_image(dd[0],dd[1],dd[2],dd[3])
        print "end downloading:"+url



    print "Download has finished."
