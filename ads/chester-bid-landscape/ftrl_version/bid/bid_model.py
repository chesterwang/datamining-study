# !/usr/bin/env python
# coding:utf-8
import math

class BidModel():
    '''
    出价模型
    '''
    def __init__(self, bid_strategy_type, fixed_parameter,auc,avg_ctr):
        '''
        type:
            threshold: fixed_parameter=[avg_ctr]
            lin:  fixed_parameter=[avg_ctr,degree]或者[avg_ctr]
            ortb: fixed_parameter=[c1,c2]
        '''
        self.bid_strategy_type = bid_strategy_type
        self.fixed_parameter = fixed_parameter
        self.auc = auc
        self.avg_ctr = avg_ctr
        #if auc <= 0.5: #auc大小不在这里进行检查，而是在该调用该类的外部进行检查
        #    raise NameError('auc is too low')
        self.ctr_pow = (auc - 0.5)*2  #ctr去依赖化的幂次
        # 辅助参数，便于出价计算
        if bid_strategy_type == "lin":
            if len(self.fixed_parameter) == 1:
                #增加ctr依赖程度参数，如不指定，默认为1
                pass
                #self.fixed_parameter.append(1)
        if bid_strategy_type == 'ortb':
            #辅助参数，预计算好，不需要每次计算出价时再计算。
            self.aux_parameter = fixed_parameter[0] ** 2 - fixed_parameter[0] * fixed_parameter[1]
    def get_bids(self, ctr, variable_paras):
        '''
        根据可变参数的值和某req的ctr来得到出价
        variable_parameter = [0.1,0.2,0.3...] #表示许多可变参数的列表
        type:
            threshld: variable_paras=[fixed price,...]
            lin:  variable_paras=[base price,...]
            ortb: variable_paras=[lambda,...]
        '''
        if len(variable_paras) == 0:
            raise NameError("there is no variable paras")
        if self.bid_strategy_type == 'threshold':
            #阈值为平均点击率，大于该平均点击率才出价
            return [p if ctr > self.fixed_parameter[0] else 0 for p in variable_paras]
        elif self.bid_strategy_type == 'lin':
            return [float(p) * ctr / (self.fixed_parameter[0]) for p in variable_paras]
        elif self.bid_strategy_type == 'ortb':
            # 如果该值为负，则不处理，因为肯定竞不到，即相当于值为0
            bids = [-self.fixed_parameter[1] + math.sqrt(ctr / p + self.aux_parameter) 
                if ctr / p > -self.aux_parameter else -self.fixed_parameter[1] for p in variable_paras]
            # 底价处理,小于该底价，则胜率为0，即出价为0,真正线上用时，则不出价(因为点击率过低)
            # 以后再讨论
            return [bid if bid > 0 else 0 for bid in bids]
    def get_bids_auc(self, ctr, variable_paras):
        return self.get_bids(((ctr/self.avg_ctr)**self.ctr_pow)*self.avg_ctr, variable_paras)

    def get_paras_by_log(self, central_para, max_para, min_para, range_num):
        '''
            即使参数为负，也能正常运行,因为log只对倍数操作
        '''
        max_fold = float(max_para) / central_para
        min_fold = float(min_para) / central_para
        bin_size = (math.log(max_fold) - math.log(min_fold)) / range_num
        exp_num = [math.log(min_fold) + idx * bin_size for idx in range(0, range_num + 1)]
        if self.bid_strategy_type == 'threshold':
            return [central_para * math.exp(num) for num in exp_num]
        elif self.bid_strategy_type == 'lin':
            return [central_para * math.exp(num) for num in exp_num]
        elif self.bid_strategy_type == 'ortb':
            return sorted([central_para * math.exp(num) for num in exp_num], reverse=True)
