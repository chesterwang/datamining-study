#!/usr/bin/env python
#coding:utf8


import sys
import pickle
import tukmob_protobuf as tp
import gzip

def str2byte(s):
    base='0123456789ABCDEF'
    i=0
    s = s.upper()
    s1=''
    while i < len(s):
        c1=s[i]
        c2=s[i+1]
        i+=2
        b1=base.find(c1)
        b2=base.find(c2)
        if b1 == -1 or b2 == -1:
            return None
        s1+=chr((b1 << 4)+b2)
    return s1

class EnhancedBidRequest():
    def __init__(self):
        self.req = tp.BidRequest()
        self.map_list = {
            'req_device_os':'device.os',
            'req_device_model':'device.model',
            'req_device_device_type':'device.device_type',
            'req_device_geo_country':'device.geo.country',
            'req_device_carrier':'device.carrier',
            'req_device_connection_type':'device.connection_type',
            'req_impressions_banner_width':'impressions[0].banner.width',
            'req_impressions_banner_height':'impressions[0].banner.height',
            }
    def ParseFromLog(self,line):
        self.req.ParseFromString(str2byte(line.strip('\n')))
        #print '----------------%s' % type(self.req.device.geo.geoid)#['geo_id']
        #print '----------------',self.req.device.geo.HasField('geo_id')
        #print '----------------%s' % self.req.impressions[0].banner.width#['geo_id']
    def get(self,field_list):
        return tuple([str(self.get_field(field_name)) for field_name in field_list ])
    def __str__(self):
        return '%s' % self.req
    def get_field(self,field_name):
        if field_name in self.map_list:
            return eval('self.req.' + self.map_list[field_name])
        else:
            return None




def get_comb_value(input_file, the_field_list):

    comb_value_stats = {}
    comb_value_bidfloor = {}
    line_num = 0
    exception_num = 0
    req = EnhancedBidRequest()
    comb_value_stats = {}
    for input_file_name in input_files:
        if input_file_name.find('.gz') != -1:
            input_file = gzip.open(input_file_name)
        else:
            input_file = open(input_file_name)
        for line in input_file:
            if line_num % 10000 == 0:
                print line_num,len(comb_value_stats)
            line_num += 1
            if line.strip('\n') == '':
                continue
            req.ParseFromLog(line)
            comb_value =  tuple(req.get(the_field_list))
            if comb_value not in comb_value_stats:
                comb_value_stats[comb_value] = 0
            comb_value_stats[comb_value] += 1
            #if comb_value not in comb_value_bidfloor:
            #    comb_value_bidfloor[comb_value] = {}
            #if len(comb_value_bidfloor[comb_value].keys()) < 50:
            #    if bidfloor != None:
            #        if bidfloor not in comb_value_bidfloor[comb_value]:
            #            comb_value_bidfloor[comb_value][bidfloor] = 0
            #        comb_value_bidfloor[comb_value][bidfloor] += 1
            print ','.join(the_field_list)
            print '\n'.join(['%s %d' % (key,val) for key,val in comb_value_stats.items()])
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
    #if sys.argv[1:] != []:
    #    input_files += [open(f) for f in sys.argv[1:]]
    #else:
    #    input_files.append(sys.stdin)
    input_files = '/export/bidder_src_logs/dragon_bid_req.log-201506042200_gz_1_18603.gz'

    the_field_list = [
        'req_device_os',
        'req_device_model',
        'req_device_device_type',
        'req_device_geo_country',
        'req_device_carrier',
        'req_device_connection_type',
        'req_impressions_banner_width',
        'req_impressions_banner_height'
        ]

    result = get_comb_value(input_files,the_field_list)
    print result
    #pickle.dump(result,open('/home/data/tongpeng/traffic_predict/result','w'))

    #get_ratio('/home/data/tongpeng/traffic_predict/result')
    print '----------------------'
    #get_traffic_ratio('/home/data/tongpeng/traffic_predict/result',('1', '418', '1', 'US', 'WIFI', '3', '320', '50'),0.8)

    #a,b=rollup('/home/data/tongpeng/traffic_predict/result')
    #print a[('2', '171', '1', '*', 'WIFI', '3', '320', '50')]
    #print b[('2', '171', '1', '*', 'WIFI', '3', '320', '50')]
