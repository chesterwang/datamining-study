# coding:utf8
__author__ = 'chester'
import sys
sys.path.append('/home/chester/KuaiPan/workspace/tukmob')
import ctr_model.ctr_model as ctr_model
import ctr_model.ctr_model_evaluation as ctr_model_evaluation
import util.join as join
import pickle
import math


win_price_field_name = 'event_price'
bid_floor_field_name = 'req_impressions_bid_floor'
campaign_field_name = 'event_ca'


class BidLandscapeModel():
    """
    bid landscape类
    通过dsp的成交价来得到的bid landscape类。
    dsp的成交价也就是其他dsp竞争者的出价bid。
    初始实现是通过简单的统计来达到目的。
    """
    def __init__(self):
        pass

    def train(self, data_file):
        pass

    def predict(self):
        pass

    def evaluate(self):
        pass


class SimpleBidLandscapeModel(BidLandscapeModel):
    """

    """

    def __init__(self):
        pass

    def train(self, join_file, feats_name):
        """
        data_file: join file
        """
        result = get_comb_value(join_file, feats_name)
        self.win_price_stats = {k1:result[k1]["win price"] for k1 in result}
        print self.win_price_stats
        print self.win_price_stats == []
        print self.win_price_stats == None

    def predict(self, feat, bid):
        if feat not in self.win_price_stats:
            return None
        total_num = sum(self.win_price_stats[feat].values())
        below_num = sum([self.win_price_stats[feat][key] for key in self.win_price_stats[feat] if bid >= key])

        #print total_num, below_num

        return float(below_num) / total_num

    def get_cost(self, feat, bid):
        if feat not in self.win_price_stats:
            return None
        total_num = sum([self.win_price_stats[feat][key] for key in self.win_price_stats[feat] if bid >= key])
        cost = sum([key*float(self.win_price_stats[feat][key])/total_num for key in self.win_price_stats[feat] if bid >= key])
        return cost

    def evaluate(self):
        pass

def dict_plus(dict1, dict2):
    """
    两个字典合成一个字典，对每一个键，将两个字段对应的值相加
    """
    dict3 = {}
    for k in set(dict1.keys() + dict2.keys()):
        dict3[k] = (dict1[k] if k in dict1 else 0) + (dict2[k] if k in dict2 else 0)
    return dict3


def binary_search(ascend_sorted_list, target):
    '''
    对于较长列表进行测试，但对长度较短的列表没有测试，即长度为1,2,3的列表
    返回第一个大于等于target的值的索引(从0开始)
    如果target小于列表中的第一个值(最小值)，则返回0
    如果target大于列表中的最后的值(最大值)，则返回len(ascend_sorted_list)(无法索引的值)
    '''
    if type(ascend_sorted_list) != type([]):
        raise NameError('not a list')
    if len(ascend_sorted_list) == 0:
        raise NameError('emptry list')
    low = 0
    high = len(ascend_sorted_list) - 1
    while low < high:
        mid = (low + high) // 2
        midVal = ascend_sorted_list[mid]
        if midVal < target:
            low = mid + 1
        elif midVal > target:
            high = mid - 1
        else:
            return mid
    if low == high:
        cur_val = ascend_sorted_list[low]
        if low == len(ascend_sorted_list) - 1:
            return low if target <= cur_val else low + 1
        elif low == 0:
            return low + 1 if target > cur_val else low
        else:
            if target <= cur_val:
                return low
            else:
                return low + 1
    elif low - 1 == high:
        return low


