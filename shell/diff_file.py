#!/usr/local/bin/python
# coding:utf-8
# 这个脚本是比较2个文件之间的差异,通过执行python diff_file.py text1.text text2.text > /data/www/diff.html
import difflib
import sys

try:
    textfile1 = sys.argv[1]
    textfile2 = sys.argv[2]
except Exception, e:
    print "Error:"+str(e)
    print "Usage: simple3.py filename1 filename2"
    sys.exit()

def readfile(filename):
    try:
        fileHandle = open(filename, "rb")
        text = fileHandle.read().splitlines()
        fileHandle.close()
        return text
    except IOError as error:
        print "open"+filename+"error"+str(error)
        sys.exit()

if textfile1=="" or textfile2=="":
    print "file is empty"
    sys.exit()

text1 = readfile(textfile1)
text2 = readfile(textfile2)

"""
在命令行中输出格式不是美观
d = difflib.Differ()
diff = d.compare(text1, text2)

print "\n".join(list(diff))"""

# 通过html方式现实
d = difflib.HtmlDiff()
print d.make_file(text1, text2)

