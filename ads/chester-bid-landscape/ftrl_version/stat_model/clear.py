#!/usr/bin/env python
#coding:utf-8
'''把数据转成符合FTRL训练模型处理的格式，删掉不用的特征，数组扩展，得到mmh3在2^24方下的余数作为特征，加载app库和campaign库进行特征扩展
'''

import sys,cPickle,math,time,os,os.path,datetime,mmh3
import hashlib

reload(sys)
sys.setdefaultencoding('utf-8')


#舍弃的特征类：
#event类别特征
#rsp类别的特征
id_class={'tran_id':0,
    'req_id':0,
    'req_device_geo_latitude':0,
    'req_device_geo_longitude':0,
    'req_device_ip':0,
    'req_impressions_id':0,
    'req_ext_udi_idfa':0,
    'req_user_custom_data':0,
    'req_device_ext_nex_ifa':0,
    'req_device_geo_zip':0,
    'req_user_geo_zip':0,
    'req_user_ext_nex_hhi':0,
    'req_ext_x_uidh':0,
    'req_site_ref':0,
    'req_user_keywords':0,
    'req_device_dev_platform_id_sha1':0,
    'req_user_id':0,
    'req_ext_udi_udidmd5':0,
    'req_ext_udi_udidsha1':0,
    'req_ext_udi_openudid':0,
    'req_user_ext_nex_vzwuidh':0,
    'req_ext_udi_macmd5':0,
    'req_ext_udi_odin':0,
    'req_device_ext_nex_macsha1':0,
    'req_device_dev_platform_id_md5':0,
    'req_user_ext_nex_dma':0,
    'req_app_keywords':0,
    'req_user_geo_city':0,
    'req_device_geo_city':0,
    'rsp_id':0,
    'rsp_seatbid_bid_impid':0,
    'rsp_seatbid_bid_nurl':0,
    'rsp_seatbid_bid_adm':0,
    'rsp_seatbid_bid_price':0,
    'rsp_seatbid_bid_id':0,
    'rsp_bidid':0,
    'event_action_flag':0,
    'event_action_tr':0,
    'event_action_ts':0,
    'event_adx':0,
    #'event_ca':0,
    'event_ch':0,
    'event_click_flag':0,
    'event_click_tr':0,
    'event_click_ts':0,
    'event_co':0,
    'event_crv':0,
    'event_cur':0,
    'event_dev':0,
    'event_devt':0,
    'event_enct':0,
    #'event_grp':0,
    'event_impression_flag':0,
    'event_impression_ts':0,
    'event_ip':0,
    'event_price':0,
    'event_win_notice_ts':0}

def gethash(str):
    mmh3Value =  mmh3.hash(str, 3419)
    return mmh3Value % 16777216

appfea = {}
def loadappfea(appfeafile):
    appfile = open(appfeafile)
    for line in appfile:
        line = line.strip('\n')
        arr = line.split('\t')
        appfea[arr[0]] = arr[1:]

camfea = {}
def loadcamfea(camfeafile):
    camfile = open(camfeafile)
    for line in camfile:
        line = line.strip('\n')
        arr = line.split('\t')
        tempList = []
        camArr = arr[1:]
        for cam in camArr:
            tempList.append(gethash(cam))
        camfea[arr[0]] = tempList


def clear(orifilename, tfilename):
    orifile = open(orifilename)
    tfile = open(tfilename, 'w')
   
    elemArr = []
    for line in orifile:
        line = line.strip('\n')
        if 'event_impression_flag:0' in line:
            continue
        clk = 0
        enventCa = ''#记录campaign
        eventGrp = ''#记录广告组
        eventPrice = ''#记录成交价
        featList = []
        camfeatList = []
        arr = line.split('|')
        for elem in arr:
            if elem == ' Types of Mobile Phones':
                continue

            elemArr = elem.split(':')
            if len(elemArr) != 2:
                continue

            if len(elemArr[1]) == 0:
                continue

            if elemArr[0] == 'event_click_flag':
                clk = int(elemArr[1])
                continue

            if elemArr[0] == 'event_price':
                if 'req_adx:youku' in line:
                    eventPrice = str(float(elemArr[1]) / 6.1447)
                else:
                    eventPrice = elemArr[1]
                continue

            if elemArr[0] == 'event_ca':
                eventCa = elemArr[1]
                #continue

            if elemArr[0] == 'event_grp':
                eventGrp = elemArr[1]
                if elemArr[1] in camfea:
                    for cf in camfea[elemArr[1]]:
                        featList.append(cf)
                #continue

            if elemArr[0] in id_class:
                continue
            
            if elemArr[0] == 'req_app_bundle':
                featMD5 = hashlib.md5(elemArr[1]).hexdigest().upper()
                if featMD5 in appfea:
                    for af in appfea[featMD5]:
                        featList.append(af)

            try:
                if elemArr[1][0] == '[' and elemArr[1][-1] == ']':
                    arrStr = elemArr[1][1:-1]#去掉首尾的[]
                    if arrStr == '':
                        continue

                    strArr = arrStr.split(',')
                    for s in strArr:
                        s = s.strip()
                        if s[0] == 'u':
                            s = s[2:-1]
                        elif s[0] == '\'' and s[-1] == '\'':
                            s = s[1:-1]
   
                        featList.append(gethash(elemArr[0] + ':' + s))
                else:
                    featList.append(gethash(elem))
            except:
                print(elem)

        tfile.write(str(clk) + '\t' + eventCa + '\t' + eventGrp + '\t' + eventPrice)
        for x in range(len(featList)):
            tfile.write('\t' + str(featList[x]))
        tfile.write('\n')

    tfile.close()

if os.path.exists('/home/chester/KuaiPan/workspace/tukmob/resource/appfeat/appfeat'):
    loadappfea('/home/chester/KuaiPan/workspace/tukmob/resource/appfeat/appfeat')

base_dir = '/home/chester/KuaiPan/workspace/tukmob/resource/camfeat/'
filenames = os.listdir(base_dir)
maxstamp = 0.0
camfeatfilename = ''
if len(filenames) > 0:
    for fn in filenames:
        fn = fn.replace('camfeat', '')
        if float(fn) > maxstamp:
            maxstamp = float(fn)
            camfeatfilename = 'camfeat' + fn
    loadcamfea(base_dir + camfeatfilename)

stamp = str(time.time())
clear(sys.argv[1], sys.argv[2])
print 'Clear is OK!'
