#!/usr/bin/env python
#coding:utf-8

#this algorithm is used to implement template selection algorithm
import sys,cPickle
import StarTree

class Template:
    # query template
    def __init__(self, value_list, quality_score, coverage_score):
        #template is a list , whose vlaues only includ * and v
        value_check = [ True if t in ('*','v') else False for t in value_list]
        if reduce(lambda x, y:x&y, value_check):
            self.value_list = value_list
            self.quality_score = quality_score
            self.coverage_score = coverage_score
        else:
            raise NameError(), ('template is a list ,'
                'whose vlaues only includes * and v')
    #def setQualityScore(self,quality_score):
    #    self.quality_score = quality_score
    #quality_score
    def mask_path(self, path):
        if len(self.value_list) == len(path):
            return [ '*' if self.value_list[i] == '*' else path[i] 
                for i in range(0, len(path))]

def get_template_list(number_dimension):
    template_list = []
    for i in range(0, 2**number_dimension ):
        template = Template(['*']*number_dimension,0,0)
        for j in range(0, number_dimension):
            template.value_list[j] = '*' if i & 2**j == 0 else 'v'
        template_list.append(template)
    return template_list

def delta(value1, value2):
    return 1 if value1 == value2 else 0

def cal_quality_score(template, feature_weight):
    if (isinstance(template, Template) and
        len(template.value_list) == len(feature_weight)):
        return sum([t[1]*( 1 if t[0] == 'v' else 0) 
            for t in zip(template.value_list, feature_weight)])
    else:
        raise NameError, 'sss'

def template_list_initialize(number_dimension, feature_weight):
    # train template
    #impressions = [ s[impression_col] for s in training_samples]
    #number_dimension = len(training_samples[0]) - 1 # subtract impression_col
    #quality_score = [0]*number_dimension
    template_list = get_template_list(number_dimension)
    for template in template_list:
        template.quality_score = cal_quality_score(template, feature_weight)
        template.coverage_score =  0
    template_list = sorted(template_list,
        key=lambda x:x.quality_score, reverse=True)
    return template_list

def template_list_train(template_list, sample, sample_count, star_tree):
    i = 0
    while not star_tree.query( template_list[i].mask_path(sample)):
        if i < len(template_list) - 1:
            i += 1
        else:
            break
            #raise NameError,'asdf'
    template_list[i].coverage_score += sample_count #必须减1
    return template_list

def template_list_sort(template_list,number_template,number_dimension):
    #template_list = sorted(template_list,
    template_list.sort(key=lambda x:x.coverage_score, reverse=True)
    #return template_list
    #template_list = template_list[0:number_template]
    del(template_list[number_template:])
    all_star_template = ['*']*number_dimension
    if not reduce(lambda x, y:x&y, 
            [t.value_list == all_star_template for t in template_list]):
        template_list[-1] = Template(all_star_template,0,0)
    return template_list
def template_select(file_name,StarTree_pickle,ordered_selected_feat,selected_feat,number_template,template_list_pickle,log_path):
    #print cal_quality_score(Template(['*','v','*']),[1,2,1])

    #(StarTree_pickle,feature_info,number_template,log_path)=sys.argv[1:]
    #feature_info = [ info.split(',') for info in feature_info.split('|')]
    feature_su = [selected_feat[feat] for feat in ordered_selected_feat]
    feature_weight =  feature_su #用SU度量来代表权重
    number_dimension = len(ordered_selected_feat)
    star_tree = cPickle.load(open(StarTree_pickle,'r'))
    number_template = int(number_template)
    
    #默认权重均为1
    #feature_weight=[1,1]
    result_template_list = template_list_initialize(number_dimension, feature_weight)
    
    for line in open(file_name):
        sample=line.split('\t')[0:-3]
        sample_count=int(line.split('\t')[-3])
        result_template_list = template_list_train(result_template_list, sample, sample_count, star_tree)

    result_template_list = template_list_sort(result_template_list,number_template,number_dimension)

    print result_template_list[0].value_list, result_template_list[0].quality_score
    print result_template_list[1].value_list, result_template_list[1].quality_score

    log_text = '--------StarTree 查询模板训练结果为:---------\n'
    log_text += '\n'.join([ 'template ' + str(l.value_list) + '\t quality_score ' + str(l.quality_score) + 
        '\tcoverage_score ' + str(l.coverage_score) 
        for l in result_template_list])
    log_text += '\n'
    log_file = open(log_path,'a')
    log_file.write(log_text)
    log_file.close()

    #存储template结构
    f_template_list=open(template_list_pickle,'w')
    cPickle.dump(result_template_list,f_template_list)
    f_template_list.close()
    
if __name__ == '__main__':
    #print cal_quality_score(Template(['*','v','*']),[1,2,1])
    pass
