import sys
import matplotlib.pyplot as pp

def perf_plot(perf_array,title):
    print perf_array
    para,click,imp,cost,cpc,ctr,avg_pctr,cpm=zip(*perf_array)
    pp.plot(para,cpc)
    pp.xlim(0,0.3)
    pp.ylim(0,0.08)
    pp.title(title)
    pp.show()

log_file = "/home/chester/data/log"

file_handle = open(log_file)

last_pos = None
while True:
    line  = file_handle.readline()
    if line == '':
        break
    #if "************parameter performance start************" in prev_pos:
    if "*************test_with_strategy start****************" in line:
    #if "bid_paras_optimization.py start" in line:
        last_pos = file_handle.tell()

if last_pos == None:
    sys.exit(2)

file_handle.seek(last_pos)
perf_flag = 0
data_flag = 0
title=''

start_str ="************parameter performance start************"
end_str = "************parameter performance end************"

while True:
    line = file_handle.readline()
    if line == '': #eof
        break
    line = line.rstrip('\n')
    if line == None or line == '':
        continue
    if start_str in line:
        perf_flag = 1
    if end_str in line:
        data_flag = 0
        perf_flag = 0
        perf_plot(perf_array,title)
        title = ''
    if data_flag == 1:
        perf_array.append(line.split(' '))
    if perf_flag == 1 and 'bid_history_files' in line:
        title = str([file_name.split('/')[-1] for file_name in line.split(':')[-1].split(',')])
        print title
    if perf_flag == 1 and 'unit: US dollar' in line:
        data_flag = 1
        perf_array = []
        



