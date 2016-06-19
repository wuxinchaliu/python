# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib
import re
import time
import os
import hashlib
import sys
import MySQLdb
import json
import base64
reload(sys)
sys.setdefaultencoding('utf-8')

db = MySQLdb.connect("192.168.1.161", "qiaonaoke", "qiaonaoke_psw", "qiaonaoke")
cursor = db.cursor()


def schedule(a,b,c):
    per = 100.0 * a * b / c
    if per > 100 :
        per = 100
    print '%.2f%%' % per


def get_html(url):
    page = urllib.urlopen(url)
    html = page.read()

    return html


def output_html(title, content):
    fout = open("/data/www/study/output.html", "w")
    fout.write("<html><head><meta charset='UTF-8'><title>%s</title></head><body>" % title)
    fout.write("<h1>%s</h1>" % title)
    fout.write("%s" % content)
    fout.write("</body></html>")


def get_str_md5(string):
    md = hashlib.md5()
    md5_str = md.update(string)
    md5_str = md.hexdigest()
    return md5_str


def get_download_data():
    sql = "select source,thumb_image,vid,id from qnk_cerebra where is_download=0"
    cursor.execute(sql)

    return cursor.fetchall()


def update_download_status(data):
    sql = "update qnk_cerebra set is_download=%s where id=%s"

    cursor.execute(sql, data)
    return db.commit()


def update_download_data(is_download, img_url,video_url, id):
    sql = "update qnk_cerebra set is_download=%s,image=%s,url=%s where id=%s"
    cursor.execute(sql, (is_download, img_url, video_url, id))
    return db.commit()


def download_img(url, pic_path):
    if not os.path.exists(pic_path):  # 路径不存在时创建一个
        os.makedirs(pic_path)

    md5_str = get_str_md5(url)
    target = pic_path + md5_str +'.jpg'

    if os.path.exists(target):
        print "图片文件"+target+'已存在,不要重复下载'
        return target

    urllib.urlretrieve(url, target, schedule)

    return target


def download_video(url, video_path):
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
    div_video = soup.find(name="div", attrs={"id": "video"})

    play_id = div_video.attrs['tt-videoid']

    if play_id is None:
        print "抓取不到数据,或您输入地址有误"
        os._exit(0)

    call_url = "http://i.snssdk.com/video/urls/1/toutiao/mp4/"+play_id+"?callback=tt_playerikzen"

    html = get_html(call_url)
    kk = html.replace("tt_playerikzen(", "")
    response = kk.replace(")", "")
    if response is None:
        print 'json解析失败'
        os._exit(0)
    response = json.loads(response)

    response_data = response['data']['video_list']
    key = 'video_' + str(response['total'])
    if response_data[key]['vtype'] != 'mp4':
        print '视频格式不是mp4,无法下载'
        os._exit(0)
    video_type = response_data[key]['vtype']
    video_url = response_data[key]['main_url']
    video_url = base64.decodestring(video_url)

    if not os.path.exists(video_path):   #路径不存在时创建一个
        os.makedirs(video_path)
    md5_str = get_str_md5(url)

    filename = md5_str+"."+video_type
    target = video_path + filename
    if os.path.exists(target):
        return target

    urllib.urlretrieve(video_url, target, schedule)
    return target


if __name__ == '__main__':
    day_now = time.localtime()
    folder_name = '%d%02d' % (day_now.tm_year, day_now.tm_mon)+"/"

    data = get_download_data()

    if not data:
        print '暂时无下载数据'
        os._exit(0)

    for dd in data:
        id = str(dd[3])
        is_download = '1'
        update_download_status((is_download, id))
        video_url = download_video(dd[0], "./video/"+folder_name)
        img_url = download_img(dd[1], "./image/"+folder_name)
        is_download = '2'
        update_download_data(is_download, img_url,video_url, id)

    db.close()
    print "下载完成"

