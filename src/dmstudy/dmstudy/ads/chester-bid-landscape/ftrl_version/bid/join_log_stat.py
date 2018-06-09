# !/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
对于输入的price_clear文件的win price进行分campaign统计，并对统计曲线进行拟合
'''
import model_log

import util.join as join

# logger作为全局变量
#jls_logger = model_log.model_log('join_log_stat', '/data/online_join/bid_paras_optimization/bid_paras_optimization.log')
#jls_logger = model_log.model_log('join_log_stat', '/home/chester/data/log')

def join_log_stat(file_names, bin_num, fit_flag):
    ''' 
    file_name为clear_price文件,bin_num为价格分区间的数目
    fit_flag:是否拟合的标记
    return:
        stat_result[(camp_id,grp_id)] = {'impression':0,'click':0,'cost':0,
                'price_bin':{'bin_size':bin_size,'x':statx,'y':staty},
                'win_function_fitting':'fitting_para','filtered_xy'}
    '''
    #jls_logger.info('****************join_log_stat start*******************')
    stat_result = {}  # 格式{[cam id,grp id]:stat_result,[cam id,grp id]:}
    total_line_num = 0
    bad_line_count = 0
    req_parser = join.Parser()
    for file_name in file_names:
        for line in open(file_name):
            total_line_num += 1
            req_parser.feed(line)
            field_dict = req_parser.get_all()
            #field_dict = get_field_dict(line)
            if field_dict == None:
                bad_line_count += 1
                continue
            # 0 click,1campaign id,2adgroup id,3price
            camp_id = field_dict['campaign_id']
            grp_id = field_dict['adgroup_id']
            if not stat_result.has_key((camp_id, grp_id)):
                stat_result[(camp_id, grp_id)] = {'impression':0, 'click':0, 'cost':0, 'price_stat':{}}
            # impression stat
            stat_result[(camp_id, grp_id)]['impression'] += 1
            # price stat
            round_price = round(float(field_dict['win_price']), 4)
            if not stat_result[(camp_id, grp_id)]['price_stat'].has_key(round_price):
                stat_result[(camp_id, grp_id)]['price_stat'][round_price] = 0 
            stat_result[(camp_id, grp_id)]['price_stat'][round_price] += round_price
            # cost stat
            stat_result[(camp_id, grp_id)]['cost'] += 1
            # click stat
            if field_dict['click_flag'] == True:
                stat_result[(camp_id, grp_id)]['click'] += 1

    stats_str = ''
    stats_str += "bad_line_count:%d\n" % bad_line_count
    for (camp_id, grp_id) in stat_result.keys():
        stats_str += 'camp_id:%s,grp_id:%s,impression num:%s,click num:%s\n' % (camp_id, grp_id, stat_result[(camp_id, grp_id)]['impression'], stat_result[(camp_id, grp_id)]['click'])
    #jls_logger.info('log stat information:%s' % stats_str)
    # jls_logger.info('log_stat stats:\ntotal_line_num:%s,adgroup list:%s' % (total_line_num,stat_result.keys()))
    # if total_line_num < 10000:
    #    jls_logger.info('clear_price%s' % file_name)
    #    return None


    # 对价格进行分区
    if fit_flag == True:
        for (camp_id, grp_id) in stat_result.keys():
            # if (sum(stat_result[grp_id].values())+0.0)/total_line_num <0.1:
            #    continue
            print 'len(stat_result price stat)', len(stat_result[(camp_id, grp_id)]['price_stat'])
            max_price = max(stat_result[(camp_id, grp_id)]['price_stat'])
            min_price = min(stat_result[(camp_id, grp_id)]['price_stat'])
            bin_size = (max_price - min_price) / bin_num
            if bin_size == 0:
                stat_result[(camp_id, grp_id)]['price_bin'] = {'bin_size':bin_size, 'x':None, 'y':None}
                continue
            price_bin = [0] * bin_num
            for price in stat_result[(camp_id, grp_id)]['price_stat'].keys():
                bin_idx = int(round((price - min_price) / bin_size))
                bin_idx = bin_idx if bin_idx != bin_num else bin_idx - 1
                price_bin[bin_idx] += stat_result[(camp_id, grp_id)]['price_stat'][price]
            print 'price bin %d',price_bin
            total_imp = stat_result[(camp_id, grp_id)]['impression']
            #total_click = stat_result[(camp_id, grp_id)]['click']
            histogram = [float(price_bin[idx]) / total_imp for idx in range(0, bin_num)]
            # plot data
            print 'bin_size', bin_size
            # x为左端点,这里statx为所有闭区间的左端点以及最后一个右开区间的左端点
            statx = [ min_price + idx * bin_size for idx in range(0, bin_num + 1)]
            staty = map(lambda idx:sum(histogram[0:idx]), range(1, len(histogram) + 1))
            staty = [0] + staty
            #avg_ctr = float(total_click) / total_imp
            del stat_result[(camp_id, grp_id)]['price_stat']
            stat_result[(camp_id, grp_id)]['price_bin'] = {'bin_size':bin_size, 'x':statx, 'y':staty}
            # 'avg_ctr':avg_ctr,'total_click':total_click,'total_imp':total_imp}

        # fitting
        for (camp_id, grp_id) in stat_result.keys():
            fit_fun = lambda x, p:(p[0] + x) / (p[1] + x)
            # 待拟合的函数，x是变量，p是参数
            # (fitting_para,filtered_xy)= win_function_fitting('win_function_sample',fit_fun)
            if stat_result[(camp_id, grp_id)]['price_bin']['bin_size'] == 0:
                print 'bin size 0'
                continue
            #print 'stat result', len(stat_result[(camp_id, grp_id)]['price_bin']['x']), len(stat_result[(camp_id, grp_id)]['price_bin']['y'])
            #print stat_result[(camp_id, grp_id)]['price_bin']['x']
            #print stat_result[(camp_id, grp_id)]['price_bin']['y']
            (fitting_para, filtered_xy) = win_function_fitting(x=stat_result[(camp_id, grp_id)]['price_bin']['x'], y=stat_result[(camp_id, grp_id)]['price_bin']['y'], fit_fun=fit_fun)
            if fitting_para == None:
                stat_result[(camp_id, grp_id)]['win_function_fitting'] = None
                continue
            print 'c1', fitting_para[0], 'c2', fitting_para[1]
            # win_function_plot(filtered_xy[0],filtered_xy[1],fit_fun,fitting_para)
            stat_result[(camp_id, grp_id)]['win_function_fitting'] = {'fitting_para':fitting_para, 'filtered_xy':filtered_xy}
            #jls_logger.info('win function fitting by campaign and adgroup(%s,%s):%s' % (camp_id, grp_id, fitting_para))

    #print '\n'.join(['campaign,adgroup:'+str(camp_grp)+'\n'.join(stat_result.keys()) for camp_grp in stat_result])
    result_string = '\n'
    for camp_grp in stat_result:
        result_string += '*********************\n'
        result_string += 'files:' + ','.join(file_names) + '\n'
        result_string += 'camp_id:%s,adgroup_id:%s\n' % camp_grp
        for info in stat_result[camp_grp]:
            result_string += info + ':' +str(stat_result[camp_grp][info]) +'\n'
    #print '\n'.join(['campaign,adgroup:'+str(camp_grp)+'\n'.join[str(info) +':'+ str(stat_result[camp_grp][info]) for info in stat_result[camp_grp].keys()] for camp_grp in stat_result])
    #jls_logger.info('join_log_stat result:%s' % result_string)
    #jls_logger.info('****************join_log_stat end*******************')
    return stat_result

def win_function_fitting(x, y, fit_fun):
    '''
    file_name为win function统计结果，格式为:
        x1,x2,x3,...
        y1,y2,y3,...
    返回结果为:
        [拟合参数列表，过滤的xy]
        [fitting_para[0],fitting_para[1]],[filtered_x,filtered_y]
    '''
    if len(x) != len(y):
        None, None, None
    # 过滤是为了两端的数据大大影响拟合效果
    filtered_idx = filter(lambda idx:True if y[idx] > 0.01 and y[idx] < 0.99 else False, range(0, len(x)))
    if filtered_idx == None or filtered_idx == []:
        return None, None
    if filtered_idx[0] != 0:
        filtered_idx = [filtered_idx[0] - 1] + filtered_idx
    if filtered_idx[-1] != len(x) - 1:
        filtered_idx = filtered_idx + [filtered_idx[0] + 1]
    filtered_x = [x[idx] for idx in filtered_idx]
    filtered_y = [y[idx] for idx in filtered_idx]
    if len(set(filtered_y)) <= 1:  # 欠定问题
        return None, None
    
    # 待拟合的函数，x是变量，p是参数
    # fit_fun = lambda x,p:(p[0] + x) / (p[1] + x)
    # 计算真实数据和拟合数据之间的误差，p是待拟合的参数，x和y分别是对应的真实数据
    fit_err = lambda p, x, y:fit_fun(x, p) - y
    
    # 定义起始的参数 即从 y = 1*x+1 开始，其实这个值可以随便设，只不过会影响到找到最优解的时间
    p0 = [1, 1]  
    from scipy.optimize import leastsq
    (fitting_para, status) = leastsq(fit_err, p0, args=(filtered_x, filtered_y))
    return [fitting_para[0], fitting_para[1]], [filtered_x, filtered_y]
    
def win_function_plot(xs, ys, fit_fun, fitting_para):
    import matplotlib.pyplot as pp
    fit_ys = [fit_fun(x, fitting_para) for x in xs]
    pp.plot(xs, ys, '-r')
    pp.plot(xs, fit_ys, '-b')
    pp.legend(['stat', 'fiting'], loc='lower right')
    # pp.show()
    pp.savefig('fitting_plot.png')

if __name__ == "__main__":
    # import cProfile
    # cProfile.run('campaign_fitting("/data/data_workspace/tongpeng/clear_price1417067974.01.COMPLETED")')
    # campaign_fitting("/data/data_workspace/tongpeng/clear_price1417067974.01.COMPLETED")
    # campaign_fitting()
    pass
