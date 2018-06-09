# !/usr/bin/env python
# coding:utf-8
'''
点击的时间分布数据,这里是分时间段的点击量百分比,
按照一天为总时间，单个时间段长度即为 20小时/列表长度
example
global_click_time_distribution = [0.0417]*24
'''
import time

# global variable
tmp_dist = [0.0521, 0.0301, 0.0228, 0.0205, 0.0151, 0.004, 0.0093, 0.0138, 0.0328, 0.0345, 0.0443, 0.0521, 0.0636, 0.0596, 0.0364, 0.0384, 0.0384, 0.0419, 0.0485, 0.0543, 0.0504, 0.0797, 0.084, 0.0737]
global_click_time_distribution = [tmp_dist[idx / 2] / 2 for idx in range(0, 48)]
print global_click_time_distribution

def str2time(timestr):
    return time.mktime(time.strptime(timestr, '%Y%m%d %H:%M'))  # + 8*3600

def click_allocation_by_time(specified_time_range, time_ranges, total_intended_click):
    '''
    按照点击的时间分布数据以及期望达到的点击数在时间段内进行分配，并返回当前时间戳内分配的点击量
    即该函数应该每单位时间长度(半小时)被调用一次，重新计算。
    paras:
        specified_time_range: 当前时间戳
            如果为空，则返回time_ranges中第一个时间段的第一个半小时的分配点击量
            格式:[1418094000,1418115600]
        click_time_distribution:
            点击的时间分布数据,这里是分时间段的点击量百分比,
            按照一天为总时间，单个时间段长度即为 20小时/列表长度
            example
            click_time_distribution = [0.0417]*24
        time_ranges: 投放时间范围，每个range的时间范围必须为30分钟的倍数。
            格式:[[1418094000,1418115600],...]
        total_intended_click: 期望达到的点击数目
    return:
        返回
        intended_click
    '''
    click_time_distribution = global_click_time_distribution
    total_prop = 0
    for time_range in time_ranges:
        print get_half_hour_list(time_range)
        for time_idx in get_half_hour_list(time_range):
            total_prop += click_time_distribution[time_idx % 24]
    if specified_time_range == None:
        print 'asddfsdfsdfsd'
        return click_time_distribution[get_half_hour_list(time_ranges[0])[0]]
    if not reduce(lambda x, y:x or y, [specified_time_range[0] >= t[0] and specified_time_range[1] <= t[1] for t in time_ranges]):
        print 'specified time range is not included in all_time_ranges'
        raise ValueError
    specified_time_prop = sum([click_time_distribution[idx] for idx in get_half_hour_list(specified_time_range)])
    return int((float(specified_time_prop) / total_prop) * total_intended_click)

def get_half_hour_list(time_range):
    '''
    获取整数化的时间界限。
    paras:
        time_range:
            #格式:[1418094000,1418115600]
            [20141209 11:00,20141209 17:00]
            返回 range(23,35) #序号从0开始
    return:
        每个时间段的起始时间(按照半小时整数)
        range(start_hour,end_hour)
    '''
    # time_range[0]=time.mktime(time.strptime(time_range[0],'%Y%m%d %H:%M')) + 8*3600
    # time_range[1]=time.mktime(time.strptime(time_range[1],'%Y%m%d %H:%M')) + 8*3600
    m_time_range = [0, 0]
    m_time_range[0] = str2time(time_range[0])
    m_time_range[1] = str2time(time_range[1])
    if (int(m_time_range[1]) - int(m_time_range[0])) % 1800 != 0:
        print 'time range need to be in minimum unit of 30 minutes'
        raise ValueError
    start_remove_day = int(m_time_range[0]) % 86400
    end_remove_day = int(m_time_range[1]) - (int(m_time_range[0]) - start_remove_day)
    if (start_remove_day % 1800 != 0) or (end_remove_day % 1800 != 0):
        print 'time range starting and ending need to be in minimum unit of 30 minutes'
        raise ValueError
    start_time = start_remove_day / 1800
    end_time = end_remove_day / 1800
    if start_time >= end_time:
        print 'start time is later than end time'
        raise  ValueError
    return range(start_time, end_time)

def test():
    # click_time_distribution = [0.0417]*48
    # print get_half_hour_list(['20141209 11:00','20141209 17:00'])
    # print get_half_hour_list(['20141209 00:00','20141209 03:00'])
    # click_allocation_by_time(['20141209 11:00','20141209 15:00'],[['20141209 11:00','20141209 17:00'],['20141210 11:00','20141210 17:00']],5000)
    print click_allocation_by_time(['20141226 01:00', '20141226 01:30'], [['20141226 00:00', '20141227 00:00']], 1000)

if __name__ == '__main__':
    test()
    pass
