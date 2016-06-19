# -*- coding: utf-8 -*-
import time
import os
import sys
import MySQLdb
import oss2
reload(sys)
sys.setdefaultencoding('utf-8')

db = MySQLdb.connect("192.168.1.161", "qiaonaoke", "qiaonaoke_psw", "qiaonaoke")
cursor = db.cursor()


def get_download_data():

    sql = "select id, url,image from qnk_cerebra where video_size=0"
    cursor.execute(sql)

    return cursor.fetchall()


def update_upload_status(video_size,video_time, id):

    sql = "update qnk_cerebra set video_size=%s,video_time=%s where id=%s"
    cursor.execute(sql, (video_size,video_time, id))
    return db.commit()


def get_path_size(str_path):
    if not os.path.exists(str_path):
        return 0

    if os.path.isfile(str_path):
        return os.path.getsize(str_path)

    total_size = 0
    for strRoot, lsDir, lsFiles in os.walk(str_path):
        # get child directory size
        for strDir in lsDir:
            total_size = total_size + get_path_size(os.path.join(strRoot, strDir))

            # for child file size
        for strFile in lsFiles:
            total_size = total_size + os.path.getsize(os.path.join(strRoot, strFile))

    return total_size

if __name__ == '__main__':

    data = get_download_data()
    if not data:
        print '暂时无切片数据'

    #上传文件到oss
    for dd in data:

        #上传视频文件到oss
        folder = dd[1].split("/")
        dir = "./split_video/"+folder[2]+"/" +folder[3].split(".")[0]

        video_size = get_path_size(dir)
        video_time = os.popen("ffmpeg -i " + dd[1] + " 2>&1 | grep 'Duration' | cut -d ' ' -f 4 | sed s/,//").read()
        update_upload_status(video_size,video_time.strip("\r\n"), dd[0])

    db.close()


