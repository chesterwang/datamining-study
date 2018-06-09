

import sys
sys.path.append('/home/chester/KuaiPan/workspace/tukmob')
import util.join as join
import matplotlib.pyplot as pp


dir_pre = '/home/chester/KuaiPan/workspace/tukmob/resource/join_log/join_log_april_adx/'

for adx_name in ["adiquity", "axonix", "doubleclick", "inmobi", "nexage", "smaato", "tapsense",]:
    parser = join.Parser()
    price_stat = {}
    for line in  open(dir_pre + '/' + 'join_log_april_1_' + adx_name,'r'):
        parser.feed(line)
        price = round(parser.get_all()['win_price'],2)
        if price not in price_stat:
            price_stat[price] = 0
        price_stat[price] += 1
    sorted_price_stat = sorted(price_stat)
    pp.clf()
    pp.plot(sorted_price_stat,[price_stat[price] for price in sorted_price_stat])
    pp.title("win_price_"+adx_name)
    pp.savefig('/home/chester/win_price_' + adx_name + ".png")

