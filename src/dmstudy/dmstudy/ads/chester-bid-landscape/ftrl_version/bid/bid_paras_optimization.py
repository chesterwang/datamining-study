# !/usr/bin/env python
# coding:utf-8
import sys, math, time,os,json,logging
import ConfigParser

import join_log_stat
import ctr_model.lr_ctr_model as lr_ctr_model
import ctr_model.ctr_model_evaluation as ctr_model_evaluation
import bid_model
import util.join as join
import util.redis_parse as redis_parse

bpo_logger = logging.getLogger('bid_paras_optimization')
bpo_logger.setLevel(logging.DEBUG) 

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

def history_repeat(bid_history_files, the_ctr_model, bid_model, candidate_paras):
    '''
    历史重演，对一批历史数据进行模拟投放
    paras:
        bid_history_files:join文件列表
        the_ctr_model:ctr模型
        bid_model:出价模型
        candidate_paras:候选参数
    return:
        paras_perf[camp_grp][para] =
            {'impression':,'avg_pctr':,'click':,'cost':,'ctr':,'ecpc':,'cpm':}
    '''
    candidate_paras = {camp_grp:candidate_paras[camp_grp] for camp_grp in candidate_paras.keys() if len(candidate_paras[camp_grp]) != 0 }
    bpo_logger.info('**************history_repeat function start**************')
    bpo_logger.info('files:%s' % ','.join(bid_history_files))
    bpo_logger.info('************** bid_model: %s**************' % (bid_model.keys()))
    bpo_logger.info('************** candidate_paras: %s**************' % (candidate_paras))
    stop_flag_idx = {}
    result = {}
    for (camp_id, grp_id) in bid_model.keys():
        tmp_num = len(candidate_paras[(camp_id, grp_id)])
        stop_flag_idx[(camp_id, grp_id)] = tmp_num
        result[(camp_id, grp_id)] = [None] * tmp_num
        for idx in range(0, tmp_num):
            result[(camp_id, grp_id)][idx] = {'impression':0, 'avg_pctr':0, 'click':0, 'cost':0}
    req_parser = join.Parser()
    total_time = 0
    for bid_history_file in bid_history_files:
        for line in open(bid_history_file):
            req_parser.feed(line)
            field_dict = req_parser.get_all()
            if field_dict == None:
                continue
            win_price = float(field_dict['win_price'])
            camp_grp = (field_dict['campaign_id'], field_dict['adgroup_id'])
            #bid_model的camp_grp 为有效的adgroup，如果该条req的adgroup不再bid_model中，则continue
            if (not candidate_paras.has_key(camp_grp)) or (not bid_model.has_key(camp_grp)) or win_price == None or win_price <= 0:
                continue
            pctr = the_ctr_model.predict_ctr(field_dict['feature_values'])
            candidate_bid_prices = bid_model[camp_grp].get_bids_auc(ctr=pctr, variable_paras=candidate_paras[camp_grp])
            first_ge_idx = binary_search(candidate_bid_prices, win_price)

            #非累积方式
            #if first_ge_idx < stop_flag_idx[camp_grp]:
            #    for tmp_idx in range(first_ge_idx, stop_flag_idx[camp_grp]):
            #        result[camp_grp][tmp_idx]['impression'] += 1
            #        result[camp_grp][tmp_idx]['avg_pctr'] += pctr
            #        result[camp_grp][tmp_idx]['click'] += (1 if field_dict['click_flag'] == '1' else 0)
            #        result[camp_grp][tmp_idx]['cost'] += win_price

            # 因为没有投放限制(比如总预算，总预订点击等)，下列语句被注释了
            # 指定资源限制方法:这里是成本限制,50%*总成本
            # print float(total_budget[camp_grp])/2
            # stop_flag_idx[camp_grp] = binary_search([result[camp_grp][idx]['cost'] for idx in range(0,stop_flag_idx[camp_grp])],float(total_budget[camp_grp])/16)
            # print stop_flag_idx[camp_grp]
            
            #累积方式，累积方式是不能添加资源限制的。累计方式速度更快
            if first_ge_idx < stop_flag_idx[camp_grp]:
                result[camp_grp][first_ge_idx]['impression'] += 1
                result[camp_grp][first_ge_idx]['avg_pctr'] += pctr
                result[camp_grp][first_ge_idx]['click'] += (1 if field_dict['click_flag'] == True else 0)
                result[camp_grp][first_ge_idx]['cost'] += win_price

    for camp_grp in result:
        for idx in range(1,len(result[camp_grp])):
            for tmp_metric in ['impression','avg_pctr','click','cost']:
                result[camp_grp][idx][tmp_metric] += result[camp_grp][idx-1][tmp_metric]

    #计算ctr/avg_pctr/ecpc/cpm等衍生度量
    for camp_grp in result:
        for tmp_idx in range(0, len(result[camp_grp])):
            result[camp_grp][tmp_idx]['cost'] /= 1000  # 修改单位
            # print result[camp_grp]
            tmp_dict = result[camp_grp][tmp_idx]
            result[camp_grp][tmp_idx]['ctr'] = ((tmp_dict['click'] + 0.0) / tmp_dict['impression']) if tmp_dict['impression'] != 0 else 0
            result[camp_grp][tmp_idx]['avg_pctr'] = ((tmp_dict['avg_pctr'] + 0.0) / tmp_dict['impression']) if tmp_dict['impression'] != 0 else 0
            result[camp_grp][tmp_idx]['ecpc'] = (tmp_dict['cost']) / tmp_dict['click'] if tmp_dict['click'] != 0 else 0
            result[camp_grp][tmp_idx]['cpm'] = 1000 * tmp_dict['cost'] / tmp_dict['impression']  if tmp_dict['impression'] != 0 else 0

    #提取出具体参数，而非参数索引
    paras_perf = {}
    #for camp_grp in result.keys():
    #    paras_perf[camp_grp] = {}
    #    for idx in range(0, len(candidate_paras[camp_grp])):
    #        paras_perf[camp_grp][candidate_paras[camp_grp][idx]] = result[camp_grp][idx]
    paras_perf ={camp_grp:{ candidate_paras[camp_grp][idx]:result[camp_grp][idx] for idx in range(0, len(candidate_paras[camp_grp]))}  for camp_grp in result.keys()}

    #打印结果
    bpo_logger.info('**************history_repeat function end**************')
    formatter = 'paras_performance\ncampaign id:{camp}\nadgroup id:{grp}\nbid strategy:{strategy}\nbid strategy fixed parameter:{para}\n'
    for camp_grp in paras_perf.keys():
        log_perf_str = 'bid_history_files:%s\n' % ','.join(bid_history_files)
        log_perf_str += formatter.format(
            camp=camp_grp[0],
            grp=camp_grp[1],
            strategy=bid_model[camp_grp].bid_strategy_type,
            para=bid_model[camp_grp].fixed_parameter)
        log_perf_str += 'para click imp cost cpc ctr avg_pctr cpm\n'
        log_perf_str += 'unit: US dollar\n'
        for para in sorted(paras_perf[camp_grp].keys()):
            tmp_dict = paras_perf[camp_grp][para]
            log_perf_str += str(para) + ' %(click)s %(impression)s %(cost)s %(ecpc)s %(ctr)s %(avg_pctr)s %(cpm)s\n' % tmp_dict


        bpo_logger.info('************parameter performance start************')
        bpo_logger.info(log_perf_str)
        bpo_logger.info('************parameter performance end************')
    #print paras_perf

    return paras_perf


