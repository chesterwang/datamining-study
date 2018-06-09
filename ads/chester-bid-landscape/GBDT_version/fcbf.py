#!/usr/bin/env python
#coding:utf-8

import os,sys

def fcbf(su,features_name,target_name,delta):
    '''
    su: symmetry uncertainty of combination fields
        format: {'feat1,feat2':,'feat2,feat3':,...}
    fields_name: features used for analysis
        format: ['feat1','feat2',...]
    target_name: target used for analysis
        format: 'target'
    delta: threshold
    结果:
    final_feat_candidate:
        {feature:su(feature,target),...}
    '''
    #features format: [feature,feature,...]
    feat_su_candidate={}
    if features_name.index(target_name) != -1:
        del features_name[features_name.index(target_name)]
    #feat_su_candidate={key:su[key] for key in su if su[key]>delta}
    for feat in features_name:
        if su[feat][target_name]>delta:
            feat_su_candidate[feat] = su[feat][target_name]
    feat_candidate=[(key,feat_su_candidate[key]) for key in sorted(feat_su_candidate.keys(), key=lambda x:feat_su_candidate[x], reverse=True)]
    i=0
    while i<len(feat_candidate):
        fp=feat_candidate[i][0]
        j=i+1
        while j<len(feat_candidate):
            fq=feat_candidate[j][0]
            if su[fp][fq]>=su[fq][target_name]:
                del feat_candidate[j]
            j=j+1
        i=i+1
    #候选feat索引
    #final_feat_candidate = [(features_name.index(f[0])+1,f[0],f[1]) for f in feat_candidate]
    #return final_feat_candidate
    return {k:v for (k,v) in feat_candidate}


if __name__ == "__main__":
    #delta
    features_name = 'req_device_osv,req_app_cat,req_device_model,req_device_geo_country,req_user_gender,req_imp_displaymanager,req_device_connectiontype,req_imp_banner_h,req_imp_banner_w,req_banner_pos,event_price'.split(',')
    target_name = 'event_price'
    delta=float(delta)
    the_feat_candidate=fcbf(su,features_name,target_name,delta)
    ##print ','.join(map(lambda x:str(x),fci))
    ##输出格式: device_carrier user_gender user_geo_city
    #print ','.join(map(lambda x:str(x),fci)) + ' ' +','.join(map(lambda x:x[0],fc))
    #输出格式: 1,device_carrier,su|3,user_gender,su
    print '|'.join([ ','.join([str(ff) for ff in f]) for f in the_feat_candidate ])


