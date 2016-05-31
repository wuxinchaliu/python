# -*- coding: utf-8 -*-
import urllib
import re
import time
import os
import md5
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

def downloadImg(html):
    reg = r'data-src="(.*?)">'
    imgre = re.compile(reg)
    md = md5.new()

    imglist = re.findall(imgre, html)
    #定义文件夹的名字
    t = time.localtime(time.time())
    foldername = str(t.__getattribute__("tm_year"))+"-"+str(t.__getattribute__("tm_mon"))+"-"+str(t.__getattribute__("tm_mday"))
    picpath = './%s' % (foldername) #下载到的本地目录
  
    if not os.path.exists(picpath):   #路径不存在时创建一个
        os.makedirs(picpath)   
    x = 0

    for imgurl in imglist:
        md.update(imgurl)
        kk = md.hexdigest()

        target = picpath+'/%s.jpg' % kk
        print 'Downloading image to location: ' + target + '\nurl=' + imgurl
        image = urllib.urlretrieve(imgurl, target, schedule)
        x += 1
    return image

  
if __name__ == '__main__':

    html = getHtml("http://toutiao.com/a6288819702621946113/#p=1")

    downloadImg(html)
    print "Download has finished."