def get_comb_value(input_files, feats):
    """
    get win price stats and bid-floor stats from input_file for combined feature value
    and specified feature list(feats).
    :type input_files: list
    :param input_files:
    :param feats:specified feats
    :return: comb_feat_stats
    """
    info_key = ['win price', 'bid floor', 'occurrence num']
    info_val = [{}, {}, 0]
    comb_feat_stats = {}
    line_num = 0
    for input_file in input_files:
        for line in open(input_file,'r'):
            line = line.strip('\n')
            if line == '':
                continue
            if line_num % 10000 == 0:
                print line_num, len(comb_feat_stats)
            line_num += 1
            line_array = line.split('|')
            feat_values = dict.fromkeys(feats)
            bid_floor = None
            for key_val in line_array:
                if ':' not in key_val:
                    continue
                key, val = key_val.split(':', 1)
                if key in feats:
                    feat_values[key] = val
                if key == bid_floor_field_name:
                    bid_floor = float(val)
                if key == win_price_field_name:
                    win_price = float(val)
            comb_value = tuple([feat_values[feat] for feat in feats])
            if comb_value not in comb_feat_stats:
                comb_feat_stats[comb_value] = dict.fromkeys(info_key)
                comb_feat_stats[comb_value]['bid floor'] = {}
                comb_feat_stats[comb_value]['win price'] = {}
                comb_feat_stats[comb_value]['occurrence num'] = 0
            comb_feat_stats[comb_value]['occurrence num'] += 1

            if bid_floor not in comb_feat_stats[comb_value]['bid floor'] and len(
                    comb_feat_stats[comb_value]['bid floor'].keys()) < 50:
                comb_feat_stats[comb_value]['bid floor'][bid_floor] = 0
            comb_feat_stats[comb_value]['bid floor'][bid_floor] += 1

            if win_price not in comb_feat_stats[comb_value]['win price']:
                comb_feat_stats[comb_value]['win price'][win_price] = 0
            comb_feat_stats[comb_value]['win price'][win_price] += 1

    return comb_feat_stats


def get_ratio(file_name):
    traffic_stats, bidfloor_stats = pickle.load(open(file_name, 'r'))
    total_line = sum(traffic_stats.values())
    for key in traffic_stats:
        ratio = float(traffic_stats[key]) / total_line
        if ratio > 0.0001:
            print key, float(traffic_stats[key]) / total_line
            total_bid = sum(bidfloor_stats[key].values())
            print 'bid ratio', float(total_bid) / traffic_stats[key]
            for bid in bidfloor_stats[key]:
                bid_ratio = float(bidfloor_stats[key][bid]) / total_bid
                if bid_ratio > 0.1:
                    print bid, bid_ratio, ','
            print ''


def rollup(file_name):
    traffic_stats, bidfloor_stats = pickle.load(open(file_name, 'r'))

    total_line = sum(traffic_stats.values())
    if traffic_stats == None:
        return None
    for feat_idx in range(0, len(traffic_stats.keys()[0])):
        tmp_star_dict = {}
        star_comb_feat = ()
        for comb_feat in traffic_stats.keys():
            star_comb_feat = comb_feat[0:feat_idx] + ('*',) + comb_feat[feat_idx + 1:]
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
        ratio = float(traffic_stats[key]) / total_line
        if ratio > 0.001:
            # format_result_1 += '%s\t%s\n'% (key,ratio)
            format_result_2 += '\n%s\t%s\t' % ('\t'.join([str(f) for f in key]), ratio)
            total_bid = sum(bidfloor_stats[key].values())
            # print total_bid
            # print traffic_stats[key]
            # print ' 有底价的记录在该组合特征的记录上占多少比例 ',float(total_bid)/traffic_stats[key]
            for bid in bidfloor_stats[key]:
                bid_ratio = float(bidfloor_stats[key][bid]) / total_bid
                if bid_ratio > 0.01:
                    # print bid,bid_ratio,','
                    format_result_2 += '%s:%s,' % (bid, bid_ratio)
            format_result_2 = format_result_2.rstrip(',')
            # print ''

    open('/home/data/tongpeng/traffic_predict/format_result', 'w').write(format_result_2)
    return traffic_stats, bidfloor_stats


