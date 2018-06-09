#!/usr/bin/env python
#coding:utf8


import sys,pickle

def get_comb_value(input_file, feats):
    '''
    get occurency num stats and bidfloor stats from input_file for combinated feature value
    from specified feature list(feats).
    :param input_file:
    :param feats:specified feats
    :return:
    '''

    comb_value_stats = {}
    comb_value_bidfloor = {}
    line_num = 0
    exception_num = 0
    for input_file in input_files:
        for line in input_file:
            line = line.strip('\n')
            if line == '':
                continue
            if line_num % 10000 == 0:
                print line_num,len(comb_value_stats)
            line_num += 1
            line_array=line.split('|')
            feat_values = dict.fromkeys(feats)
            bidfloor = None
            exception_flag = 0
            for key_val in line_array:
                kv_array = key_val.split(':')
                if len(kv_array) < 2:
                    continue
                key = key_val.split(':')[0]
                val = key_val.split(':')[1]
                if key in feats:
                    feat_values[key] = val
                if key == 'req_impressions_bid_floor':
                    bidfloor = float(val)
            comb_value = tuple([feat_values[feat] for feat in feats])
            if comb_value not in comb_value_stats:
                comb_value_stats[comb_value] = 0
            comb_value_stats[comb_value] += 1
            if comb_value not in comb_value_bidfloor:
                comb_value_bidfloor[comb_value] = {}
            if len(comb_value_bidfloor[comb_value].keys()) < 50:
                if bidfloor != None:
                    if bidfloor not in comb_value_bidfloor[comb_value]:
                        comb_value_bidfloor[comb_value][bidfloor] = 0
                    comb_value_bidfloor[comb_value][bidfloor] += 1
    return (comb_value_stats,comb_value_bidfloor)

def get_ratio(file_name):
    traffic_stats,bidfloor_stats = pickle.load(open(file_name,'r'))
    total_line = sum(traffic_stats.values())
    for key in traffic_stats:
        ratio = float(traffic_stats[key])/total_line
        if ratio > 0.0001:
            print key,float(traffic_stats[key])/total_line
            total_bid=sum(bidfloor_stats[key].values())
            print 'bid ratio',float(total_bid)/traffic_stats[key]
            for bid in bidfloor_stats[key]:
                bid_ratio = float(bidfloor_stats[key][bid])/total_bid
                if bid_ratio > 0.1:
                    print bid,bid_ratio,','
            print ''

def rollup(file_name):
    traffic_stats,bidfloor_stats = pickle.load(open(file_name,'r'))

    total_line = sum(traffic_stats.values())
    if traffic_stats == None:
        return None
    for feat_idx in range(0,len(traffic_stats.keys()[0])):
        tmp_star_dict = {}
        star_comb_feat = ()
        for comb_feat in traffic_stats.keys():
            star_comb_feat = comb_feat[0:feat_idx] + ('*',) + comb_feat[feat_idx+1:]
            if not traffic_stats.has_key(star_comb_feat):
                traffic_stats[star_comb_feat] = 0
            traffic_stats[star_comb_feat] += traffic_stats[comb_feat]
            if not bidfloor_stats.has_key(star_comb_feat):
                bidfloor_stats[star_comb_feat] = {}
            for price in bidfloor_stats[comb_feat]:
                if not bidfloor_stats[star_comb_feat].has_key(price):
                    bidfloor_stats[star_comb_feat][price] = 0
                bidfloor_stats[star_comb_feat]
                bidfloor_stats[star_comb_feat][price] += bidfloor_stats[comb_feat][price]

    format_result_2 = ''
    for key in traffic_stats:
        ratio = float(traffic_stats[key])/total_line
        if ratio > 0.001:
            #format_result_1 += '%s\t%s\n'% (key,ratio)
            format_result_2 += '\n%s\t%s\t'% ('\t'.join([str(f) for f in key]),ratio)
            total_bid=sum(bidfloor_stats[key].values())
            #print total_bid
            #print traffic_stats[key]
            #print ' 有底价的记录在该组合特征的记录上占多少比例 ',float(total_bid)/traffic_stats[key]
            for bid in bidfloor_stats[key]:
                bid_ratio = float(bidfloor_stats[key][bid])/total_bid
                if bid_ratio > 0.01:
                    #print bid,bid_ratio,','
                    format_result_2 += '%s:%s,'% (bid,bid_ratio)
            format_result_2=format_result_2.rstrip(',')
            #print ''

    open('/home/data/tongpeng/traffic_predict/format_result','w').write(format_result_2)
    return traffic_stats,bidfloor_stats

def get_traffic_ratio(file_name,comb_feat,bidprice):
    traffic_stats,bidfloor_stats = pickle.load(open(file_name,'r'))
    print float(traffic_stats[comb_feat])/sum(traffic_stats.values())
    print bidfloor_stats[comb_feat]
    tmp_sum = 0
    for key in bidfloor_stats[comb_feat]:
        if bidprice > key:
            tmp_sum += bidfloor_stats[comb_feat][key]
    print float(tmp_sum)/sum(bidfloor_stats[comb_feat].values())
            
if __name__ == "__main__":
    input_files = []
    if sys.argv[1:] != []:
        input_files += [open(f) for f in sys.argv[1:]]
    else:
        input_files.append(sys.stdin)
    feats = [
    'req_device_os',
    'req_device_model', 
    'req_device_device_type',
    'req_device_geo_country',
    'req_device_carrier',
    'req_device_connection_type',
    'req_impressions_banner_width',
    'req_impressions_banner_height'
    ]
    result = get_comb_value(input_files,feats)
    pickle.dump(result,open('/home/data/tongpeng/traffic_predict/result','w'))

    #get_ratio('/home/data/tongpeng/traffic_predict/result')
    print '----------------------'
    #get_traffic_ratio('/home/data/tongpeng/traffic_predict/result',('1', '418', '1', 'US', 'WIFI', '3', '320', '50'),0.8)

    a,b=rollup('/home/data/tongpeng/traffic_predict/result')
    print a[('2', '171', '1', '*', 'WIFI', '3', '320', '50')]
    print b[('2', '171', '1', '*', 'WIFI', '3', '320', '50')]
