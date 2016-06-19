#!/usr/local/bin/python
# coding:utf-8
# 这是一个探测web服务质量,测试web服务性能脚本
import os,sys,time,pycurl

URL = "http://www.baidu.com" #探测目标地址

c = pycurl.Curl() #创建Curl 对象
c.setopt(pycurl.URL, URL) #定义请求的url常量
c.setopt(pycurl.CONNECTTIMEOUT, 5) #请求连接等待时间
c.setopt(pycurl.TIMEOUT, 5) #请求超时时间
c.setopt(pycurl.NOPROGRESS, 1) #屏蔽下载进度条
#完成交互后强制断开连接,不重用
c.setopt(pycurl.FORBID_REUSE, 1)
#指定http重定向的数为1
c.setopt(pycurl.MAXREDIRS, 1)

#设置保存dns信息的时间为30s
c.setopt(pycurl.DNS_CACHE_TIMEOUT, 30)

#创建文件对象,以"wb"方式打开,用来存储返回的http头部及页面内容
indexfile = open(os.path.dirname(os.path.realpath(__file__))+"/content.txt", 'wb')
#返回的HTTP HEADER 定向到indexfile文件
c.setopt(pycurl.WRITEHEADER, indexfile)
#返回的HTML内容定向到indexfile文件对象
c.setopt(pycurl.WRITEDATA, indexfile)

try:
    c.perform()   #提交请求
except Exception,e:
    print "connection error:"+str(e)
    indexfile.close()
    c.close()
    sys.exit()

NAMELOOKUP_TIME = c.getinfo(c.NAMELOOKUP_TIME) #获取dns解析时间
CONNECT_TIME = c.getinfo(c.CONNECT_TIME)  #获取建立连接时间
PRETRANSFER_TIME = c.getinfo(c.PRETRANSFER_TIME) #获取从建立连接到准备传输所消耗的时间
STARTTRANSFER_TIME = c.getinfo(c.STARTTRANSFER_TIME) #获取从建立连接到传输开始消耗的时间
TOTAL_TIME = c.getinfo(c.TOTAL_TIME) #获取传输的总时间
HTTP_CODE = c.getinfo(c.HTTP_CODE) #获取http状态码
SIZE_DOWNLOAD = c.getinfo(c.SIZE_DOWNLOAD) #获取下载数据包大小
HEADER_SIZE = c.getinfo(c.HEADER_SIZE) # 获取http头大小
SPEED_DOWNLOAD = c.getinfo(c.SPEED_DOWNLOAD) # 获取平均下载速度
#打印输出相关数据

print "HTTP状态码:%s" % (HTTP_CODE)
print "DNS解析时间:%.2f ms" % (NAMELOOKUP_TIME*1000)
print "建立连接时间:%.2f ms" % (CONNECT_TIME * 1000)
print "准备传输时间:%.2f ms" % (PRETRANSFER_TIME * 1000)
print "传输开始时间:%.2f ms" % (STARTTRANSFER_TIME * 1000)
print "传输结束总时间:%.2f ms" % (TOTAL_TIME * 1000)
print "下载数据包大小:%d bytes/s" % (SIZE_DOWNLOAD)
print "HTTP头部大小:%d bytes/s" % (HEADER_SIZE)
print "平均下载速度:%d bytes/s" % (SPEED_DOWNLOAD)
# 关闭文件及Curl 对象
indexfile.close()
c.close()

