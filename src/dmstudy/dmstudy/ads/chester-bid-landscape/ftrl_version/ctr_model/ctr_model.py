# !/usr/bin/env python
# coding:utf-8
import math,hashlib,mmh3

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
    
    def get_weight(self,feat_value):
        '''
        根据一个特征值来计算对应权重，先经过hash处理，再查询权重。
        feat_value为字符串,形式为feat_name:feat_value
        例如: width:300
        '''
        if self.new_old != "old":
            hash_value = mmh3.hash(feat_value, 3419) % self.feat_num
            return self.featWeight[hash_value] if hash_value < self.feat_num and hash_value >= 0 else 0
        else:
            hash_value = hashlib.md5(feat_value).hexdigest().upper()
            return self.featWeight.get(hash_value,0)

    def predict_ctr(self, feat_value_list):
        '''
        feat_value_list:为原始特征值的列表
        feat_value_list: ["width:300","height:400"]
        '''
        if self.featWeight == []:
            return None
        weighted_sum = reduce(lambda a, b:a + b, [self.get_weight(elem) for elem in feat_value_list])
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


    