def history_repeat_filter(bid_history_files, the_ctr_model, bid_model, candidate_paras,outfilename):
    '''
    这里仅有一个参数
    历史重演，对一批历史数据进行模拟投放
    paras:
        bid_history_files:join文件列表
        the_ctr_model:ctr模型
        bid_model:出价模型
        candidate_paras:候选参数
    return:
        paras_perf[camp_grp][para] =
            {'impression':,'avg_pctr':,'click':,'cost':,'ctr':,'ecpc':,'cpm':}
    '''
    candidate_paras = {camp_grp:candidate_paras[camp_grp] for camp_grp in candidate_paras.keys() if len(candidate_paras[camp_grp]) == 1 }
    if len(candidate_paras) == 0:
        print 'there is no candidate parameter'
        return 
            
    click_num = 0
    imp_num = 0
    cost = 0
    click_num_old = 0
    imp_num_old = 0
    cost_old = 0
        
    outfile=open(outfilename,'w')
    for bid_history_file in bid_history_files:
        for line in open(bid_history_file):
            #line = line.rstrip('\n')
            field_dict = join.get_field_dict(line)
            if field_dict == None:
                continue
            win_price = float(field_dict['win_price'])
            camp_grp = (field_dict['campaign_id'], field_dict['adgroup_id'])
            if (not candidate_paras.has_key(camp_grp)) or (not bid_model.has_key(camp_grp)) or win_price == None or win_price <= 0:
                continue
            pctr = the_ctr_model.predict_ctr(field_dict['feature_values'])
            candidate_bid_prices = bid_model[camp_grp].get_bids_auc(pctr, candidate_paras[camp_grp])
            if candidate_bid_prices[0] >= win_price:
                outfile.write(line)
                imp_num += 1
                click_num += (1 if field_dict['click_flag'] == True else 0)
                cost += win_price
            imp_num_old += 1
            click_num_old += (1 if field_dict['click_flag'] == True else 0)
            cost_old += win_price
    cost = float(cost)/1000
    cost_old = float(cost_old)/1000

    print 'file%s' % bid_history_files
    print 'old imp_num %d,click_num %d,cost %.4f' % (imp_num_old,click_num_old,cost_old)
    print 'old cpm %.4f,ctr %.8f,cpc %.4f' % (1000*cost_old/imp_num_old,float(click_num_old)/imp_num_old,cost_old/click_num_old)
    print 'imp_num %d,click_num %d,cost %.4f' % (imp_num,click_num,cost)
    print 'cpm %.4f,ctr %.8f,cpc %.4f' % (1000*cost/imp_num,float(click_num)/imp_num,cost/click_num)

