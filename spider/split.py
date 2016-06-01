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

auth = oss2.Auth('dd', 'dd')
endpoint = 'oss-cn-hangzhou.aliyuncs.com'
bucket = oss2.Bucket(auth, endpoint, 'qifa-cerebra')


def get_download_data():
    sql = "select id, url,image from qnk_cerebra where is_download=2 and is_split=0"
    cursor.execute(sql)

    return cursor.fetchall()


def get_upload_data():
    sql = "select id, url,image from qnk_cerebra where is_download=2 and is_split=2 and is_upload_oss=0"
    cursor.execute(sql)

    return cursor.fetchall()


def update_split_status(is_split, id):
    sql = "update qnk_cerebra set is_split=%s where id=%s"
    cursor.execute(sql, (is_split, id))
    return db.commit()


def update_upload_status(is_upload_status,video_size,video_time, id):

    sql = "update qnk_cerebra set is_upload_oss=%s,video_size=%s,video_time=%s,is_published=1 where id=%s"
    cursor.execute(sql, (is_upload_status,video_size,video_time, id))
    return db.commit()


def split_video(url, video_path):
    filename = os.path.basename(url)
    filename = filename.split('.')[0]

    video_path += filename

    if not os.path.exists(video_path):  # 路径不存在时创建一个
        os.makedirs(video_path)

    if os.path.exists(video_path+"/video.m3u8"):
        print "该文件已经切过片"
        return False
    os.system("ffmpeg -y -i "+url+" -vcodec copy -acodec copy -vbsf h264_mp4toannexb  "+video_path+"/video.ts")
    os.system("ffmpeg -i "+video_path+"/video.ts -c copy -map 0 -f segment -segment_list "+video_path+"/video.m3u8 -segment_time 5 "+video_path+"/video-%04d.ts")
    os.system("rm -rf "+video_path+"/video.ts")

    return True


def upload_file(dir):
    all_file = os.listdir(dir)

    if not all_file:
        return False

    for file in all_file:
        filename = dir+'/'+file
        if os.path.isfile(filename):
            upload_file_oss_server(filename)

    return True


def upload_file_oss_server(filename):
    key = filename[2:]

    if not bucket.object_exists(key):
        print bucket.put_object_from_file(key, filename)

    return True


def get_path_size(str_path):
    if not os.path.exists(str_path):
        return 0;

    if os.path.isfile(str_path):
        return os.path.getsize(str_path);

    total_size = 0;
    for strRoot, lsDir, lsFiles in os.walk(str_path):
        # get child directory size
        for strDir in lsDir:
            total_size = total_size + get_path_size(os.path.join(strRoot, strDir));

            # for child file size
        for strFile in lsFiles:
            total_size = total_size + os.path.getsize(os.path.join(strRoot, strFile));

    return total_size;

if __name__ == '__main__':

    data = get_download_data()
    if not data:
        print '暂时无切片数据'

    #对文件进行切片
    for dd in data:
        folder_name = dd[1].split("/")[2]
        split_video(dd[1], './split_video/'+folder_name+"/")
        is_split = 2
        update_split_status(is_split, dd[0])

    oss_data = get_upload_data()
    #上传文件到oss
    for dd in oss_data:
        #上传图片文件到oss
        upload_file_oss_server(dd[2])
        #上传视频文件到oss
        folder = dd[1].split("/")
        dir = "./split_video/"+folder[2]+"/" +folder[3].split(".")[0]

        if upload_file(dir):
            is_upload_status = 2
            video_size = get_path_size(dir)
            video_time = os.popen("ffmpeg -i " + dd[1] + " 2>&1 | grep 'Duration' | cut -d ' ' -f 4 | sed s/,//").read()
            update_upload_status(is_upload_status,video_size,video_time.strip("\r\n"), dd[0])

    db.close()


