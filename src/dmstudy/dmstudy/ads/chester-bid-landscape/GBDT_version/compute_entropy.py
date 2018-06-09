#!/usr/bin/env python
import sys,math


def compute_entropy(diff_val_count_list):
    '''
    compute entropy from a list of count of different value of feature
    '''
    total = sum(diff_val_count_list)
    prob_list = [float(c)/total for c in diff_val_count_list]
    #some probability value may be zero because of machine precision
    return sum([-p*math.log(p) if p != 0 else 0 for p in prob_list])

def compute_entropy_from_table(fields_name,target_name,file_name):
    '''
    compute entropy from table file
    '''
    #initialize
    field_dict={f:{} for f in fields_name}
    total_rows=0
    
    #statistics from stdin
    for line in open(file_name):
        total_rows+=1
        fields=line.strip('\n').split('\t')
        for idx in range(0,len(fields)):
            if not field_dict[fields_name[idx]].has_key(fields[idx]):
                field_dict[fields_name[idx]][fields[idx]] = 0
            field_dict[fields_name[idx]][fields[idx]] += 1
    
    #compute occurence count of other value
    #for k in field_dict:
    #    field_dict[k]['other'] =  total_rows-sum([field_dict[k][v] for v in field_dict[k]])
    
    #compute entropy
    feat_entropy = {}
    for key in field_dict:
        feat_entropy[key] =  compute_entropy(field_dict[key].values())
    print feat_entropy,feat_entropy
    return feat_entropy


def compute_cond_entropy_from_table(fields_name,target_name, file_name, feat_entropy):
    '''
    compute conditional entropy from table file
    '''
    #initialize
    joint_field_dict={}
    for i in range(0,len(fields_name)-1):
        for j in range(i+1,len(fields_name)):
            joint_field_dict[fields_name[i] + ',' + fields_name[j]]={}
    total_rows=0

    for line in open(file_name):
        total_rows+=1
        fields=line.strip('\n').split('\t')
        for idx in range(0,len(fields)-1):
            for idx2 in range(idx+1,len(fields)):
                comb_name = fields_name[idx] + ',' + fields_name[idx2]
                comb_val = fields[idx] + ',' + fields[idx2]
                if not joint_field_dict[comb_name].has_key(comb_val):
                    joint_field_dict[comb_name][comb_val] = 0
                joint_field_dict[comb_name][comb_val] += 1

    #compute entropy
    cond_feat_entropy = {}
    joint_feat_entropy = {}
    for comb_name in joint_field_dict:
        joint_feat_entropy[comb_name] =  compute_entropy(joint_field_dict[comb_name].values())
        x=comb_name.split(',')[0]
        y=comb_name.split(',')[1]
        #comb_name = x,y
        cond_feat_entropy[y+'|'+x] = round(joint_feat_entropy[comb_name] - feat_entropy[x],15)
        cond_feat_entropy[y+'|'+x] = 0 if abs(cond_feat_entropy[y+'|'+x]) < pow(10,-15) else cond_feat_entropy[y+'|'+x]
        cond_feat_entropy[x+'|'+y] = round(joint_feat_entropy[comb_name] - feat_entropy[y],15)
        cond_feat_entropy[x+'|'+y] = 0 if abs(cond_feat_entropy[x+'|'+y]) < pow(10,-15) else cond_feat_entropy[x+'|'+y]
    print cond_feat_entropy,cond_feat_entropy
    return cond_feat_entropy

def compute_su(entropy,cond_entropy):
    '''
    compute symmetry uncertaity
    '''
    cond_info_gain =  {} #
    result = {}
    for key in cond_entropy:
        #Info_Gain(X|Y) = entropy(X) - entropy(X|Y)
        (x,y)=key.split('|')
        cond_info_gain=entropy[x]-cond_entropy[x+'|'+y]
        if not result.has_key(x):
            result[x] = {}
        result[x][y] = 2*cond_info_gain/(entropy[x]+entropy[y]) if entropy[x]+entropy[y] != 0 else 0
        #result[x+','+y] = 2*cond_info_gain/(entropy[x]+entropy[y])
        result[x][y] = 0 if abs(result[x][y]) < pow(10,-15) else result[x][y]
        if not result.has_key(y):
            result[y] = {}
        result[y][x] = result[x][y]
    return  result

def compute_su_from_table(fields_name,target_name, file_name):
    '''
    compute symmetry uncertainty from table file
    '''
    feat_entropy=compute_entropy_from_table(fields_name,target_name, file_name)
    cond_feat_entropy=compute_cond_entropy_from_table(fields_name,target_name, file_name,feat_entropy)
    result_su=compute_su(feat_entropy,cond_feat_entropy)
    print '-------------'
    print 'req_imp_banner_w info'
    print 'entropy',feat_entropy['req_imp_banner_w']
    print 'target entropy',feat_entropy[target_name]
    print 'cond entropy over target',cond_feat_entropy['req_imp_banner_w|' + target_name]
    print 'su',result_su['req_imp_banner_w'][target_name]
    print '-------------'
    return result_su


def test_all():
    result = True
    result &= compute_entropy([1]) == 0
    file_name = '/data/data_workspace/tongpeng/features_table'
    fields_name = 'req_device_osv,req_app_cat,req_device_model,req_device_geo_country,req_user_gender,req_imp_displaymanager,req_device_connectiontype,req_imp_banner_h,req_imp_banner_w,req_banner_pos'.split(',')
    feat_entropy=compute_entropy_from_table(fields_name, file_name)
    cond_feat_entropy=compute_cond_entropy_from_table(fields_name, file_name,feat_entropy)
    for feat in feat_entropy:
        print feat,feat_entropy[feat]
    for comb_feat in cond_feat_entropy:
        print comb_feat,cond_feat_entropy[comb_feat]
    result_su=compute_su(feat_entropy,cond_feat_entropy)
    print result_su
    for comb_feat in result_su:
        print comb_feat,result_su[comb_feat]
    if result == True:
        print 'test pass'
    return result

#fields_name=sys.argv[1].split(',')
#file_name = ''
#compute_entropy(fields_name,file_name)
#compute_cond_entropy(fields_name,file_name)

if __name__ == "__main__":
    pass
    #file_name = '/data/data_workspace/tongpeng/features_table'
    #fields_name = 'req_device_osv,req_app_cat,req_device_model,req_device_geo_country,req_user_gender,req_imp_displaymanager,req_device_connectiontype,req_imp_banner_h,req_imp_banner_w,req_banner_pos,event_win_notice_price'.split(',')
    #target_name = 'event_win_notice_price'
    #print compute_su_from_table(fields_name,target_name,file_name)