def bid_paras_optimization(bid_history_files, the_ctr_model, bid_model, min_para, max_para, max_ecpc):
    '''
    对出价历史中的每个adgroup以及指定出价策略，挑选出最优的参数。
    paras:
        bid_history_files: 为join好的全部为win的日志文件列表
        initial_paras:默认为单个参数，即为一个浮点型变量
        endure_max_ecpc:reference effective CPC 可取为上一个时间段内的平均eCPC,或者使用总的 max eCPC
    return:
        optimal_paras[camp_grp]:[optimal_para,] or []
    '''
    candidate_paras = {}
    for (camp_id, grp_id) in bid_model.keys():
        #initial_para定为最大参数和最小参数之间的平均
        candidate_paras[(camp_id, grp_id)] = bid_model[(camp_id, grp_id)].get_paras_by_log(central_para=(min_para + max_para + 0.0) / 2, max_para=max_para, min_para=min_para, range_num=200)

    paras_perf = {}
    paras_perf  = history_repeat(bid_history_files, the_ctr_model, bid_model, candidate_paras)
    optimal_paras = {}
    for camp_grp in bid_model.keys():
        if not paras_perf.has_key(camp_grp):
            continue
        #大于10个点击的才能进行优化，因为点击太少时的优化结果很不稳定
        para_list = paras_perf[camp_grp].keys()
        #tmp_paras_ecpc为保留了3位小数的ecpc字典
        tmp_paras_ecpc = {para: round(paras_perf[camp_grp][para]['ecpc'],4) for para in para_list}
        #para_list = filter( lambda x:True if paras_perf[camp_grp][x]['click'] >= 10 else False, para_list )
        para_list = [para for para in para_list if paras_perf[camp_grp][para]['click'] >= 10 ]
        # 考虑异常情况，没有任何一个参数能达到目标点击量
        if len(para_list) == 0:
            bpo_logger.warn('for camp_grp %s and bid strategy %s, click # of all parameters < 10 ' % (camp_grp, bid_model[camp_grp].bid_strategy_type))
            optimal_paras[camp_grp] = []
            continue
        # 小于目标cpc上限的参数集
        if type(max_ecpc) == type({}):
            tmp_max_ecpc = max_ecpc[camp_grp[0]]
        else:
            tmp_max_ecpc = max_ecpc
        para_list = [para for para in para_list if tmp_paras_ecpc[para] < tmp_max_ecpc ]
        if len(para_list) == 0:
            bpo_logger.warn('for camp_grp %s and bid strategy %s, ecpc # of all parameters < %.f ' % (camp_grp, bid_model[camp_grp].bid_strategy_type, tmp_max_ecpc))
            #若没有任何一个参数可以达到该目标ecpc，则取最小参数
            optimal_paras[camp_grp] = [min(tmp_paras_ecpc.keys(),key=lambda x:tmp_paras_ecpc[x])]
            continue
        #排序
        para_list.sort()
        #去除参数列表两端的无效参数
        last_effective_idx,first_effective_idx = None,None
        last_para_ecpc,first_para_ecpc = tmp_paras_ecpc[para_list[-1]],tmp_paras_ecpc[para_list[0]]
        max_margin_ecpc=max(last_para_ecpc,first_para_ecpc)
        bpo_logger.info('max_margin_ecpc:%s ' % str(max_margin_ecpc))
        try:
            last_effective_idx = len(para_list)-[ True if tmp_paras_ecpc[para] == last_para_ecpc  else False for para in para_list[::-1] ].index(False)
            first_effective_idx = [ True if tmp_paras_ecpc[para] == first_para_ecpc  else False for para in para_list ].index(False)
        except ValueError:
            raise NameError('parameter not change ecpc performance ')
        if last_effective_idx != None and first_effective_idx != None:
            para_list = para_list[first_effective_idx:last_effective_idx]
        para_list = [para for para in para_list if tmp_paras_ecpc[para] < max_margin_ecpc*0.9 ]

        #bpo_logger.info('cpc90 %f, max cpc %f',cpc90,max([paras_perf[camp_grp][para]['ecpc'] for para in paras_perf[camp_grp].keys()]))

        # 小于目标cpc上限的参数集中点击量最大的参数
        if len(para_list) >= 2:
            optimal_paras[camp_grp] = [reduce(lambda x, y:x if paras_perf[camp_grp][x]['click'] > paras_perf[camp_grp][y]['click'] else y, para_list)]
        elif  len(para_list) == 1:
            optimal_paras[camp_grp] = [para_list[0]]
        else:
            optimal_paras[camp_grp] = []
    return optimal_paras


