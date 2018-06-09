#!/usr/bin/env python
#coding:utf-8

import sys,cPickle
#import StarTree

from StarTree import *
from TemplateSelection import *

class Validator:
    '''校验器
    '''
    def __init__(self, count_threshold, var_threshold):
        self.count_threshold = count_threshold
        self.var_threshold = var_threshold
    def validate(self, count, var):
        '''对于样本的数量和方差进行判断
        如果数量小于阈值，则不将这个样本作为GBDT训练样本
        数量少或者方差小，在预测分布时，都会很不准确
        '''
        count_threshold = 2
        var_threshold = 10e-5
        if count < self.count_threshold or var < self.var_threshold:
            return False #校验不通过
        else:
            return True #校验通过

def generate(startree_pickle,templates_pickle,file_name,stat_type,count_threshold,var_threshold,out_file_name):
    validator = Validator( count_threshold, var_threshold)
    if stat_type not in ('mean','var'):
        raise ValueError

    out_file = open(out_file_name,'w')
    #载入star_tree结构
    #in_file=open('StarTree.pickle','r')
    in_file=open(startree_pickle,'r')
    star_tree = cPickle.load(in_file)
    #star_tree.tree(star_tree.root,'|')
    in_file.close()
    
    #from TemplateSelection import *
    #载入template_list结构
    #in_file=open('template_list.pickle','r')
    in_file=open(templates_pickle,'r')
    template_list = cPickle.load(in_file)
    in_file.close()
    
    for line in open(file_name):
        line=line.strip('\n')
        line_array = line.split('\t')
        sample = line_array[0:-3]
        count = line_array[-3]
        old_sum = line_array[-2]
        sq_sum = line_array[-1]
        count = int(count)
        #mean = float(old_sum)/count
        #variance = float(sq_sum)/count - mean**2
        #for fined_sample in fined_samples:
        (is_query, result, similar_template, similar_path) = star_tree.query_by_template(template_list, sample)
        if is_query is True:
            #检索出similar path的统计量
            similar_count = result['count'] 
            similar_sum = result['sum'] 
            similar_sq_sum = result['sq_sum'] 

            mean = float(old_sum)/count
            similar_mean = float(similar_sum)/similar_count
            var = float(sq_sum)/count - mean**2
            similar_var = float(similar_sq_sum)/similar_count - similar_mean**2
            #if not validator.validate(count, var):
            #    #count = validator.count_threshold
            #    var = validator.var_threshold
            #if not validator.validate(count, var):
            #    similar_var = validator.var_threshold
            if stat_type == 'mean':
                out_file.write('%s\t%s\t%s\t%s\n' %('|'.join(sample),similar_mean,mean,count))
                #print '%s\t%s\t%s\t%s' %('|'.join(sample),similar_mean,mean,count)
            elif stat_type == 'var':
                out_file.write('%s\t%s\t%s\t%s\n' %('|'.join(sample),similar_var,var,count))
                #print '%s\t%s\t%s\t%s' %('|'.join(sample),similar_var,var,count)

if __name__=='__main__':
    pass
