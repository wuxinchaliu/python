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
import random
import urlparse

reload(sys)
sys.setdefaultencoding('utf-8')

db = MySQLdb.connect("localhost","root", "root@123", "wer")
cursor = db.cursor()
db.set_character_set('utf8')
cursor.execute('SET NAMES utf8;')
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')

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

def output_html(title, content):
    fout = open("/data/www/study/output.html", "w")
    fout.write("<html><head><meta charset='UTF-8'><title>%s</title></head><body>" % title)
    fout.write("<h1>%s</h1>" % title)
    fout.write("%s" % content)
    fout.write("</body></html>")

def download_toutiao(url,picpath):
    html = getHtml(url)
    return_data = []
    soup = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
    summary_node = soup.find(name="div", attrs={"class": "article-content"})

    if summary_node is None:
        print "抓取不到数据,或您输入地址有误"
        os._exit(0)

    summary_title = soup.find(name='h2', attrs={"id":"arttitle"}).getText()
    print summary_node
    print summary_title
    os._exit(0)
    summary_tag = soup.find(name='ul', attrs={"class":"tag-list"}).findAll('a')

    description = soup.find(name="meta", attrs={"name":"description"}).attrs["content"]

    tag_list = []
    for tag in summary_tag:
         tag_list.append(tag.getText())

    summary_tag = ",".join(tag_list)

    data = summary_node.findAll('img')
    imglist = {}
    for img in data:
        imglist[data.index(img)] = img.attrs['src']


    #定义文件夹的名字
    t = time.localtime(time.time())
    foldername = "/uploads/"+str(t.__getattribute__("tm_year"))+str(t.__getattribute__("tm_mon"))+str(t.__getattribute__("tm_mday"))
    picpath = picpath+'%s' % (foldername) #下载到的本地目录

    if not os.path.exists(picpath):   #路径不存在时创建一个
        os.makedirs(picpath)

    md = hashlib.md5()

    summary_url = {}
    upload_list = []
    for (key,imgurl) in imglist.items():
        md5_str = md.update(imgurl)
        md5_str = md.hexdigest()
        target = picpath+'/%s.jpg' % md5_str
        orgin_url  = foldername+'/'+md5_str+'.jpg'
        upload_list.append(orgin_url)

        summary_url[imgurl] = foldername+'/'+md5_str+'.jpg'

        summary_node = str(summary_node).replace(imgurl, orgin_url)
        summary_node = summary_node.replace('onerror="javascript:errorimg.call(this);"', '')
        summary_node = summary_node.replace('<div class="article-content">','')
        summary_node = summary_node.replace('<div>','')
        summary_node = summary_node.replace('</div>','')

        print 'Downloading image to location: ' + target + '\nurl=' + imgurl
        if not os.path.exists(target):
            urllib.urlretrieve(imgurl, target, schedule)

    return_data = [summary_node,summary_title,summary_tag,json.dumps(summary_url),int(time.time())]

    return_disc = {
        "title":summary_title,
        "thumb_image": '',
        "keywords":summary_tag,
        "description":description,
        "type_id":"45",
        "body":summary_node,
        "upload_list":upload_list
    }

    return return_disc