def get_traffic_ratio(file_name, comb_feat, bidprice):
    traffic_stats, bidfloor_stats = pickle.load(open(file_name, 'r'))
    print float(traffic_stats[comb_feat]) / sum(traffic_stats.values())
    print bidfloor_stats[comb_feat]
    tmp_sum = 0
    for key in bidfloor_stats[comb_feat]:
        if bidprice > key:
            tmp_sum += bidfloor_stats[comb_feat][key]
    print float(tmp_sum) / sum(bidfloor_stats[comb_feat].values())


def predict_4_files(target_ecpc,input_files, ctr_model_file_name, bid_landscape_model_file_name, out_file_name):
    """predict
    :param input_files:
    :param the_ctr_model:
    :return:
    """

    info_key = ['win price', 'bid floor', 'occurrence num']

    the_ctr_model = ctr_model.LrCtrModel(ctr_model_file_name, 'new')

    bid_landscape_model = pickle.load(open(bid_landscape_model_file_name, 'r'))

    out_file = open(out_file_name,'w')

    #bid_info = {'10544':4,'10564':1.8,'10501':2,'10527':2}

    req_parser = join.Parser()
    line_num = 0
    for input_file in input_files:
        for line in open(input_file,'r'):
            line_num += 1
            if line_num % 1000 == 0:
                print line_num
            #if line_num > 100:
            #    sys.exit(1)
            req_parser.feed(line)
            field_dict = req_parser.get_all()
            if field_dict == None:
                continue
            pctr = the_ctr_model.predict_ctr(field_dict['feature_values'])

            line_array = line.strip('\n').split('|')
            feat_values = dict.fromkeys(feats)
            bid_floor = None
            for key_val in line_array:
                if ':' not in key_val:
                    continue
                key, val = key_val.split(':', 1)
                if key in feats:
                    feat_values[key] = val
                if key == bid_floor_field_name:
                    bid_floor = float(val)
                if key == win_price_field_name:
                    win_price = float(val)
                if key ==  campaign_field_name:
                    camp_id = val
            comb_value = tuple([feat_values[feat] for feat in feats])

            if comb_value == 'doubleclick':
                continue

            click_flag = 1 if field_dict['click_flag'] == True else 0
            #bid = bid_info[camp_id]*0.62
            bid = target_ecpc*pctr*1000
            win_rate = bid_landscape_model.predict(comb_value,bid)
            #print bid
            expected_cost = bid_landscape_model.get_cost(comb_value,bid)
            ecpc = float(expected_cost)/pctr

            if bid < win_price:
                continue
            
            out_file.write('%d\t%f\t%f\t%f\t%f\t%f\t%f\n' % (click_flag,pctr,win_rate,bid,win_price,expected_cost,ecpc))



