# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib
import re
import time
import os
import hashlib
import sys

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

    soup = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
    summary_node = soup.find(name="div", attrs={"class": "article-content"})
    summary_title = soup.find(name='h1', attrs={"class":"title"}).getText()

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

    for (key,imgurl) in imglist.items():
        md5_str = md.update(imgurl)
        md5_str = md.hexdigest()
        target = picpath+'/%s.jpg' % md5_str
        orgin_url  = "http://localhost/"+foldername+'/'+md5_str+'.jpg'


        summary_node = str(summary_node).replace(imgurl, orgin_url)
        summary_node = summary_node.replace('onerror="javascript:errorimg.call(this);"', '')

        print 'Downloading image to location: ' + target + '\nurl=' + imgurl
        image = urllib.urlretrieve(imgurl, target, schedule)

    output_html(summary_title, summary_node)
    return image

  
if __name__ == '__main__':

    html = getHtml("http://toutiao.com/a6285980631693459714/")

    downloadImg(html)
    print "Download has finished."


