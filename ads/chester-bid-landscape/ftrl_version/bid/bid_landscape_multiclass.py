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

class Ftrl():
    """ftrl算法
    """
    def __init__(self, beta, alpha, lambda1, lambda2):
        self.beta = beta
        self.alpha = alpha
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.line_no = 0
        self.click_no = 0
        self.class_dict = {(0,0.1):"1",
            "2":(0.1,0.2),
            "3":(0.2,0.3),
            "4":(0.3,0.4),
            "5":(0.4,0.5),
            "6":(0.5,0.6),
            "7":(0.6,0.7),
            "8":(0.7,0.8),
            "9":(0.8,0.9),}
            "10":(0.9,1),}
        self.class_wznfile_map = {"1":'',
            "2":'',
            "3":'',
            "4":'',
            "5":'',
            "6":'',
            "7":'',
            "8":'',
            "9":'',}
        }
        self.wzn = {"1":{},
            "2":{},
            "3":{},
            "4":{},
            "5":{},
            "6":{},
            "7":{},
            "8":{},
            "9":{},}
        }
 
    def get_class_flag(price):
        """
            类用字符串来表示
        """
        for class_flag,price_range in self.class_dict.items():
            if price > price_range[0] and price< price_range[1]:
                return class_flag
        
    def load_wzn(self):
        for class_flag,wzn_file in  self.class_wznfile_map.items():
            if not os.path.exists(wzn_file):
                os.mknod(wzn_file)
            for line in open(wzn_file,'r'):
                line_arr = line.strip('\n').split('\t')
                vlist = []
                #for vs in arr[1:]:
                #    vlist.append(float(vs))
                #vlist.append(False)#用来标识该项是否修改过，使得每次增量更新模型文件
                self.wzn[class_flag][arr[0]] = line_arr[1:]
    def get_weight(self,class_flag,feat_val):
       para_z = self.wzn[class_flag][feat_val][0]
       para_n = self.wzn[class_flag][feat_val][1]
       return -cutoff(para_z)/(self.lambda2 + (self.beta + sqrt(para_n))/self.alpha)

    def cutoff(self, val, threshold)
        #threshold必须为>0
        return (1 if val >= 0 else -1)(abs(val) - threshold) if abs(val) > threshold else 0

    def get_class_prob(self, class_flag, feat_vals):
        math.exp(sum([self.get_weight(class_flag, feat_val) for feat_val in feat_vals]))
        exp_sum_list = {class_flags:math.exp(sum([self.get_weight(class_flag, feat_val) for feat_val in feat_vals])) for class_flag in class_flags}
        sum_exp_sum = sum(exp_sum_list.values())
        return {class_flag:exp_sum_list[class_flag]/sum_exp_sum  for class_flag in class_flags}

    def train(self, trainfilename, wznfilename, fwfilename):
        startTime = datetime.datetime.now()
        trainfile = open(trainfilename)

        for line in trainfile:
            self.line_no += 1
            arr = line.strip('\n').split('\t')
            pred = 0.0
            clk, train = int(arr[0]), arr[4:]
            if clk == 1:
                self.click_no += 1 

                
            for elem in train:
                if elem not in self.wzn:
                    self.wzn[elem] = [0.0, 0.0, 0.0, True]
                else:
                    self.wzn[elem][3] = True

                if (abs(self.wzn[elem][1]) < self.lambda1):
                    self.wzn[elem][0] = 0.0
                else:
                    self.wzn[elem][0] = -(self.wzn[elem][1] - self.sgn(self.wzn[elem][1])*self.lambda1)/((self.beta+math.sqrt(self.wzn[elem][2]))/self.alpha+self.lambda2)
                pred += self.wzn[elem][0]

            pred = self.sigmoid(pred)

            for feat in train:
                gval = (pred - clk)
                sigma = (math.sqrt(self.wzn[feat][2] + gval*gval) - math.sqrt(self.wzn[feat][2]))/self.alpha
                self.wzn[feat][1] = self.wzn[feat][1] + gval - sigma*self.wzn[feat][0]
                self.wzn[feat][2] += gval*gval

        outfileWZN = open(wznfilename, 'w')
        outfileW = open(fwfilename, 'w')
        #把训练好的特征权值输出
        for f in self.wzn:
            outfileWZN.write(f + '\t' + str(self.wzn[f][0]) + '\t' + str(self.wzn[f][1]) + '\t' + str(self.wzn[f][2]) + '\n')
            if self.wzn[f][0] != 0.0 and self.wzn[f][3]:
                outfileW.write(f + '\t' + str(self.wzn[f][0]) + '\n')

        outfileWZN.close()
        outfileW.close()

        print 'impression:' + str(self.line_no)
        print 'click:' + str(self.click_no)
        endTime = datetime.datetime.now()
        print 'time:' + str((endTime - startTime).seconds)
        print 'train is ok!'

def createPath(path):
    if os.path.exists(path)  == False:
        os.makedirs(path)
 
def getParameters(adxname):
    if adxname == 'doubleclick':
        return 1,0.133,0.005,1
    if adxname == 'smaato':
        return 1,0.457,0.005,1
    if adxname == 'nexage':
        return 1,0.151,0.005,1
    if adxname == 'youku':
        return 1,0.538,0.005,1
    print "no adx"
    return 1,0.5,0.005,1

    if len(sys.argv) == 2:
        trainfilename = sys.argv[1]
        #rootpath 定义了wzn文件夹所在的目录
        rootpath = '/data/data_workspace/featonlineadx'
        stamp = str(time.time())
        split_trainfilename = trainfilename.split('/')
        adx = split_trainfilename[len(split_trainfilename)-2]
        print adx
        path = rootpath + '/wzn/' + adx 
        wznfilename = rootpath + '/wzn/' + adx + '/wzn'
        createPath(path)
        path = rootpath + '/fw/' + adx
        createPath(path)
        fwfilename = rootpath + '/fw/' + adx + '/fw' + stamp 
        beta,alpha,lambda1,lambda2 = getParameters(adx)
        obj = ftrl(beta, alpha , lambda1, lambda2)
        if os.path.exists(wznfilename):
            obj.loadwzn(wznfilename)
        obj.train(trainfilename, wznfilename, fwfilename)
    else:
        print 'params is error!'



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
