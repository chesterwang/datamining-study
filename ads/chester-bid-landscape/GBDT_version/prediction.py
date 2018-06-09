#!/usr/bin/env python
#coding:utf-8

import TemplateSelection,sys,math,cPickle
#import matplotlib.pyplot as plt

import StarTree
import GBDT
import TemplateSelection

#假设样本是一个字典,例如{'co':3, 'ca':4, 'bid':5}

def decompose(sample,targeting_levels):
    '''样本分解
    sample: format [['500','400'],'iOS','*',...]
        sample targting
    target_profile: format [['500','400'],['iOS','android'],['2.1','3.5'],...]
        levels of targeting
    '''
    result=[[]]
    for idx in range(0,len(sample)):
        if type(sample[idx]) == type([]):
            if True != reduce(lambda x,y:x&y,[val in targeting_levels[idx] for val in sample[idx]]):
                print 'value not in preseted dictionary'
                #raise ValueError 这里不抛出异常，因为StarTree和GBDT决策树都可以处理未知值。
            result = [[rs + [val] for rs in result] for val in sample[idx]]
            result = reduce(lambda x,y:x+y, result)
        #elif sample[idx] == '*':
        #    result = [[rs + [val] for rs in result] for val in targeting_levels[idx]]
        #    result = reduce(lambda x,y:x+y, result)
        else:
            if sample[idx] not in targeting_levels[idx]:
                #print '----------------'
                #print sample[idx]
                #print targeting_levels[idx]
                #print 'value not in preseted dictionary'
                #raise ValueError 
                result = [[rs + ['*'] for rs in result] for rs in result]
            #result = [rs + ['*'] for rs in result] + [rs + [sample[idx]] for rs in result]
            else:
                result = [rs + [sample[idx]] for rs in result]
    return result

def finite_mixture_model(fined_predictions, function_type):
    '''
    function_type: 0 pdf, 1 cdf
    note:
        mu and sigma is not mean and variance.
    return:
        plotxy:[plotx,ploty]
    '''
    #假设每个prediction都包含了均值和方差, mean variance
    #利用含变量的lambda表达式的自动变化特性
    mu = lambda :math.log(mean) - math.log(1+var/(mean**2))/2
    sigma2 = lambda :math.log(1+var/(mean**2))

    if function_type == 0:
        log_normal = lambda x:math.exp( -(math.log(x) - mu())**2/(2*sigma2()))/(x*math.sqrt(sigma2())*math.sqrt(2*math.pi))
    else:
        log_normal = lambda x:(1+math.erf((math.log(x) - mu())/(math.sqrt(sigma2()*2))))/2
    fined_prediction_tuple=[(fp['prior'], fp['mean'], fp['var']) for fp in fined_predictions]
    plotxy = [[0.01*i for i in range(1,101)]]
    #for x in plotxy[0]:
    #    #[prior*log_normal(x) for (prior,mean,var) in fined_prediction_tuple]
    #    for (prior,mean,var) in fined_prediction_tuple:
    #        print prior,mean,var,mu(),sigma2()
    plotxy.append([sum([prior*log_normal(x) for (prior,mean,var) in fined_prediction_tuple]) for x in plotxy[0]])
    return plotxy

def load_model(star_tree_file,template_list_file,GBDT_mean_file,GBDT_var_file):
    '''
    载入各种数据结构和模型
    '''

    #载入star_tree结构
    in_file=open(star_tree_file,'r')
    star_tree = cPickle.load(in_file)
    in_file.close()

    #载入template_list结构
    in_file=open(template_list_file,'r')
    template_list = cPickle.load(in_file)
    in_file.close()

    #载入GBDT mean模型
    in_file = open(GBDT_mean_file,'r')
    mean_model  = cPickle.load(in_file)
    in_file.close()
    #载入GBDT var模型
    in_file = open(GBDT_var_file,'r')
    var_model  = cPickle.load(in_file)
    in_file.close()

    return (star_tree,template_list,mean_model,var_model)

def sample_predict(sample,targeting_levels,startree_pickle,templates_pickle,GBDT_mean_pickle,GBDT_var_pickle):
    '''sample: format [['500','400'],'iOS','*',...]
    return:
        (is_success,mean,var,[plotx,ploty])
        is_success: True or False
        mean: mean produced by prediciton model
        var: var produced by prediction model
        plotx: list of x axis values
        ploty: list of y axis values
    '''
    (star_tree,template_list,mean_model,var_model) = load_model(startree_pickle,templates_pickle,GBDT_mean_pickle,GBDT_var_pickle)

    prediction = []#包含均值 方差 以及先验概率
    (is_query, result,similar_template,similar_path)=star_tree.query_by_template(template_list, sample)
    if is_query is True:
        similar_mean = float(result['sum'])/result['count']
        pred_mean = mean_model.get_prediction(sample + [similar_mean])
        similar_var = float(result['sq_sum'])/result['count'] - similar_mean**2
        pred_var = var_model.get_prediction(sample + [similar_var])
        pred_var = pred_var if pred_var > 10e-8 else 10e-8
        prediction.append({'count':float(result['count']),'mean':pred_mean,'var':pred_var})
        prediction[-1]['prior']=1
        plotxy = finite_mixture_model(prediction,1)
        #print 'sample predict process',similar_mean,similar_var,pred_mean,pred_var
        return (True,pred_mean,pred_var,plotxy)
    else:
        return (False,None,None,None)

def campaign_predict(campaign,targeting_levels,startree_pickle,templates_pickle,GBDT_mean_pickle,GBDT_var_pickle):
    '''campaign: format [['500','400'],'iOS','*',...]
    return:
        (is_success,[plotx,ploty])
        is_success: True or False
        plotx: list of x axis values
        ploty: list of y axis values
    '''

    #(star_tree,template_list,mean_model,var_model) = load_model('./StarTree.pickle','template_list.pickle','AdditiveRegressionTrees_mean.pickle','AdditiveRegressionTrees_var.pickle')
    (star_tree,template_list,mean_model,var_model) = load_model(startree_pickle,templates_pickle,GBDT_mean_pickle,GBDT_var_pickle)

    fined_samples = decompose(campaign,targeting_levels)
    fined_predictions = []#包含均值 方差 以及先验概率
    for fined_sample in fined_samples:
        #print  'fined samle',fined_sample,
        (is_query, result,similar_template,similar_path)=star_tree.query_by_template(template_list, fined_sample)
        if is_query is True:
            #prediction
            similar_mean = float(result['sum'])/result['count']
            #print 'fined_sample',fined_sample
            #print 'similar template',similar_template.value_list
            #print 'similar mean',similar_mean
            #print 'similar path',similar_path
            pred_mean = mean_model.get_prediction(fined_sample + [similar_mean])
            #print pred_mean,
            similar_var = float(result['sq_sum'])/result['count'] - similar_mean**2
            pred_var = var_model.get_prediction(fined_sample + [similar_var])
            pred_var = pred_var if pred_var > 10e-8 else 10e-8
            #print pred_var
            #prediction
            fined_predictions.append({'count':float(result['count']),'mean':pred_mean,'var':pred_var})
    if fined_predictions != []:
        total_number = sum([ p['count'] for p in fined_predictions])
        for p in fined_predictions:
            p['prior'] = p['count']/total_number
        plotxy = finite_mixture_model(fined_predictions,1)
        return (True,plotxy)
    else:
        return (False,None)

            
if __name__ == "__main__":
    pass
    #test(targeting_levels)

    #batch_predict(samples,targeting_levels):
