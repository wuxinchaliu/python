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

reload(sys)
sys.setdefaultencoding('utf-8')
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

def downloadImg(html):
    return_data = []
    soup = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
    summary_node = soup.find(name="div", attrs={"class": "article-content"})

    if summary_node is None:
        print "抓取不到数据,或您输入地址有误"
        os._exit(0)

    summary_title = soup.find(name='h1', attrs={"class":"title"}).getText()
    summary_tag = soup.find(name='ul', attrs={"class":"tag-list"}).findAll('a')

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
    foldername = str(t.__getattribute__("tm_year"))+"-"+str(t.__getattribute__("tm_mon"))+"-"+str(t.__getattribute__("tm_mday"))
    picpath = '/data/www/study/%s' % (foldername) #下载到的本地目录

    if not os.path.exists(picpath):   #路径不存在时创建一个
        os.makedirs(picpath)

    md = hashlib.md5()

    summary_url = {}
    for (key,imgurl) in imglist.items():
        md5_str = md.update(imgurl)
        md5_str = md.hexdigest()
        target = picpath+'/%s.jpg' % md5_str
        orgin_url  = "http://localhost/"+foldername+'/'+md5_str+'.jpg'
        summary_url[imgurl] = foldername+'/'+md5_str+'.jpg'

        summary_node = str(summary_node).replace(imgurl, orgin_url)
        summary_node = summary_node.replace('onerror="javascript:errorimg.call(this);"', '')

        print 'Downloading image to location: ' + target + '\nurl=' + imgurl
        image = urllib.urlretrieve(imgurl, target, schedule)

    return_data = [summary_node,summary_title,summary_tag,json.dumps(summary_url),int(time.time())]
    output_html(summary_title, summary_node)

    return return_data

def insert_data(data):
    db = MySQLdb.connect("localhost","root", "root@123", "test")
    cursor = db.cursor()
    sql = "insert into spider (`content`,`title`,`tag`,`img_url`,`create_time`,`url`,`source`) " \
          "values (%s,%s,%s,%s,%s,%s,%s)"

    cursor.executemany(sql, [data])
    return db.commit()

def get_domain(url):
    proto, rest = urllib.splittype(url)
    res, rest = urllib.splithost(rest)
    return res

if __name__ == '__main__':
    url = "http://toutiao.com/a6290460409251053825/"
    html = getHtml(url)

    return_data = downloadImg(html)

    return_data.append(url)
    return_data.append(get_domain(url))

    print insert_data(tuple(return_data))

    print "Download has finished."