def download_kuaibao(url,picpath):
    results = urlparse.urlparse(url)
    params = urlparse.parse_qs(results.query, True)
    id = params['id'][0]
    time_now = time.time()
    time_now = int(time_now*1000)
    str2 = "http://openapi.kuaibao.qq.com/getSubNewsContent?" \
       "callback=responseData&appver=8.4_qnreading_1.0.0&" \
       "screen_width=320&screen_height=568&devid=D5126D83-6E2F-4C7F-8BEF-3D81E34C4387&" \
       "device_model=iPhone&screen_scale=2&id="+id+ \
       "&alg_version=0&chlid=news_news_dailyhot&media_id=2240" \
       "&seq_no=&isShowTitle=1&_="+str(time_now)

    html = getHtml(str2).replace("responseData(","").replace(")","")

    html = json.loads(html)
    title = html['content']['titleName']
    content = html['content']['text']
    strinfo = re.compile('id="(.*?)"')
    content = strinfo.sub('',content)

    image_list = html['attribute']
    len_disc = len(image_list)

    #定义文件夹的名字
    t = time.localtime(time.time())
    foldername = "/uploads/"+str(t.__getattribute__("tm_year"))+str(t.__getattribute__("tm_mon"))+str(t.__getattribute__("tm_mday"))
    picpath = picpath+'%s' % (foldername) #下载到的本地目录

    if not os.path.exists(picpath):   #路径不存在时创建一个
        os.makedirs(picpath)

    md = hashlib.md5()
    summary_url = {}
    upload_list = []

    for img in image_list:
        md5_str = md.update(image_list[img]['url'])
        md5_str = md.hexdigest()
        target = picpath+'/%s.jpg' % md5_str
        origin_url = foldername+'/'+md5_str+'.jpg'
        upload_list.append(origin_url)

        old = "<!--"+img+"-->";
        if image_list[img]['desc']:
            alt = image_list[img]['desc']
        else:
            alt = title
        new = "<img src='"+origin_url+"' alt='"+alt+"' />"
        content = content.replace(old, new)

        #print 'Downloading image to location: ' + target + '\nurl=' + image_list[img]['url']
        if not os.path.exists(target):
            urllib.urlretrieve(image_list[img]['url'], target, schedule)

    return_disc = {
        "title":title,
        "thumb_image": '',
        "keywords":"",
        "description":'',
        "type_id":"45",
        "body":content,
        "upload_list":upload_list
    }

    return return_disc

def get_max_id():

    sql = "select max(id) as id  from zyh_archives"
    cursor.execute(sql)
    return cursor.fetchone()


def insert_article_server(return_data):
    title = return_data['title']
    thumb_image = return_data['thumb_image']
    keywords = return_data['keywords']
    description = return_data['description']
    type_id = return_data['type_id']
    body = return_data['body']
    upload_list = return_data['upload_list']

    last_id = get_max_id()

    if not last_id[0]:
        last_id = 1
    else:
        last_id = int(last_id[0])+1

    sql_main = "INSERT INTO `zyh_archives` (`id`,`typeid`, `flag`, `channel`, `click`,  `title`,  " \
          "`writer`, `source`, `litpic`, `pubdate`, `senddate`, `mid`, `keywords`,  `description`,`voteid`)\
          VALUES(%s,%s, %s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s)"
    rand_num = random.randint(200,1000)
    create_time = int(time.time())
    main_table = (last_id,type_id,  'c,p',  1, rand_num,title, '小蜻蜓', '网络', thumb_image, create_time,create_time, 1, keywords, description,0)

    cursor.execute(sql_main,main_table)


    sql_tiny = "INSERT INTO `zyh_arctiny` (`id`,`typeid`, `channel`,`senddate`,`sortrank`,`mid`)\
                VALUES (%s,%s,%s,%s,%s,%s)"
    tiny_table = (last_id,type_id, '1',create_time,create_time,'1')

    cursor.execute(sql_tiny,tiny_table)

    sql_body = "INSERT INTO `zyh_addonarticle` (`aid`,`typeid`, `body`)\
                VALUES (%s,%s,%s)"
    body_table = (last_id,type_id, body)

    cursor.execute(sql_body,body_table)

    pic_sql = "INSERT INTO `zyh_uploads` ( `arcid`, `title`, `url`, `mediatype`, \
                `uptime`, `mid`) VALUES (%s,%s,%s,%s,%s,%s)"
    pic_list = []
    for pic in upload_list:
        pic_table = (last_id,title, pic, 1,1464951214, 1)
        pic_list.append(pic_table)

    cursor.executemany(pic_sql, pic_list)

    return db.commit()


def get_domain(url):
    proto, rest = urllib.splittype(url)
    res, rest = urllib.splithost(rest)
    return res


def update_status(id):

    sql = "update zyh_scrapy_html set status=%s where id=%s"
    cursor.execute(sql,(1,id))
    return db.commit()

def get_spider_data():
    sql = "select id,source,source_type from zyh_scrapy_html where status=0"

    cursor.execute(sql)
    return cursor.fetchall()


if __name__ == '__main__':

    data = get_spider_data()
    if data:
        for dd in data:
            url = dd[1]
            pic_path = "/alidata/www/qwer"
            if "toutiao" in dd[2]:
                return_data = download_toutiao(url, pic_path)
            elif "qq" in dd[2]:
                return_data = download_kuaibao(url, pic_path)
            insert_article_server(return_data)
            update_status(dd[0])
            print "download finish:"+url

    print "Download has finished all."
