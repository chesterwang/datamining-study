

log_f = open('/data/data_workspace/click.data')

log_f_1 = open('/data/data_workspace/tongpeng/click.data27','w')
log_f_2 = open('/data/data_workspace/tongpeng/click.data28','w')
log_f_3 = open('/data/data_workspace/tongpeng/click.data29','w')

field_name= 'event_win_notice_ts:'
for  line in log_f:
    line_array=line.split('|')
    for l in line_array:
        if l.startswith(field_name):
            str_ts = l[len(field_name):]
            if str_ts == '':
                continue
            imp_ts=int(str_ts)
            if imp_ts < 1409155200:
                log_f_1.write(line)
            elif imp_ts > 1409155200 and imp_ts < 1409241600:
                log_f_2.write(line)
            elif imp_ts > 1409241600:
                log_f_3.write(line)
            continue
log_f.close()
log_f_1.close()
log_f_2.close()
log_f_3.close()
