#!/usr/bin/env python


import sys


for file_name in ['click.data27','click.data28','click.data29']:
    src_log='/data/data_workspace/tongpeng/' + file_name
    fields_name='req_device_osv,req_app_cat,req_device_model,req_device_geo_country,req_user_gender,req_imp_displaymanager,req_device_connectiontype,req_imp_banner_h,req_imp_banner_w,req_banner_pos,event_price'
    #feats=sys.argv[1].split(',')
    feats = fields_name.split(',')
    output_log = '/data/data_workspace/tongpeng/feat_table_' + file_name
    
    #for line in sys.stdin:
    out_f=open(output_log,'w')
    for line in open(src_log):
        fields=line.split('|')
        fields_dict = {}
        for field in fields:
            idx=field.find(':')
            if idx == -1:
                break
            if field[0:idx] in feats:
                fields_dict[field[0:idx]] = field[idx+1:]
        out_f.write('\t'.join([fields_dict[feat] if fields_dict.has_key(feat) else ''  for feat in feats])+'\n')
    out_f.close()
