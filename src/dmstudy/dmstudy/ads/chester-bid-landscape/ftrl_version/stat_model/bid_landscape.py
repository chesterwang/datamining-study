#coding:utf8
#处理
__author__ = 'chester'
import sys,time,os,datetime,math,mmh3
sys.path.append('/home/chester/KuaiPan/workspace/tukmob/')
import util.join as join
import ctr_model.ctr_model_clear as ctr_model


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
    join_parser = join.Parser()
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

        self.join_parser.feed(line)
        all_info = self.join_parser.get_all()

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

class BidFtrl():
    def __init__(self, beta, alpha, lambda1, lambda2, adx_name, class_dict):
        self.beta = beta
        self.alpha = alpha
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.line_no = 0
        self.click_no = 0
        self.class_flags = sorted(set(class_dict.keys()))
        #{"1", "2", "3", "4", "5", "6", "7", "8", "9",}

        self.class_dict = class_dict
        #self.class_dict = {"1":(0,0.05),
        #    "2":(0.05,0.10),
        #    "3":(0.10,0.15),
        #    "4":(0.15,0.20),
        #    "5":(0.20,0.25),
        #    "6":(0.25,0.30),
        #    "7":(0.30,0.35),
        #    "8":(0.35,0.40),
        #    "9":(0.40,0.45),
        #    "10":(0.45,0.50),}
        dir_prefix = '/home/chester/KuaiPan/workspace/tukmob/resource/wzn_price_bin'
        self.class_wznfile_map = {key:dir_prefix+ '/' + key for key in class_dict}
        #文件格式,w\t z\t n\t feat_value(feat_value中不可以含有\t \n)
        #wzn 值格式"1":{3928:[z,n,feat_value]}
        self.wzn = {key:{} for key in class_dict}

        self.reload_wzn()
        self.sampleDataProcessor = SampleDataProcessor()
 
    def get_class_flag(self,price):
        """
            类用字符串来表示
        """
        for class_flag,price_range in self.class_dict.items():
            if price > price_range[0] and price<= price_range[1]:
                return class_flag
        
    def reload_wzn(self):
        self.wzn = {"1":{},
            "2":{},
            "3":{},
            "4":{},
            "5":{},
            "6":{},
            "7":{},
            "8":{},
            "9":{},
            "10":{},}
        for class_flag,wzn_file in  self.class_wznfile_map.items():
            if not os.path.exists(wzn_file):
                os.mknod(wzn_file)
            for line in open(wzn_file,'r'):
                line_arr = line.strip('\n').split('\t')
                vlist = []
                #for vs in arr[1:]:
                #    vlist.append(float(vs))
                #vlist.append(False)#用来标识该项是否修改过，使得每次增量更新模型文件
                self.wzn[class_flag][int(line_arr[0])] = [ float(line_arr[1]),  float(line_arr[2]),line_arr[3]]
    def get_weight(self,class_flag,feat_val):
        """
        初始化为
        """
        para_z = self.get_para_z(class_flag,feat_val)
        para_n = self.get_para_n(class_flag,feat_val)
        return -self.cutoff(para_z, self.lambda1)/(self.lambda2 + (self.beta + math.sqrt(para_n))/self.alpha)

    def get_para_z(self,class_flag,feat_val):
        return self.wzn[class_flag][feat_val][0] if self.wzn[class_flag].has_key(feat_val) else 0
    def get_para_n(self,class_flag,feat_val):
        return self.wzn[class_flag][feat_val][1] if self.wzn[class_flag].has_key(feat_val) else 0

    def cutoff(self, val, threshold):
        #threshold必须为>0
        return (1 if val >= 0 else -1)*(abs(val) - threshold) if abs(val) > threshold else 0

    def get_class_probs(self, feat_vals):
        exp_sum_list = {class_flag:math.exp(sum([self.get_weight(class_flag, feat_val) for feat_val in feat_vals])) for class_flag in self.class_flags}
        sum_exp_sum = sum(exp_sum_list.values())
        if sum_exp_sum == 0:
            #预测不在所有价格范围内
            #思考为什么这样做
            class_flag_num = len(self.class_flags)
            exp_sum_list = {class_flag:1.0/class_flag_num for class_flag in self.class_flags}
            sum_exp_sum = sum(exp_sum_list.values())
            print "error  ----------------------------- error"
        return {class_flag:exp_sum_list[class_flag]/sum_exp_sum  for class_flag in self.class_flags}

    def dump_wzn(self):
        for class_flag,wzn_file in  self.class_wznfile_map.items():
            if not os.path.exists(wzn_file):
                os.mknod(wzn_file)
            out_file = open(wzn_file,'w')
            #处理
            for feat in self.wzn[class_flag]:
                self.wzn[class_flag][feat][2] = self.wzn[class_flag][feat][2].replace('\t','').replace('\n','')
                out_file.write(str(feat) + '\t' + '\t'.join([str(elem) for elem in self.wzn[class_flag][feat]])+'\n')
            out_file.close()

    def train(self, trainfilename ):
        startTime = datetime.datetime.now()
        trainfile = open(trainfilename)

        price_bin = [round(idx*0.025,3) for idx in range(1,21)] 
        for line in trainfile:
            if self.line_no % 10000 == 9999:
                #break
                print self.line_no
            self.line_no += 1
            line = line.strip('\n')
            pred = 0.0
            arr = line.split('\t')

            win_price, hashed_feat_list =  self.sampleDataProcessor.clear(line)

            actual_class_flag = self.get_class_flag(win_price)
            if actual_class_flag is None:
                continue

            class_probs = self.get_class_probs(hashed_feat_list)
            for class_flag in self.class_flags:
                for feat in hashed_feat_list:
                    para_z = self.get_para_z(class_flag,feat)
                    para_n = self.get_para_n(class_flag,feat)
                    gval = class_probs[class_flag] - (1 if class_flag == actual_class_flag  else 0)
                    sigma = (math.sqrt(para_n + gval**2) - math.sqrt(para_n))/self.alpha
                    if not self.wzn[class_flag].has_key(feat):
                        self.wzn[class_flag][feat] = [0,0,'']
                    self.wzn[class_flag][feat][0] = para_z + gval - sigma*self.get_weight(class_flag, feat)
                    self.wzn[class_flag][feat][1] += gval**2
                    self.wzn[class_flag][feat][2] = hashed_feat_list[feat]
        self.dump_wzn()

        print 'impression:' + str(self.line_no)
        print 'click:' + str(self.click_no)
        endTime = datetime.datetime.now()
        print 'time:' + str((endTime - startTime).seconds)
        print 'train is ok!'
        trainfile.close()


    def predict_file(self,sample_file):
        for line in open(sample_file,'r'):
            line = line.strip('\n')
            win_price, hashed_feat_list =  self.sampleDataProcessor.clear(line)
            actual_class_flag = self.get_class_flag(win_price)
            class_probs =self.get_class_probs(hashed_feat_list)
            print {key:round(class_probs[key],2) for key in class_probs},reduce(lambda x,y:x if class_probs[x]>class_probs[y] else y,class_probs), actual_class_flag,win_price
            #print reduce(lambda x,y:x if class_probs[x]>class_probs[y] else y,class_probs), actual_class_flag,price
    def evaluate(self,sample_file):
        import sklearn.metrics as metrics 
        import  numpy
        y_true=[]
        y_score=[]
        predict_accuracy = {}
        total_cnt = 0
        for line in open(sample_file,'r'):
            line = line.strip('\n')
            win_price, hashed_feat_list =  self.sampleDataProcessor.clear(line)
            actual_class_flag = self.get_class_flag(win_price)
            class_probs =self.get_class_probs(hashed_feat_list)
            if actual_class_flag == None:
                continue
            total_cnt +=1
            predict_class_flag = reduce(lambda x,y:x if class_probs[x]>class_probs[y] else y,class_probs)
            if (actual_class_flag,predict_class_flag) not in predict_accuracy:
                predict_accuracy[(actual_class_flag,predict_class_flag)] = 0
            predict_accuracy[(actual_class_flag,predict_class_flag)] += 1

            tmp_y_true = [0]*len(class_probs)
            tmp_y_true[int(actual_class_flag)-1] = 1
            y_true += tmp_y_true
            y_score +=[ class_probs[class_flag] for class_flag in self.class_flags]
            #print {key:round(class_probs[key],2) for key in class_probs},reduce(lambda x,y:x if class_probs[x]>class_probs[y] else y,class_probs), actual_class_flag,win_price
        y_true = numpy.array(y_true)
        y_score = numpy.array(y_score)
        class_num = len(self.class_flags)
        confusion_matrix = numpy.zeros([class_num,class_num])
        for key in predict_accuracy:
            confusion_matrix[int(key[0])-1,int(key[1])-1] = predict_accuracy[key]
        
        numpy.set_printoptions(suppress=True)
        print 'confusion matrix'
        print confusion_matrix
        print 'auc evaluation'
        print metrics.roc_auc_score(y_true,y_score)

    def get_win_rate(self, line, bid):
        win_price, hashed_feat_list =  self.sampleDataProcessor.clear(line)
        actual_class_flag = self.get_class_flag(win_price)
        class_probs = self.get_class_probs(hashed_feat_list)
        return sum([class_probs[key]  for key in  class_probs if bid > class_probs[key]])
    def get_cost(self, line, bid):
        win_price, hashed_feat_list =  self.sampleDataProcessor.clear(line)
        #actual_class_flag = self.get_class_flag(win_price)
        class_probs = self.get_class_probs(hashed_feat_list)
        return sum([(self.class_dict[key][0]+self.class_dict[key][1])/2*class_probs[key]  for key in  class_probs if bid > self.class_dict[key][0]])

    def prediction_file(self,sample_file):
        target_ecpc=0.06
        import util.join as join
        req_parser = join.Parser()
        the_model = ctr_model.LrCtrModel('/home/chester/KuaiPan/workspace/tukmob/resource/wzn/wzn','new')
        bid_array = []
        expected_price_array = []
        surplus_array = []
        line_no = 0
        for line in open(sample_file):
            #if line_no % 1000 == 0:
            if line_no == 1000:
                print line_no
                break
            line_no += 1
            #print ftrl.get_win_rate(line,0.2),
            #print ftrl.get_cost(line,0.2),
            req_parser.feed(line)
            if req_parser.get_adx() == 'youku':
                continue
            bid = round(target_ecpc*the_model.predict_ctr(line)*1000,2)
            expected_price = round(self.get_cost(line,bid),4)
            print 'win_price','pctr','bid','expected_price','win_rate','surplus'
            print req_parser.get_price(),
            print the_model.predict_ctr(line),
            print bid,expected_price,
            print self.get_win_rate(line,bid),
            print (bid-expected_price)*self.get_win_rate(line,bid)
            bid_array.append(round(bid,2))
            expected_price_array.append(round(expected_price,2))
            surplus_array.append(round((bid-expected_price)*self.get_win_rate(line,bid),2))
            
        #print bid_array,expected_price_array,surplus_array

        import collections
        import matplotlib.pyplot as pp

        cnt = collections.Counter(bid_array)
        total_cnt = len(bid_array)
        sort_cnt_key = sorted(cnt.keys())
        pp.clf()
        pp.plot(sort_cnt_key, [ (cnt[ppp]+0.0)/total_cnt for ppp in sort_cnt_key ])
        pp.savefig('/home/chester/bid.png')

        cnt = collections.Counter(expected_price_array)
        total_cnt = len(expected_price_array)
        sort_cnt_key = sorted(cnt.keys())
        pp.clf()
        pp.plot(sort_cnt_key, [ (cnt[ppp]+0.0)/total_cnt for ppp in sort_cnt_key ])
        pp.savefig('/home/chester/expected_price_array.png')


        cnt = collections.Counter(surplus_array)
        total_cnt = len(surplus_array)
        sort_cnt_key = sorted(cnt.keys())
        pp.clf()
        pp.plot(sort_cnt_key, [ (cnt[ppp]+0.0)/total_cnt for ppp in sort_cnt_key ])
        pp.savefig('/home/chester/surplus.png')

def test():
    #trainfilename='/home/chester/KuaiPan/workspace/tukmob/resource/join_log/join_log_may_small1_1'
    trainfilename='/home/chester/KuaiPan/workspace/tukmob/resource/join_log/join_log_april_1'

    tmp_class_dict = {"1":(0,0.05),
        "2":(0.05,0.10),
        "3":(0.10,0.15),
        "4":(0.15,0.20),
        "5":(0.20,0.25),
        "6":(0.25,0.30),
        "7":(0.30,0.35),
        "8":(0.35,0.40),
        "9":(0.40,0.45),
        "10":(0.45,0.50),}
    ftrl = BidFtrl(1, 0.1, 0.005, 1.0,'doubleclick', tmp_class_dict)
    ftrl.train(trainfilename)
    ftrl.dump_wzn()
    ftrl.evaluate('/home/chester/KuaiPan/workspace/tukmob/resource/join_log/join_log_april_2')
    #ftrl.prediction_file('/home/chester/KuaiPan/workspace/tukmob/resource/join_log/join_log_april_2')
    #统计出价 成交价 剩余价值的画图

if __name__ == "__main__":
    test()