def strategy_optimization(new_old, bid_strategy_type, ctrmodel_file_name, join_log_files_name, adgroup_list, min_para, max_para, max_ecpc, ctrmodel_auc, bidprice_out_file, strategy_out_file, auc_threshold):
    '''
        针对所有指定策略类型进行优化
        initial_para = {'lin':0.22,'ortb':0.016}
        没有实现mcpc
    '''

    bpo_logger.info('************bid_paras_optimization.py start************')
    bpo_logger.info('bid_paras_optimization.py start. join_log_file_name:%s,ctr_weight_file:%s' % (join_log_files_name, ctrmodel_file_name))
    start_time = time.clock()

    optimal_paras_str = ''
    lrCtrModel = lr_ctr_model.LrCtrModel(fwfile_name=ctrmodel_file_name,new_old=new_old)
    if ctrmodel_auc == None:
        eval_dict,eval_str = ctr_model_evaluation.ctr_model_evaluation(join_log_files_name,lrCtrModel)
        ctrmodel_auc = eval_dict['auc']
        print 'auc******************%s' % ctrmodel_auc
    bpo_logger.info('ctr model auc:%f' %  ctrmodel_auc)
    if ctrmodel_auc < auc_threshold:
        bpo_logger.info('auc is too little. exit')
        sys.exit(2)
    stat_result = join_log_stat.join_log_stat(file_names=join_log_files_name, bin_num=20, fit_flag=True if bid_strategy_type == "ortb" else False)

    #由于实际情况时，一般只有一种出价策略，因此这里在顶层对出价策略进行迭代
    #不再对策略进行迭代，该函数每次只使用一次策略

    bidModel = {}#针对每个adgroup都有一个出价模型,即字典的键为camp_id与adgroup_id,值为BidModel对象
    if stat_result == {}:
        bpo_logger.info('join log stat: stat_result is empty,there is no join_log data')
    for (camp_id, grp_id) in stat_result.keys():
        #过滤，对于活着的ecpc才进行历史重演
        if type(max_ecpc) == type({}):
            if camp_id not in  max_ecpc:
                continue
        if  adgroup_list == []:
            #空列表相当于不做任何限制
            pass
        else:
            if grp_id in adgroup_list:
                continue
            else:
                pass
        if stat_result[(camp_id, grp_id)]['click'] < 10:
            bpo_logger.info('campaign%s,adgroup%s,click number is too small:%d' % (camp_id, grp_id,stat_result[(camp_id, grp_id)]['click']))
            continue
        avg_ctr = float(stat_result[(camp_id, grp_id)]['click']) / stat_result[(camp_id, grp_id)]['impression']
        avg_cpc = float(stat_result[(camp_id, grp_id)]['cost']) / stat_result[(camp_id, grp_id)]['click']
        #print camp_id, grp_id, avg_ctr
        #if bid_strategy_type == 'mcpc':
        #    optimal_paras_str += '%s\t%s\t%s\n' % (grp_id, bid_strategy_type, round(avg_cpc, 6))
        #    continue
        fixed_parameter = None
        if bid_strategy_type == 'threshold':
            fixed_parameter = [avg_ctr]
        elif bid_strategy_type == 'lin':
            fixed_parameter = [avg_ctr]
        elif bid_strategy_type == 'ortb':
            if not stat_result[(camp_id, grp_id)].has_key('win_function_fitting'):
                continue
            fixed_parameter = stat_result[(camp_id, grp_id)]['win_function_fitting']['fitting_para']
        if fixed_parameter != None:
            bidModel[(camp_id, grp_id)] = bid_model.BidModel(bid_strategy_type=bid_strategy_type, fixed_parameter=fixed_parameter,auc=ctrmodel_auc,avg_ctr=avg_ctr)
    bpo_logger.info('Generated bidModel list:%s' % bidModel.keys())
    optimal_paras = {}
    optimal_paras_str = ""
    optimal_strategy_str = ""
    if bidModel == {}:
        bpo_logger.info('bidModel is empty. there is available bid model.')
        optimal_paras = {}
    else:
        #历史重演
        optimal_paras = bid_paras_optimization(join_log_files_name, lrCtrModel, bidModel, min_para, max_para, max_ecpc)
        if optimal_paras == {}:
            optimal_paras_str = ""
            bpo_logger.info('optimal setting result is emptry')
        else:
            for (camp_id, grp_id) in optimal_paras:
                tmp_para_str = '\t'.join([str(round(p, 6)) for p in bidModel[(camp_id, grp_id)].fixed_parameter]) + '\t' +  str(bidModel[(camp_id, grp_id)].auc)
                #threshold的结果中 参数顺序和其他策略不同，须特殊处理
                if optimal_paras[(camp_id,grp_id)] == [] or len(optimal_paras[(camp_id,grp_id)]) != 1:
                    continue
                if bid_strategy_type == 'threshold':
                    optimal_paras_str += '%s\t%s\t%s\t%s\n' % (grp_id, bid_strategy_type, tmp_para_str, round(optimal_paras[(camp_id, grp_id)][0], 6))
                else:
                    optimal_paras_str += '%s\t%s\t%s\t%s\n' % (grp_id, bid_strategy_type, round(optimal_paras[(camp_id, grp_id)][0], 6), tmp_para_str)
                optimal_strategy_str += '%s\t%s\n' % (grp_id,bid_strategy_type)
            #结果写入文件
            outfile = open(bidprice_out_file, 'w')
            outfile.write(optimal_paras_str)

            #outfile = open('/data/data_workspace/featonline/strategy/strategy_out_file','w')
            outfile = open(strategy_out_file,'w')
            outfile.write(optimal_strategy_str)
    bpo_logger.info('optimal setting result:%s' % optimal_paras_str)
    bpo_logger.info('optimal strategy result:%s' % optimal_strategy_str)

    end_time = time.clock()
    bpo_logger.info("bid_pars_optimization.py end. Total running  time:%f second", end_time - start_time)
    bpo_logger.info('************bid_paras_optimization.py end************')
    return optimal_paras

