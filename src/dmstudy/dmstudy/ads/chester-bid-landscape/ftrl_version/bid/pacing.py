#coding:utf8
'''
该功能中所有统计都是以10min为单位
#凌晨启动初始化投放概率，10min.
'''

#
#campaign_id="10544"
#camp_info_str=os.popen('echo "get campaign_'+ campaign_id+'" | redis-cli -x').read()
#
#camp_info=json.loads(camp_info_str)
#print camp_info
##预算单位:人民币*10**6
#total_daily_budget = int(camp_info['dailyBudget'])/(10**6)


import os,time,csv
import util.event as event
import util.redis_parse as redis_parse
import util.stat as stat


def update_status(event_log_dir,done_filenames_file,status_file_name):
    '''
        更新状态文件
        状态文件记录了每个adgroup在每10分钟内event统计数据
        处理过的event日志，其文件名会加入到done_filenames_file中
    '''
    print event_log_dir,done_filenames_file,status_file_name
    #取得今天所有的event文件
    #today = time.strftime('%Y%m%d',time.localtime())
    today = time.strftime('%Y%m%d',time.localtime(time.time()-24*3600))
    today_filenames=os.popen('find %s -maxdepth 2 -name "*%s*" -type f' % (event_log_dir,today)).read().strip('\n').split('\n')
    #已读文件,内容为已读文件的全路径
    done_filenames = open(done_filenames_file).read().strip('\n').split('\n')
    #lambda函数:去除文件名的done_前缀
    remove_done=lambda f:os.path.dirname(f) + os.path.sep + os.path.basename(f).lstrip('done_')
    #两者做差集
    undone_filenames=[tmp_var for tmp_var in today_filenames if remove_done(tmp_var) not in done_filenames]
    #读取状态文件中的数据到 status_dict中
    status_dict= {}
    #time 201504200300 代表03:00-03:10
    fieldnames = ['campaign_id','adgroup_id','time','win','cost','impression','click','action']
    status_file=csv.DictReader(file(status_file_name,'rb'),delimiter=',',fieldnames=fieldnames)
    for line_dict in status_file:
        camp_grp = (line_dict['campaign_id'],line_dict['adgroup_id'])
        if not status_dict.has_key(camp_grp):
            status_dict[camp_grp] = {}
        #print 'time',line_dict['time']
        #print 'camp',(line_dict['campaign_id'],line_dict['adgroup_id'])
        #print 'fffff',[line_dict[field] for field in fieldnames[3:]]
        status_dict[camp_grp][line_dict['time']] = {'win':int(line_dict['win']),
            'cost':float(line_dict['cost']),
            'impression':int(line_dict['impression']),
            'click':int(line_dict['click']),
            'action':int(line_dict['action']),}
    #读入新文件，并更新状态字典为status_dict
    status_dict,status_dict_str = stat.event_file_stat(undone_filenames,status_dict)
    #更新已读文件列表到已读文件列表文件
    #去除done_开头
    undone_filenames = [remove_done(f) for f in undone_filenames]
    open(done_filenames_file,'a').write('\n'.join(undone_filenames)+'\n')
    #把新状态写入到状态文件
    tmp_handle = open(status_file_name,'w')
    tmp_handle.write(status_dict_str)


def get_time_section(adgroup_id):
    '''
    获取adgroup的投放时间段
    主要是为了计算剩余时间
    '''
    redis_parse.redis_parse()

def compute_prob(status_file_name, prob_file_name, traffic_rate_curve):
    '''
        根据花钱速度来控制response概率
    '''
    #total_budget = redis_parse.redis_parse('campaign','')
    #traffic_rate_curve 也以10分钟为单位
    traffic_rate_curve = {'0010':1,'0020':2,}

    #时间范围
    time_section_info = get_time_section()

    #日预算
    daily_budget = 

    #解析概率文件
    prob_file=csv.DictReader(file(prob_file_name,'rb'),delimiter=',',fieldnames=['minute_section','probability'])
    prob_dict = {}
    for line_dict in prob_file:
        prob_dict[line_dict['minute_section']] = line_dict['probability']

    status_file=csv.DictReader(file(status_file_name,'rb'),delimiter=',',fieldnames=fieldnames)
    cost_info = {}
    total_cost = {}
    prob_traffic = {}
    for line_dict in status_file:
        campaign_id = line_dict['campaign_id']
        adgroup_id = line_dict['adgroup_id']
        if not cost_info.has_key((campaign_id,adgroup_id)):
            cost_info[(campaign_id,adgroup_id)] = {'10min_num':0,'cost':0}
        cost_info[(campaign_id,adgroup_id)]['10min_num'] += 1
        cost_info[(campaign_id,adgroup_id)]['cost'] += float( line_dict['cost'] )
        minute_section = line_dict['time'][8:]
        prob_traffic[(campaign_id,adgroup_id)] += traffic_rate_curve[minute_section]*prob_dict[minute_section]


    now_10min = int(time.time()/(60*10))*60
    for camp_grp in cost_info:
        traffic_rate_curve[camp_grp]['end_time'] - now_10min 
        remaining_minute_sections = [time.strftime('%Y%m%d%H%M',time.localtime(now_10min + idx*60*10))  
            for idx in range(0,(time_section_info['end_time'] - now_10min)/(60*10))]
        remain_traffic=sum([traffic_rate_curve(tmp_section) for tmp_section in remaining_minute_sections])
        total_cost = cost_info[camp_grp]['cost']
        prob = prob_trafic * (daily_budget[camp_grp]-total_cost)/total_cost /  remain_traffic
        print prob

def compute_prob2(status_file_name):
    '''
        根据效果来投放,实时根据投放效果来计算概率
    '''


def compute_prob3(status_file_name):
    '''
        零点决策者， 从一天开始决定今天的投放时间，从效果角度来考虑问题
    '''

    
if __name__ == "__main__":
    event_log_dir= '/home/chester/KuaiPan/workspace/tukmob/resource'
    done_filenames_file = "/home/chester/KuaiPan/workspace/tukmob/resource/pacing_done_files"
    status_file = "/home/chester/KuaiPan/workspace/tukmob/resource/pacing_status"
    update_status(event_log_dir,done_filenames_file,status_file)


