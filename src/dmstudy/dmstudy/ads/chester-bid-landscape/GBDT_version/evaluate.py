#!/usr/bin/env python
#coding:utf-8

import math,prediction

def sample_level_evaluation(samples_file_name,targeting_levels):
    '''
        return:(rmse_mean,rmse_var,rmsre_mean,rmsre_var)
    '''
    pred_result = []
    for line in open(samples_file_name):
        line = line.strip('\n')
        line_array=line.strip('\n').split('\t')
        sample = line_array[0:-3]
        count = int(line_array[-3])
        old_sum = float(line_array[-2])
        sq_sum = float(line_array[-1])
        (is_success,pred_mean,pred_var,plotxy)=prediction.sample_predict(sample,targeting_levels)
        if is_success == True:
            pred_result.append({})
            pred_result[-1]['count'] = count
            pred_result[-1]['mean'] = float(old_sum)/count
            pred_result[-1]['var'] = float(sq_sum)/count - pred_result[-1]['mean']**2
            #var = var if var > 10e-8 else 10e-8
            pred_result[-1]['pred_mean'] = pred_mean
            pred_result[-1]['pred_var'] = pred_var
            #print mean,var,pred_mean,pred_var
    total_count = sum([d['count'] for d in pred_result])
    rmse_mean = math.sqrt(sum([(float(d['count'])/total_count) * ((d['mean']-d['pred_mean'])**2) for d in pred_result]))
    rmse_var = math.sqrt(sum([(float(d['count'])/total_count) * ((d['var']-d['pred_var'])**2) for d in pred_result]))
    rmsre_mean = math.sqrt(sum([(float(d['count'])/total_count) * (((d['mean']-d['pred_mean'])/d['mean'])**2) for d in pred_result]))
    #第一种处理方法:
    #精度处理，这里处理是为了计算相对误差时出现零除异常
    #for idx in range(0,len(pred_result)):
    #    tmp_var = pred_result[idx]['var']
    #    pred_result[idx]['var'] = tmp_var if tmp_var > 10e-8 else 10e-8
    #这种精度处理，会使得相对误差极大,因为又好多sample都是单一赢价
    #第二种处理方法,直接删除0var值sample:
    idx=0
    while idx < len(pred_result):
        #if pred_result[idx]['var'] == 0: #或者小于某个精度
        if pred_result[idx]['var'] < 10e-4: #或者小于某个精度
            del pred_result[idx]
        else:
            idx += 1
    total_count = sum([d['count'] for d in pred_result])
    rmsre_var = math.sqrt(sum([(float(d['count'])/total_count) * (((d['var']-d['pred_var'])/d['var'])**2) for d in pred_result]))
    return (rmse_mean,rmse_var,rmsre_mean,rmsre_var)

def campaign_level_evaluation(campaign_file_name,bin_num):
    fields_name='event_price:'
    price_list = []
    line_num =0
    for line in open(campaign_file_name):
        if line_num % 1000 == 0:
            print line_num
        line_num += 1
        fields=line.split('|')
        for field in fields:
            if field.startswith(fields_name):
                price_list.append(float(field[len(fields_name):]))
    max_price = max(price_list)
    min_price = min(price_list)
    bin_size = (max_price - min_price)/bin_num
    price_bin = [0]*bin_num
    print max_price
    print min_price
    print bin_size
    for price in price_list:
        bin_idx = int(round((price-min_price) / bin_size))
        bin_idx = bin_idx if bin_idx != bin_num else bin_idx -1
        if bin_idx > bin_num:
            print price
            print bin_idx
        price_bin[bin_idx] += 1
    print price_bin
    for idx in range(0,bin_num):
        print min_price+ idx*bin_size,min_price+ (idx+1)*bin_size,price_bin[idx]
        
#(is_success,pred_mean,pred_var,plotxy)=prediction.sample_predict(['*','*','*'],targeting_levels)
#(is_success,plotxy)=prediction.campaign_predict([['xxx','SOMA'],'*','*'],targeting_levels)
#


if __name__ == '__main__':
    targeting_levels = [set(['mopub', 'web', 'admarvel', 'Nexage-SDK-iOS', '', 'SOMA', '*', 'BB2.1.0', 'dfp', 'pinger', 'burstly', 'IPH-LITE']), set(['3.1.3', '4.2.1', '3.1.1', '*', '6_0', '6_1', '', '3.1.2', '6.0', '5_0', '5_1_1', '6_1_3', '7.0', '6_1_1', '6_1_6', '6.1', '6_1_5', '3.2', '5_0_1', '2.1', '2.1.1', '7_1', '7_0', '4.0.1', '8.0', '4_3_4', '4_3_5', '4_3_2', '4_3_3', '4.3', '4_3_1', '6_0_2', '6_0_1', '4_2_10', '7_1_1', '5_1', '4.3.5', '5', '4_2_7', '4_2_6', '6_1_4', '4_1', '4_2_1', '4.2.6', '3_2', '8_0', '2.0.1', '3.2.2', '5.1', '3.0', '4.0.2', '3_1_3', '5.0', '4_3', '2.2.1', '4.1', '1.0', '4_0', '4.3.3', '4.0', '6_1_2', '2.0', '7_0_1', '7.0.4', '4.2', '5.1.1', '7.1.1', '7_1_2', '4.3.4', '7.1', '4.3.2', '3.2.1', '4.2.5', '4.3.1', '7_0_2', '7_0_3', '4.2.8', '7_0_6', '7_0_4', '7_0_5']), set(['300', '', '320', '*', '728'])]
    #print sample_level_evaluation('statistics29',targeting_levels)
    campaign_level_evaluation('/data/data_workspace/tongpeng/click.data29',30)
    pass
