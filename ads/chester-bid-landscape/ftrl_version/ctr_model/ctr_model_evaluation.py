# !/usr/bin/env python
# coding:utf-8
'''
对于CTR点击率模型输出结果进行评估
评估标准为:RMSE,error rate, logloss,更多待添加(ROC,AUC,FP等)
输入格式要求:
    actual空格pred
其中, actual:真实的点击标记(1为正例，0为负例),#pred:预测的点击标记
'''
import os,sys,ctr_model,time
import util.join as join
from sklearn.metrics import  roc_auc_score  #计算MCC 只对二分类可以计算
from sklearn.metrics import  roc_curve  #计算MCC 只对二分类可以计算
from sklearn.metrics import auc 
from sklearn.metrics import confusion_matrix
from sklearn.metrics import log_loss


#结果输出目录,出价策略参数

def evalate_latest_log(file_dir, ctr_model_file_name):
    #过滤最近一个小时
    file_time = {file_dir+"/"+f:os.path.getmtime(file_dir+"/"+f) for f in os.listdir(file_dir) if os.path.getmtime(file_dir+"/"+f) >time.time()-3600}
    reversed_file_list = sorted(file_time.keys(),key=lambda x:file_time[x],reverse=True)
    the_ctr_model = ctr_model.LrCtrModel(ctr_model_file_name,'new')
    result_str = ctr_model_evaluation(reversed_file_list[0:5], the_ctr_model)
    if result_str != "":
        return ('\n'.join(reversed_file_list[0:5]) + '\n' ,ctr_model_evaluation(reversed_file_list[0:5], the_ctr_model))
    else:
        return "",""

def ctr_model_evaluation(input_files, the_ctr_model):
    actual_pred_list = predict_4_files(input_files, the_ctr_model)
    return predict_evaluation(actual_pred_list)

def predict_4_files(input_files, the_ctr_model):
    req_parser = join.Parser()
    actual_pred_list = []
    for input_file in input_files:
        for line in open(input_file):
            req_parser.feed(line)
            field_dict = req_parser.get_all()
            if field_dict == None:
                continue
            pctr = the_ctr_model.predict_ctr(field_dict['feature_values'])
            actual = 1 if field_dict['click_flag'] == True else 0
            actual_pred_list.append((actual,pctr))
    return actual_pred_list

def predict_evaluation(actual_pred_list):
    eval_str = ""
    if actual_pred_list == []:
        return eval_str
    actual_list, pred_list = zip(*actual_pred_list)
    actual_exception_num = sum([1 for val in actual_list if val not in (0,1)])
    pred_exception_num = sum([1 for val in pred_list if not (val >0 and val <1)])
    eval_str += 'total impression:%d\n' % len(actual_pred_list)
    eval_str += 'total click:%d\n' % sum(actual_list)
    eval_str += 'auc:%.4f\n' % roc_auc_score(actual_list,pred_list)
    eval_str += 'log_loss:%.4f\n' % log_loss(actual_list,pred_list)
    eval_dict = {'auc':roc_auc_score(actual_list,pred_list)}
    return eval_dict,eval_str

    #return log_loss(actual_list,pred_list)


    #(fpr,tpr,threshold)=roc_curve(actual_list, pred_list)
    #fpr_str = [str(round(f,5)) for f in fpr]
    #tpr_str = [str(round(f,5)) for f in tpr]
    #threshold_str = [str(round(f,5)) for f in threshold]
    #str_f = lambda x:str(x)
    #roc_str = ''
    #roc_str +=  '\t'.join(fpr_str) + '\n'
    #roc_str +=  '\t'.join(tpr_str) + '\n'
    #roc_str +=  '\t'.join(threshold_str) + '\n'
    #
    ##f = open(roc_outfile,'w')
    ##f.write(roc_str)
    #
    #cm =confusion_matrix(actual_list,[ 1 if p>0.5 else 0 for p in pred_list])
    ##sklear的auc
    ##eval_str +=  str(confusion_matrix(actual_list,[ 1 if p>0.5 else 0 for p in pred_list])) + '\n'
    ##eval_str +=  'sklearn计算auc %.10f\n' % auc(fpr,tpr)
    #eval_str += 'confusion matrix: %s\n' % str(cm)
    #cm_fraction = [[(col +0.0)/len(actual_list) for col in row] for row in cm] 
    #eval_str += 'confusion matrix: %s\n' % str(cm_fraction)
    ##open(evaluation_file,'w+').write(eval_str)

    #return roc_auc_score(actual_list,pred_list)
if __name__ == "__main__":
    file_list_str, eval_str=evalate_latest_log('/data/data_workspace/featonline/train','/data/data_workspace/featonline/base/wzn')
    if file_list_str == "" or eval_str == "":
        pass
    else:
        print 'evaluate file:\n' + file_list_str
        print 'evaluate result:\n' + eval_str
