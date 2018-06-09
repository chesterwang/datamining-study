#!/usr/bin/env python
#coding:utf8

import compute_entropy
import fcbf
import statistic
import StarTree
import TemplateSelection
import data_for_GBDT
import GBDT
import prediction 
#import joinlog2features_table

common_dir = "/data/data_workspace/tongpeng/bid_landscape"
#--------------------t1 t2 t3 join2table
#joinlog2features_table
#--------------------t1 join2table and feature selection
#data for feature selection and star tree
file_name_1 = common_dir + '/' + 'feat_table_click.data27'
#data for template selection and GBDT
file_name_2 = common_dir + '/' + 'feat_table_click.data28'
#data for test
file_name_3 = common_dir + '/' + 'feat_table_click.data29'


fields_name = 'req_device_osv,req_app_cat,req_device_model,req_device_geo_country,req_user_gender,req_imp_displaymanager,req_device_connectiontype,req_imp_banner_h,req_imp_banner_w,req_banner_pos,event_price'.split(',')
target_name = 'event_price'
delta = 0.001
su=compute_entropy.compute_su_from_table(fields_name,target_name,file_name_1)
selected_feat=fcbf.fcbf(su,fields_name,target_name,delta)
print selected_feat

# sort selected_feat and take index
selected_feat ={'req_imp_banner_w': 0.01786039850491193, 'req_imp_displaymanager': 0.28087397698755634, 'req_device_osv': 0.21152790389375328}
ordered_selected_feat = sorted(selected_feat.keys(),key=lambda x:selected_feat[x],reverse=True)
fields_name = 'req_device_osv,req_app_cat,req_device_model,req_device_geo_country,req_user_gender,req_imp_displaymanager,req_device_connectiontype,req_imp_banner_h,req_imp_banner_w,req_banner_pos,event_price'.split(',')
selected_feat_idx = []
for feat in ordered_selected_feat:
    selected_feat_idx.append(fields_name.index(feat))
selected_feat_idx.append(fields_name.index('event_price'))

#------------------------impression -> samples (statistics)
#file_name = '/data/data_workspace/tongpeng/feat_table_click.data27'
targeting_levels_1 = statistic.extract(file_name_1,selected_feat_idx[0:-1],file_name_1+'statistics')
StarTree.build(file_name_1+'statistics',ordered_selected_feat,10,file_name_1+'expand_samples')

#file_name = '/data/data_workspace/tongpeng/feat_table_click.data28'
targeting_levels_2 = statistic.extract(file_name_2,selected_feat_idx[0:-1],file_name_2+'statistics')
StarTree.build(file_name_2+'statistics',ordered_selected_feat,10,file_name_2+'expand_samples')

#file_name = '/data/data_workspace/tongpeng/feat_table_click.data29'
targeting_levels_3 = statistic.extract(file_name_3,selected_feat_idx[0:-1],file_name_3+'statistics')

for idx in range(0,len(targeting_levels_1)):
    targeting_levels_1[idx].union(targeting_levels_2[idx])
    targeting_levels_1[idx].union(targeting_levels_3[idx])
targeting_levels=targeting_levels_1

TemplateSelection.template_select(file_name_2+'expand_samples',file_name_1+'statistics_StarTree.pickle',ordered_selected_feat,selected_feat,10,file_name_2 + '_template_list.pickle',common_dir + '/TemplateSelection.log')
#
data_for_GBDT.generate(file_name_1+'statistics_StarTree.pickle',file_name_2 + '_template_list.pickle',file_name_2+'expand_samples','mean',2,10e-5,file_name_2 + 'GBDT_train_data_mean')
data_for_GBDT.generate(file_name_1+'statistics_StarTree.pickle',file_name_2 + '_template_list.pickle',file_name_2+'expand_samples','var',2,10e-5,file_name_2 + 'GBDT_train_data_var')
GBDT.GBDT(file_name_2 + 'GBDT_train_data_mean',[1,1,1,0],10,0.001,4,'mean',common_dir + '/GBDT_mean.pickle',common_dir + '/GBDT_mean.log')
GBDT.GBDT(file_name_2 + 'GBDT_train_data_var',[1,1,1,0],10,0.001,4,'var',common_dir + '/GBDT_var.pickle',common_dir + '/GBDT_var.log')
#


print targeting_levels
for idx in range(0,len(targeting_levels)):
    targeting_levels[idx].add('*')
#--- test in t3
(is_success,pred_mean,pred_var,plotxy)=prediction.sample_predict(['*','*','*'],targeting_levels,file_name_1+'statistics_StarTree.pickle',file_name_2 + '_template_list.pickle',common_dir + '/GBDT_mean.pickle',common_dir + '/GBDT_var.pickle')
(is_success,plotxy)=prediction.campaign_predict([['xxx','SOMA'],'*','*'],targeting_levels,file_name_1+'statistics_StarTree.pickle',file_name_2 + '_template_list.pickle',common_dir + '/GBDT_mean.pickle',common_dir + '/GBDT_var.pickle')

print targeting_levels


#----------------test---------------
mean_sq_error=0
var_sq_error =0
total_count =0
r_mean_sq_error=0#relative
r_var_sq_error =0#relative
for line in open(file_name_3 + 'statistics'):
    line_array=line.split('\t')
    sample = line_array[0:-3]
    count = int(line_array[-3])
    old_sum = float(line_array[-2])
    sq_sum = float(line_array[-1])
    (is_success,pred_mean,pred_var,plotxy)=prediction.sample_predict(sample,targeting_levels,file_name_1+'statistics_StarTree.pickle',file_name_2 + '_template_list.pickle',common_dir + '/GBDT_mean.pickle',common_dir + '/GBDT_var.pickle')
    if is_success == True:
        mean = float(old_sum)/count
        var = float(sq_sum)/count - mean**2
        #var = var if var > 10e-5 else 10e-5
        #print mean,var,pred_mean,pred_var,'---'
        print count,pred_mean-mean,pred_var-var,sample
        mean_sq_error += count*((pred_mean - mean)**2)
        var_sq_error += count*((pred_var - var)**2)
        r_mean_sq_error += count*(((pred_mean - mean)/mean)**2)
        if var >= 10e-4:
            r_var_sq_error += count*(((pred_var - var)/var)**2)
        total_count += count
mean_sq_error = mean_sq_error/total_count
var_sq_error = var_sq_error/total_count
r_mean_sq_error = r_mean_sq_error/total_count
r_var_sq_error = r_var_sq_error/total_count
print 'error',mean_sq_error,var_sq_error
print 'relative error',r_mean_sq_error,r_var_sq_error

print '--------------'

#(is_success,pred_mean,pred_var,plotxy)=prediction.sample_predict(['web', '7_0_4', '320'],targeting_levels)




