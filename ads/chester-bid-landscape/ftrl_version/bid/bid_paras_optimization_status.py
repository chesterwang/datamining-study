#coding:utf8

import os,sys,ConfigParser,json

def bid_paras_optimization_status_update(config_file):
    '''
        对优化状态文件进行更新
        该文件保存着每个campaign的 1. 优化步长，2.上次优化结果所使用的ecpc. 3. 目标ecpc。
        这里仅仅更新3.目标ecpc
        而1.步长 2.上次优化结果所使用ecpc需要在优化过程完全结束之后进行更新
        文件内容举例
        [10700]
        step_size=1
        target_ecpc=3
        last_middle_ecpc=3
        [10700]
        step_size=4
        target_ecpc=888
        last_middle_ecpc=888
    '''
    config=ConfigParser.ConfigParser()
    
    if not os.path.exists(config_file):
        raise NameError("status file not exists")
    else:
        config.read(config_file)
    
    #这里section是指camp id，并且必须是ecpc出价
    max_ecpc_info = {}
    all_campaign_str = os.popen( "echo lrange all_campaign_ids 0 -1 | `which redis-cli` -x" ).read()
    
    if all_campaign_str == '' or all_campaign_str == '\n':
        raise NameError('没有有效(活着)的campaign')
    else:
        max_ecpc_info_str = ''
        for line in all_campaign_str.split('\n'):
            tmp_camp = line.strip('\n')
            if tmp_camp == "":
                continue
            camp_info_str=os.popen( "echo get campaign_" + tmp_camp + " | `which redis-cli` -x" ).read()
            camp_info_str = camp_info_str.split('\n')[0]
            camp_info=json.loads(camp_info_str)
            #仅仅对动态出价进行记录
            if camp_info['dealMethod'] == 1 and camp_info['settleMethod'] == 1:
                max_ecpc_info[tmp_camp] = float(camp_info['settlePrice'])
            #max_ecpc_info[tmp_camp] = float(camp_info['settlePrice'])
    #对campaign 进行更新，包括step_size和ecpc
    #ecpc信息仅仅用于比对，如果新的ecpc和旧的ecpc不同，则重置step_size为0.
    #last_middle_ecpc 为上次历史重演结果中优化参数所对应的ecpc数值
    for camp_id in max_ecpc_info:
        if camp_id not in config.sections():
            config.add_section(camp_id)
            config.set(camp_id,'step_size',value=0)
            #target_ecpc记录原始单位,人民币
            config.set(camp_id,'target_ecpc',value=max_ecpc_info[camp_id])
            #last_middle_ecpc记录单位美元
            config.set(camp_id,'last_middle_ecpc',value=max_ecpc_info[camp_id])
        elif (not config.has_option(camp_id,'target_ecpc')) or float(config.get(camp_id,'target_ecpc')) !=  max_ecpc_info[camp_id]:
            config.set(camp_id,'step_size',value=0)
            config.set(camp_id,'target_ecpc',value=max_ecpc_info[camp_id])
            config.set(camp_id,'last_middle_ecpc',value=max_ecpc_info[camp_id])
        else:
            pass
            #step_size 增加 应该在历史重演结束之后
        config.set(camp_id,'target_ecpc',value=float(max_ecpc_info[camp_id]))
    
    #去除已经停掉的campaign
    for camp_id in  config.sections():
        if camp_id not in max_ecpc_info:
            config.remove_section(camp_id)
    config.write(open(config_file,'w'))
    
if __name__ == "__name__":
    config_file=sys.argv[1]
    bid_paras_optimization_status_update(config_file)