def simulate_camp(target_ecpc,input_files, ctr_model_file_name, bid_landscape_model_file_name, out_file_name):
    """predict
    :param input_files:
    :param the_ctr_model:
    :return:
    """

    simulate_result = {idx*0.025:{'cnt':0,'cost':0,'click':0} for idx in range(1,40)}

    info_key = ['win price', 'bid floor', 'occurrence num']

    the_ctr_model = ctr_model.LrCtrModel(ctr_model_file_name, 'new')

    bid_landscape_model = pickle.load(open(bid_landscape_model_file_name, 'r'))

    out_file = open(out_file_name,'w')

    bid_info = {'10544':4,'10564':1.8,'10501':2,'10527':2}

    surplus_stats = {}

    req_parser = join.Parser()
    actual_pred_list = []
    line_num = 0
    for input_file in input_files:
        for line in open(input_file,'r'):
            line_num += 1
            if line_num % 1000 == 0:
                print line_num
            #if line_num > 100:
            #    break
            req_parser.feed(line)
            field_dict = req_parser.get_all()
            if field_dict == None:
                continue
            pctr = the_ctr_model.predict_ctr(field_dict['feature_values'])

            line_array = line.strip('\n').split('|')
            feat_values = dict.fromkeys(feats)
            bid_floor = None
            for key_val in line_array:
                if ':' not in key_val:
                    continue
                key, val = key_val.split(':', 1)
                if key in feats:
                    feat_values[key] = val
                if key == bid_floor_field_name:
                    bid_floor = float(val)
                if key == win_price_field_name:
                    win_price = float(val)
                if key ==  campaign_field_name:
                    camp_id = val
            comb_value = tuple([feat_values[feat] for feat in feats])

            if comb_value == 'doubleclick':
                continue

            click_flag = 1 if field_dict['click_flag'] == True else 0
            #bid = bid_info[camp_id]*0.62
            bid = target_ecpc*pctr*1000
            win_rate = bid_landscape_model.predict(comb_value,bid)
            #print bid
            expected_cost = bid_landscape_model.get_cost(comb_value,bid)
            ecpc = float(expected_cost)/pctr
            
            surplus = (bid - expected_cost) * win_rate
            #print target_ecpc,pctr,expected_cost,win_rate
            if  round(surplus,2) not in surplus_stats:
                surplus_stats[round(surplus,2)] = 0
            surplus_stats[round(surplus,2)] += 1
            #if surplus > 0.4:
            #    out_file.write('%d\t%f\t%f\t%f\t%f\t%f\t%f\n' % (click_flag,pctr,win_rate,bid,win_price,expected_cost,ecpc))
            surplus_bin = int(surplus/0.025)*0.025
            if bid < win_price:
                continue
            if surplus_bin in simulate_result:
                simulate_result[surplus_bin]['cnt'] += 1
                simulate_result[surplus_bin]['cost'] += win_price
                if click_flag == 1:
                    simulate_result[surplus_bin]['click'] += 1
    print surplus_stats
    print simulate_result
    cnt,cost,click = 0,0,0
    print 'surplus bin','imp','cost','click','ecpc','ctr'
    for surplus_bin in sorted(simulate_result.keys(),reverse=True):
        cnt += simulate_result[surplus_bin]['cnt']
        cost += simulate_result[surplus_bin]['cost']
        click += simulate_result[surplus_bin]['click']
        print surplus_bin,cnt,cost,click,cost/click,float(click)/cnt

def simple_evaluate(file_name):
    relative_error = 0
    abs_error = 0
    cnt = 0
    nan_num = 0
    for line in open(file_name,'r'):
        line_array=line.strip('\n').split('\t')
        win_price = float(line_array[4])
        expected_cost = float(line_array[5])
        if win_price == 0:
            nan_num += 1
            continue
        relative_error += ((expected_cost - win_price)/win_price)**2
        abs_error += (expected_cost - win_price)**2
        cnt += 1
    print '相对误差和,绝对误差和,数量,相对平方误差，绝对平方误差，异常记录数'
    print relative_error,abs_error,cnt,math.sqrt(relative_error/cnt),math.sqrt(abs_error/cnt),nan_num



def predict_ctr(input_files, ctr_model_file_name ):
    """predict
    :param input_files:
    :param the_ctr_model:
    :return:
    """

    info_key = ['win price', 'bid floor', 'occurrence num']

    the_ctr_model = ctr_model.LrCtrModel(ctr_model_file_name, 'new')

    out_file = open(out_file_name,'w')

    bid_info = {'10544':4,'10564':1.8,'10501':2,'10527':2}

    req_parser = join.Parser()
    line_num = 0
    actual_pred_list = []
    for input_file in input_files:
        for line in open(input_file,'r'):
            line_num += 1
            if line_num % 1000 == 0:
                print line_num
            #if line_num > 100:
            #    sys.exit(1)
            req_parser.feed(line)
            field_dict = req_parser.get_all()
            if field_dict == None:
                continue
            pctr = the_ctr_model.predict_ctr(field_dict['feature_values'])
            click_flag = 1 if field_dict['click_flag'] == True else 0
            actual_pred_list.append((click_flag,pctr))
    print ctr_model_evaluation.predict_evaluation(actual_pred_list)