def get_latest_files(dir_name):
    '''
    对指定目录下文件按照时间进行倒排序，返回排序后文件列表
    :param dir_name: 指定目录名字
    '''
    file_time = {dir_name+"/"+f:os.path.getmtime(dir_name+"/"+f) for f in os.listdir(dir_name)}
    return sorted(file_time.keys(),key=lambda x:file_time[x],reverse=True)

def main_file(config_file):
    '''
    自动从配置文件中解析。
    '''
    global bpo_logger
    config=ConfigParser.ConfigParser()
    config.read(config_file)

    file_handler = logging.FileHandler(config.get('file','bpo_log_file'))
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    bpo_logger.addHandler(file_handler)

    strategy_type = config.get('optimization_paras','strategy_type')
    min_para=float(config.get('optimization_paras','min_para'))
    max_para=float(config.get('optimization_paras','max_para'))
    ctr_fw_dir= config.get('file','ctr_fw_dir')
    #jls_log_file= config.get('file','/home/chester/data/log')

    bidprice_out_file=config.get('file','bidprice_out_file')
    strategy_out_file=config.get('file','strategy_out_file')

    #adgroup_list: adgroup禁用列表
    adgroup_list_str=config.get('optimization_paras','adgroup_list')
    if adgroup_list_str == '':
        #相当于不做任何限制
        adgroup_list = []
    else:
        adgroup_list=config.get('optimization_paras','adgroup_list').split(',')
        
    auc_threshold = float(config.get('optimization_paras','auc_threshold'))

    try:
        (max_ecpc,cny_to_usd) = redis_parse.parse_adgroup_conf() #是一个字典
    except Exception,e:
        bpo_logger.info('\n************没有有效的campaign****************\n' +str(e))
        
    #max_ecpc = {'10694':0.5} #是一个字典

    join_log_dir=config.get('file','join_log_dir')
    join_log_time=int(config.get('file','join_log_time'))
    
    if max_ecpc == {}:
        bpo_logger.info('\n************没有有效的campaign****************\n')
        #提前退出
        sys.exit(2)
    auc = None #会自动会进行评估
    ctr_fw_file = get_latest_files(ctr_fw_dir)[0]
    join_log_files = [file_name for file_name in get_latest_files(join_log_dir)[0:200] if os.path.getmtime(file_name) > time.time()-join_log_time]
    if len(join_log_files) == 0:
        bpo_logger.info('\n************没有有效的join log_files文件****************\n')
        sys.exit(2)
    strategy_optimization("new",strategy_type, ctr_fw_file, join_log_files, adgroup_list, min_para, max_para, max_ecpc,auc,bidprice_out_file,strategy_out_file,auc_threshold)

if __name__ == '__main__':
    #test_instance = Test()
    #test_instance.test2014() #test_instance.test2015()

    #main_cmd()
    config_file=sys.argv[1]
    print config_file
    main_file(config_file)
