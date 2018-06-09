#!/usr/bin/env python
#coding:utf-8

def extract(file_name,feat_idx,outfile_name):
    '''
    feat_idx:
        the last value if target index
    return:

    '''
    outfile=open(outfile_name,'w')
    result = {} #result = {'a\tb':[count,old_sum,sq_sum]}
    target_val_except_num = 0
    for line in open(file_name):
        vals=line.strip('\n').split('\t')
        #outfile.write('\t'.join([vals[idx] for idx in range(0,len(feat_idx))]))
        #selected_vals = '\t'.join([vals[idx] for idx in feat_idx[0:-1]])
        selected_vals = '\t'.join([vals[idx] for idx in feat_idx])
        try:
            target_vals = float(vals[-1])
        except ValueError as err:
            target_val_except_num += 1
        if not result.has_key(selected_vals):
            result[selected_vals] = [0,0,0]
        result[selected_vals][0] += 1 #count
        result[selected_vals][1] += target_vals #sum
        result[selected_vals][2] += target_vals**2 #squared sum
    for key in result:
        #此处精度一定要控制好，如果精度不够，则后续程序计算方差就会出现负值
        outfile.write('%s\t%d\t%f\t%f\n' % (key, result[key][0],result[key][1],result[key][2]))
    print 'the number of except target value is %d' % target_val_except_num
    target_keys = [k.split('\t') for k in result.keys()]
    #print target_keys
    #print feat_idx
    # 每个特征的取值
    print '每个特征的取值',[set([k[idx] for k in target_keys]) for idx in range(0,len(feat_idx))]
    return [set([k[idx] for k in target_keys]) for idx in range(0,len(feat_idx))]

if __name__ == "__main__":
    pass