if __name__ == "__main__":
    input_files = []
    #if sys.argv[1:] is not []:
    #    input_files += [open(f) for f in sys.argv[1:]]
    #else:
    #    input_files.append(sys.stdin)

    #input_files = [open('/home/chester/KuaiPan/workspace/tukmob/resource/join_log/data1430279071672.COMPLETED')]

    #input_files = ['/home/chester/data/join_log/data1424838250795.COMPLETED.nonyouku.10733']
    input_files = ['/home/chester/data/join_log_may']
    feats = [
        'req_adx',
        'req_device_os',
        'req_device_model',
        'req_device_device_type',
        'req_device_geo_country',
        'req_device_carrier',
        'req_device_connection_type',
        'req_impressions_banner_width',
        'req_impressions_banner_height'
    ]

    simpleBidLandscapeModel = SimpleBidLandscapeModel()
    simpleBidLandscapeModel.train(input_files, feats)
    pickle.dump(simpleBidLandscapeModel, open('/tmp/result', 'w'))
    simpleBidLandscapeModel = pickle.load(open('/tmp/result', 'r'))

    bid_landscape_model_file_name = '/tmp/result'
    ctr_model_file_name = '/home/chester/KuaiPan/workspace/tukmob/resource/wzn/wzn'
    out_file_name = '/tmp/predict'

    #for bid in range(0,200):
    #    print simpleBidLandscapeModel.predict(('2', '171', '1', 'CN', None, None, '[320,320]', '[50,50]'), bid*0.005),
    #    print simpleBidLandscapeModel.get_cost(('2', '171', '1', 'CN', None, None, '[320,320]', '[50,50]'), bid*0.005)


    print '--------------------'
    import matplotlib.pyplot as pp
    for comb_value in simpleBidLandscapeModel.win_price_stats:
        #print comb_value, simpleBidLandscapeModel.win_price_stats[comb_value]
        pp.clf()
        info=zip(*simpleBidLandscapeModel.win_price_stats[comb_value].items())
        xx = sorted(simpleBidLandscapeModel.win_price_stats[comb_value].keys())
        yy = [simpleBidLandscapeModel.win_price_stats[comb_value][xxx] for xxx in xx]
        if sum(yy) <100:
            continue
        pp.plot(xx,yy)
        pp.title(str(comb_value))
        print comb_value
        #pp.show()


    ecpc=0.05
    predict_4_files(ecpc,input_files, ctr_model_file_name, bid_landscape_model_file_name, out_file_name)


    #simulate_camp(ecpc,input_files, ctr_model_file_name, bid_landscape_model_file_name, '/tmp/simulate_result')

    simple_evaluate(out_file_name)

    predict_ctr(input_files, ctr_model_file_name)

    # print 3
    # result = get_comb_value(input_files, feats)
    # for k1 in result:
    #     print k1
    #     for k2 in result[k1]:
    #         if k2 == 'occurrence num':
    #             print result[k1][k2]
    #         else:
    #             print result[k1][k2]




    #             # pickle.dump(result, open('/home/data/tongpeng/traffic_predict/result', 'w'))
    #             #
    #             # # get_ratio('/home/data/tongpeng/traffic_predict/result')
    #             # print '----------------------'
    #             # # get_traffic_ratio('/home/data/tongpeng/traffic_predict/result',('1', '418', '1', 'US', 'WIFI', '3', '320', '50'),0.8)
    #             #
    #             # a, b = rollup('/home/data/tongpeng/traffic_predict/result')
    #             # print a[('2', '171', '1', '*', 'WIFI', '3', '320', '50')]
    #             # print b[('2', '171', '1', '*', 'WIFI', '3', '320', '50')]


#awk '{if(($5-0)!=0){ eval += (($5-$6)/$5)^2;cnt+=1} else{nan+=1}}END{print eval,cnt,sqrt(eval/cnt),nan}' predict
