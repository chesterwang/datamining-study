# !/usr/bin/env python
# coding:utf-8
import math,hashlib,mmh3


class SampleDataProcessor():

    id_class=set(['tran_id', 'req_id','req_device_geo_latitude','req_device_geo_longitude',
            'req_device_ip','req_impressions_id','req_ext_udi_idfa',
            'req_user_custom_data','req_device_ext_nex_ifa','req_device_geo_zip',
            'req_user_geo_zip','req_user_ext_nex_hhi','req_ext_x_uidh',
            'req_site_ref','req_user_keywords','req_device_dev_platform_id_sha1',
            'req_user_id','req_ext_udi_udidmd5','req_ext_udi_udidsha1',
            'req_ext_udi_openudid','req_user_ext_nex_vzwuidh','req_ext_udi_macmd5',
            'req_ext_udi_odin','req_device_ext_nex_macsha1','req_device_dev_platform_id_md5',
            'req_user_cookie_age_seconds','req_device_hashed_idfa',
            'req_app_content_detected_vertical_weight',
            'req_user_ext_nex_dma','req_app_keywords','req_user_geo_city',
            'req_request_time','req_device_dev_platform_id','req_user_cookie_age_seconds'
            'req_device_geo_city','rsp_id','rsp_seatbid_bid_impid',
            'rsp_seatbid_bid_nurl','rsp_seatbid_bid_adm','rsp_seatbid_bid_price',
            'rsp_seatbid_bid_id','rsp_bidid','event_action_flag',
            'event_action_tr','event_action_ts','event_adx',
            #'event_ca','event_ch','event_click_flag','event_click_tr','event_click_ts','event_co',
            'event_crv','event_cur','event_dev','event_devt','event_enct',#'event_grp',
            'event_impression_flag','event_impression_ts','event_ip',
            'event_price','event_win_notice_ts'])
    def gethash(self,str):
        mmh3Value =  mmh3.hash(str, 3419)
        return mmh3Value % 16777216
    def clear(self,line):
        """去除不需要的特征和不符合格式的数据
            返回处理后的特征值列表
        """
        if 'event_impression_flag:0' in line:
            return
        clk = 0
        enventCa = ''#记录campaign
        eventGrp = ''#记录广告组
        win_price = ''#记录成交价
        hashed_feat_vals = {}
        line_arr = line.strip('\n').split('|')
        for elem in line_arr:
            if ":" not in elem:
                continue
            elemArr = elem.split(':',1)
            if elemArr[1] == '':
                continue
            if elemArr[0] == 'event_click_flag':
                clk = int(elemArr[1])
                continue

            if elemArr[0] == 'event_price':
                win_price = float(elemArr[1])

            if elemArr[0] == 'event_ca':
                eventCa = elemArr[1]
            if elemArr[0] == 'event_grp':
                eventGrp = elemArr[1]

            #hash处理
            if elemArr[0] in self.id_class:
                continue
            if '[' in elemArr[1] or ']' in elemArr[1]:
                feat_vals_list = elemArr[1].strip('[').strip(']').split(',')
                hashed_feat_vals.update( {self.gethash(elemArr[0] + ':' + feat_val):elemArr[0] + ':' + feat_val for feat_val in  feat_vals_list} )
            else:
                hashed_feat_vals[self.gethash(elem)] = elem
        return win_price,hashed_feat_vals

    def get_extended_feat(self):
        pass
        #if elemArr[1] in camfea:
        #    for cf in camfea[elemArr[1]]:
        #        featList.append(cf)

        #if elemArr[0] == 'event_price':
        #    if 'req_adx:youku' in line_arr:
        #        eventPrice = str(float(elemArr[1]) / 6.1447)
        #    else:
        #        eventPrice = elemArr[1]
        #    continue

        #if elemArr[0] == 'req_app_bundle':
        #    featMD5 = hashlib.md5(elemArr[1]).hexdigest().upper()
        #    if featMD5 in appfea:
        #        for af in appfea[featMD5]:
        #            featList.append(af)


class LrCtrModel():
    '''
    logistic regression CTR model
    这里仅仅有模型加载和模型预测功能。
    '''
    def __init__(self, fwfile_name, new_old):
        '''
        fwfile_name 为特征权重文件
        new_old表示是新模型还是旧模型,值为new 或者old
        新模型是mmh3算法,
        就模型是简单的hash算法
        '''
        self.new_old = new_old
        if new_old != "old":
            self.feat_num = 2 ** 24
            self.featWeight = [0] * (self.feat_num)
            for featline in open(fwfile_name):
                featArr = featline.rstrip('\n').split('\t')
                self.featWeight[int(featArr[0])] = float(featArr[1])
        else:
            self.featWeight = {}
            for featline in open(fwfile_name):
                featArr = featline.rstrip('\n').split('\t')
                self.featWeight[featArr[0]] = float(featArr[1])
        self.sampleDataProcessor = SampleDataProcessor()
    
    def get_weight(self,hashed_feat_value):
        '''
        根据一个特征值来计算对应权重，先经过hash处理，再查询权重。
        feat_value为字符串,形式为feat_name:feat_value
        例如: width:300
        '''
        if self.new_old != "old":
            return self.featWeight[hashed_feat_value] if hashed_feat_value < self.feat_num and hashed_feat_value >= 0 else 0
        else:
            return self.featWeight.get(hashed_feat_value,0)


    def predict_ctr(self, line):
        '''
        '''
        win_price, hashed_feat_vals = self.sampleDataProcessor.clear(line)
        if self.featWeight == []:
            return None
        weighted_sum = reduce(lambda a, b:a + b, [self.get_weight(elem) for elem in hashed_feat_vals])
        return 1 / (1 + math.exp(-weighted_sum))  # sigmoid

def ctr_model_4_anytime(incremental_model_dir,timestamp):
    '''
    未完成
    对任何一个时间点，恢复模型
    '''
    import os
    model_files=os.listdir(incremental_model_dir)
    model_files = [incremental_model_dir +'/'+ model_file for model_file in model_files]
    #=[model_file for model_file in model_files if os.path.getmtime(model_file)]
    sorted_model_files = sorted(model_files,key=lambda x:os.path.getmtime(x))
    filtered_sorted_model_files = [ model_file for model_file in sorted_model_files if os.path.getmtime(model_file) < timestamp ]
    #print filtered_sorted_model_files

    featWeight = {}
    feat_num = 2 ** 24
    featWeight = [0] * (feat_num)

    for model_file in filtered_sorted_model_files:
        with open(model_file) as file_handle:
            for featline in file_handle:
                featArr = featline.rstrip('\n').split('\t')
                featWeight[int(featArr[0])] = float(featArr[1])
    return featWeight


    

