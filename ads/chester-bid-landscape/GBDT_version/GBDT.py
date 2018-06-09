#!/usr/bin/env python
#coding:utf-8
'''
Gradient Tree Boosting Algorithm
T. Hastie, R. Tibshirani, and J. H. Friedman. Chapter 10. 
boosting and additive trees.  
In The elements of statistical learning: 
data mining, inference, and prediction, 
pages 337–384. New York: Springer, 2009.
实现细节在P361页
由于目标是连续变量，所以这里使用最小平方残差作为评判标准
这里算法没有使用count，以后可以考虑这个作为样本的权重
'''

import sys, copy, cPickle

class Stump:
    '''单个决策树,这里默认深度为1，即只有一个决策点。
    '''
    def __init__(self, root_branch):
        '''
        参数介绍:
        root_branch: 决策树根节点上的分支
        这里只考虑二叉.
        '''
        self.root_branch = root_branch

    def get_prediction(self, case):
        '''在决策树上进行预测
        参数说明:
        case = [attrs_values,...,target_value]
        '''
        if case == None:
            return None
        else:
            cur_branch = self.root_branch
            #print '-----'
            while True:
                #print cur_branch
                left_or_right = cur_branch.select(case)
                #print left_or_right
                if left_or_right == 0:
                    if cur_branch.left_child_branch == None:
                        return cur_branch.left_prediction
                    cur_branch = cur_branch.left_child_branch
                elif left_or_right == 1:
                    if cur_branch.right_child_branch == None:
                        return cur_branch.right_prediction
                    cur_branch = cur_branch.right_child_branch
                else:
                    raise ValueError
                
            #while not cur_branch.is_terminal():
            #    print 'none branch' if cur_branch==None else 'not none'
            #    cur_branch = cur_branch.get_child_branch(case)
            #return cur_branch.get_prediction(case)
    def recurse(self, f, g, h):
        '''递归代码函数
        f 函数为Branch的函数
        recurse_type:内点使用函数f, 终点使用函数g,，半终点使用h
        f g为None，表示不调用
        '''
        recurse_result = []
        if type(f) !=  type(lambda :1):
            return None
        stack = []
        stack.append(self.root_branch)
        while len(stack) != 0:
            cur_branch = stack[-1]
            del stack[-1]
            if cur_branch.is_terminal():
                if g != None:
               	    recurse_result.append(g(cur_branch))
            elif cur_branch.is_mix_terminal():
                if  h != None:
               	    recurse_result.append(h(cur_branch))
                if cur_branch.left_child_branch != None:
                    stack.append(cur_branch.left_child_branch)
                elif cur_branch.right_child_branch != None:
                    stack.append(cur_branch.right_child_branch)
            else:
                if f != None:
                    recurse_result.append(f(cur_branch))
                stack.append(cur_branch.left_child_branch)
                stack.append(cur_branch.right_child_branch)
        return recurse_result

class Branch:
    '''树中的单个分支图
    包含分支属性attr_idx、属性类型attr_type、属性如何分裂的方法split、各个分支的预测值
    '''
    def __init__(self, attr_idx, attr_type, split, left_sample_number, right_sample_number, left_prediction, right_prediction ):
        '''
        参数介绍:
        attr_idx:属性的索引,从0开始
        split: 拆分，参考call_all_split函数
        这里只考虑二叉.
        left_prediction: 左子树的预测值
        right_prediction: 右子树的预测值
        '''
        self.attr_idx = attr_idx
        self.attr_type = attr_type
        self.split = split
        self.left_sample_number = left_sample_number
        self.right_sample_number = right_sample_number
        self.left_prediction = left_prediction
        self.right_prediction = right_prediction
        self.left_child_branch = None
        self.right_child_branch = None
    def is_terminal(self):
        '''
        判断是否终端节点
        '''
        if self.left_child_branch == None and self.right_child_branch == None:
            return True
        else:
            return False
    def is_mix_terminal(self):
        '''
        判断是否半终端节点,即两个分支中只有一个可以继续分支,另一个是预测值
        '''
        if ((self.left_child_branch == None and self.right_child_branch != None) or
            (self.left_child_branch != None and self.right_child_branch == None)):
            return True
        else:
            return False
    def select(self, case):
        '''根据新的数据选择走哪个分支 参数说明:
        case = [attrs_values,...,target_value]
        return: 0左子树 1右子树
        '''
        #print self.attr_idx,case
        #print self.split.split_rule
        return self.split.select(case[self.attr_idx])
    def get_prediction(self, case):
        '''如果该分支是终端分支，则预测,即子树均为空
        参数说明:
        case = [attrs_values,...,target_value]
        '''
        if self.is_terminal() == True:
            #终端节点，可以预测
            child_flag = self.select(case)
            if child_flag == 0:
                return self.left_prediction
            elif child_flag == 1:
                return self.right_prediction
    def get_child_branch(self, case):
        '''根据新的数据选择走哪个分支
        参数说明:
        case = [attrs_values,...,target_value]
        '''
        if self.is_terminal() == False:
            child_flag = self.select(case)
            if child_flag == 0:
                return self.left_child_branch
            elif child_flag == 1:
                return self.right_child_branch

class Split:
    '''属性拆分类,包含要拆分属性的类型，以及拆分规则
    '''
    def __init__(self, attr_type, split_rule):
        '''attr_type属性类型
        attr_type=0连续或者定距变量,这时split_rule为一个数值
        attr_type=1名义变量,这时split_rule为一个由两个列表组成的列表,
        第一个列表表示属于左子节点，第二个列表表示属于右子节点。
        '''
        self.attr_type = attr_type
        self.split_rule = split_rule
    def select(self, attr_level):
        '''根据新的数据选择走哪个集合
        参数说明:
        case = [attrs_values,...,target_value]
        return: 0左子树 1右子树
        '''
        if self.attr_type == 0:
            return 0 if  attr_level < self.split_rule else 1
        elif self.attr_type == 1:
            if attr_level in self.split_rule[0]:
                return 0
            elif attr_level in self.split_rule[1]:
                return 1
            else:
                #既不在左子树，也不在右子树，则视其为未知值,从而匹配*
                if '*' in self.split_rule[0]:
                    return 0
                elif '*' in self.split_rule[1]:
                    return 1
                else:
                    #print attr_level
                    #print self.split_rule
                    print 'value not found either in left split or in right split'
                    raise ValueError

class AdditiveRegressionTrees:
    ''' 可加性回归树
    '''
    def __init__(self, target_mean):
        self.target_mean = target_mean
        self.stump_list = []
    def append(self, stump):
        '''添加一棵树
        '''
        self.stump_list.append(stump)
    def get_prediction(self, case):# 是否需要修改添加更多信息
        '''在可加性回归树模型上进行预测
        参数说明:
        case = [attrs_values,...,target_value]
        '''
        prediction = self.target_mean
        if not len(self.stump_list) == 0:
            for stump in self.stump_list:
                #print 'tree'
                prediction += stump.get_prediction(case) 
        else:
            return None
        return prediction
    def get_stump_list(self):
        '''返回树列表
        '''
        return self.stump_list
    def recurse_all_stumps(self, f, g, h):
        '''递归代码函数
        recurse_type:0非终点使用函数f，终点使用函数g
        '''
        result = []
        for stump in self.stump_list:
            result.append(['\n/*new tree*/\n'])
            result.append(stump.recurse(f, g, h))
        return result
    def cal_relative_sq_error(self, data):
        '''
        '''
        total_count = sum([d[1] for d in data ])
        if len(data) != 0:
            weighted_relative_error = 0
            rmsre = 0 #weighted root-mean-squared relative error(RMSRE)
            for d in data:
                pred_value = self.get_prediction(d[0])
                rmsre += (float(d[1])/total_count)*((d[0][-1]-pred_value)/d[0][-1])**2
            return rmsre
        else:
            return None
    def cal_sq_error(self, data):
        '''
        '''
        total_count = sum([d[1] for d in data ])
        if len(data) != 0:
            weighted_relative_error = 0
            rmsre = 0 #weighted root-mean-squared relative error(RMSRE)
            for d in data:
                pred_value = self.get_prediction(d[0])
                rmsre += (float(d[1])/total_count)*(d[0][-1]-pred_value)**2
            return rmsre
        else:
            return None
        


def cal_all_split(attr_data, attr_type):#
    '''这里只进行二叉分类。
    处理方法:
    对于连续变量，计算所有拆分值: 左子树小于拆分值，右子树大于拆分值
    应该考虑更进一步的优化，包括优化拆分值的数量。
    但是定居变量没有实现，如果要实现，需要指定一个序函数。
    对于离散变量，计算所有拆分集。这里将属性值集合拆分为两个集合。
    结果results为一个list,其每个元素由两个list组成,这两个List的所有元素组成了该属性的所有level.
    参数:
    attr_type: 0 定距变量(包括连续变量和有序变量)，1 名义变量
    attr_data: 只包括指定属性值相关数据[[[attr_level,target],count],...]
    '''
    levels = [v[0][0] for v in attr_data]
    if len(set(levels)) == 0:
        raise NameError
    if len(set(levels)) < 2:
        return []
    #print 'flag3'
    #print '-------------------'
    #print levels
    #print '-------------------'
    if attr_type == 0:
        #外面再加一层排序是因为set的结果不一定保证有序
        sorted_levels = sorted(list(set(sorted(levels)))) 
        return [Split(attr_type, float(sorted_levels[key-1] + sorted_levels[key])/2)
            for key in range(1, len(sorted_levels))  ]
    elif attr_type == 1:

        #------下面是穷举法:
        #sorted_value = sorted(list(set(sorted(values)))) 
        ##外面再加一层排序是因为set的结果不一定保证有序 
        #results = []
        ##计算量太大 2**len(sorted_value)-1)
        ##考虑使用分类方法来产生有限的拆分集合
        #for flag in range(1, 2**len(sorted_value)-1):
        #    result = [[],[]]
        #    for idx in range(0, len(sorted_value)):
        #        if not (2**idx)&flag == 0: #            
        #            result[0].append(sorted_value[idx])
        #        else:
        #            result[1].append(sorted_value[idx])
        #    results.append(result)
        #return results

        #-----下面是快捷算法
        #可以参考 Challenges in Splitting Multilevel Predictors( http://www.mathworks.cn/cn/help/stats/splitting-categorical-predictors-for-multiclass-classification.html)
        #按道理来说这里的count可以使用，也可以不使用
        #下面是不使用count的代码，从理论上更倾向于使用后一种方案
        #levels_dict =[[level,response_mean],...] 
        #这里的response应该是mean和variance两个目标值，
        #而respone_mean则是对mean的mean值
        levels_dict  = {}
        for attr_case in attr_data:
            level = attr_case[0][0]
            target = attr_case[0][1]
            if not levels_dict.has_key(level):
                levels_dict[level] = [target, 1]
            levels_dict[level][0] += target 
            levels_dict[level][1] += 1
        levels_dict = [[k, float(levels_dict[k][0])/levels_dict[k][1]] for k in levels_dict]
        sorted_levels_dict = sorted(levels_dict, reverse=True, key=lambda x:x[1])
        sorted_levels_dict = [l[0] for l in sorted_levels_dict]

        if len(sorted_levels_dict) != 2:
            return [Split(attr_type, [sorted_levels_dict[0:idx], sorted_levels_dict[idx:]])
                for idx in range(1, len(sorted_levels_dict)-1)]
        else:
            return [ Split(attr_type, [[sorted_levels_dict[0]], [sorted_levels_dict[1]]]) ]

def cal_best_split(attr_data, attr_idx, attr_type):#属性为定距变量
    '''对于某个属性计算最优分裂。
    实现方法:
    对于连续变量，计算最优拆分值。
    对于连续变量，计算最优拆分集合。
    参数介绍:
    data中每个元素为数组表示一个case(这里只包括一个属性)，包括属性值、目标值、case在历史中的数量。
    attr_data = [[[attr_value, target_value], count],...]
    attr_idx: 要拆分属性的索引,从0开始索引
    attr_type:0 定距变量(包括连续变量和有序变量)，1 名义变量
    return:
        is_split:
        branch:
        relateive_sq_error
    '''
    #print 'flag2'
    min_sq_error = float('inf')
    best_split = None
    best_left_mean = None
    best_right_mean = None
    sq_error = None
    # attributes values of all observations
    # attr_data 只包括指定属性值相关数据[[attr,target],count]
    #-------------------------hadoop 不需要并行化，但是需要更好的选择少数拆分值，
    #遍历所有的拆分值
    split_set =  cal_all_split(attr_data, attr_type)
    if len(split_set) == 0:
        #print 'flag4'
        return (False, None, None)
    for split in cal_all_split(attr_data, attr_type):
        left_data = []
        right_data = []
        #-------------------------hadoop并行化
        #对所有数据在二叉中进行预测
        for attr_case in attr_data:
            select_flag = split.select(attr_case[0][0])
            if select_flag == 0:
                left_data.append(attr_case)
            elif select_flag == 1:
                right_data.append(attr_case)
            else:
                raise ValueError,"新的属性值"
        #-------------------------hadoop并行化
        left_count = sum([d[1] for d in left_data])
        right_count = sum([d[1] for d in right_data])
        #print 'sdfsd '+str(len(left_data))
        #print 'right data '+str(len(right_data) )
        #print 'attr_type '+str(attr_type)
        #加权平均
        left_mean = float(sum([float(d[0][-1])*d[1]/left_count for d in left_data]))
        right_mean = float(sum([float(d[0][-1]*d[1])/right_count for d in left_data]))
        #相对平方误差 并加上 样本量
        left_sq_error_list = [[(value[0][-1]-left_mean)**2, value[1]] for value in left_data]
        right_sq_error_list = [[(value[0][-1]-right_mean)**2, value[1]] for value in right_data]
        sq_error = sum([float(d[0]*d[1])/left_count for d in left_sq_error_list]) + sum([ float(d[0]*d[1])/right_count for d in right_sq_error_list] )
        #最优
        if sq_error < min_sq_error:
            min_sq_error = sq_error
            best_split = split
            best_left_mean = left_mean 
            best_right_mean = right_mean 
    return (True, Branch(attr_idx, attr_type, best_split, left_count, right_count, best_left_mean, best_right_mean, ), sq_error)

def cal_best_stump(data, attrs_type, sq_error_delta, depth):
    '''计算最好的决策树，采用递归算法，其核心是计算最优的branch
    实现方法:
    这里要考虑加入如何控制树的深度，暂时实现二叉。
    参数介绍:
    data中每个元素为数组表示一个case，包括属性值、查得目标值、目标值、case在历史中的数量。
    data = [[[attrs_value, similar_target_value, target_value], count],...]
    depth: 即分叉的次数(在一条路径上) ,初始调用值是max_depth,每次减1，到0则停止
    relateive_sqerror_delta: 停止递归(即停止分支)的阈值
    return:
        is_branch
    '''
    #print('xunlian')
    if len(data) == 0:
        return (False, None)
    #这里也需要实现
    (is_branch, cur_branch, sq_error) = cal_best_branch(data, attrs_type)
    if is_branch == False:
        return (False, None )
    depth -= 1
    if depth <= 0:
        return (True, cur_branch )
    if sq_error < sq_error_delta:
        print 'error'+str(sq_error)
        print 'delta'+str(sq_error_delta)
    else:
        left_data = [] #被分到左子树的数据
        right_data = [] #被分到右子树的数据
        for case in data:
            if cur_branch.select(case[0]) == 0:
                left_data.append(case)
            elif cur_branch.select(case[0]) == 1:
                right_data.append(case)
        #if len(left_data) == 0 or len(right_data) == 0
        #需要添加这种判断
        (left_is_branch, cur_branch.left_child_branch ) = cal_best_stump(left_data, attrs_type, sq_error_delta, depth)
        (right_is_branch, cur_branch.right_child_branch ) = cal_best_stump(right_data, attrs_type, sq_error_delta, depth)
    return (True, cur_branch )

def cal_best_branch(data, attrs_type):
    '''计算最好的决策分支
    attrs_type:所有属性的属性类型: 
    0 定距变量(包括连续变量和有序变量)，1 名义变量
    这里默认深度为1，后续再修改
    return:
        is_branch:是否进行分支
    '''
    best_split_branch = None
    min_sq_error = float('inf')
    branch = None
    #遍历所有属性,除了data最后一个，因为data最后一个是目标值
    for attr_idx in range(0, len(data[0][0])-1):
        attr_data = [[[value[0][attr_idx], value[0][-1]], value[1]] for value in data]
        #print 'flag'
        (is_split, branch, sq_error) = cal_best_split(attr_data, attr_idx, attrs_type[attr_idx])
        if is_split == False:
            continue
        #print 'best split'+str(sq_error)
        if sq_error < min_sq_error:
            #print 'xunlian sub'
            min_sq_error = sq_error
            best_split_branch = branch
    if best_split_branch == None:
        return (False, None, None)
    return (True, best_split_branch, sq_error)

def lsq_gbdt(data, attrs_type, stump_number, sq_error_delta, max_depth):
    ''' 使用LSQ的gbdt算法
    data为列表的列表，每个子列表代表一条训练数据
    attrs_type为各个属性的类型，长度等于data中每条记录的长度，
    当然目标列对应列设置无效，因为这是回归问题。
    stump_number决策树的数量
    relateive_sq_error_delta: 增长树停止递归(即停止分支)的阈值
    max_depth: 最大层数，也就是在一条路径上决策的次数
    return
        is_train
    '''
    if type(max_depth) == int and max_depth <= 0:
        raise ValueError,'max_depth error'
    #the last column is the target variable
    #第一种方法计算总体均值
    total_count = sum([ value[1] for value in data])
    target_mean = float(sum([ value[0][-1]*value[1] for value in data]))/total_count
    #第二种方法计算总体均值
    #the last column is the target variable
    #total_count = len(data) 
    #target_mean = float(sum([ value[0][-1] for value in data]))/total_count

    model = AdditiveRegressionTrees(target_mean) #初始设置为全部样本的均值
    #树的深度和拓扑结构要有参数可以控制,这里暂时没有实现
    error_data = [ d[0][-1] - target_mean for d in data]
    new_data = copy.deepcopy(data)
    #这里需要计算预测效果来控制树的数量,
    #即要设计停止策略
    itr_num = 0
    while itr_num < stump_number:
        for i in range(0, len(new_data)):
            new_data[i][0][-1] = error_data[i]
        (is_branch, root_branch ) = cal_best_stump(new_data, attrs_type, sq_error_delta, max_depth)
        if is_branch == False:
            break
        stump = Stump(root_branch)
        print 'root branch'+str(root_branch)
        error_data = [ d[0][-1] - stump.get_prediction(d[0]) for d in new_data]
        model.append(stump)
        if model.cal_relative_sq_error(data) < sq_error_delta:
            return (True, model)
        itr_num += 1
    if itr_num == 0:
        return (False, None)
    return (True, model)

def traverse_plot_f(x):
    '''画图时内点使用函数
    '''
    result =''
    result += str(id(x))+' -> '+str(id(x.left_child_branch)) + ' [label="'+str(x.attr_idx)+'_'+str(x.split.split_rule[0] if x.split.attr_type == 1 else x.split.split_rule)+'"];\n'  #左
    result += str(id(x))+' -> '+str(id(x.right_child_branch)) + ' [label="'+str(x.attr_idx)+'_'+str(x.split.split_rule[1] if x.split.attr_type == 1 else x.split.split_rule)+'"];\n' #右
    result += str(id(x)) +' [label=" "]' +';\n' #当前节点
    return result

def traverse_plot_g(x):
    '''画图时终点使用函数
    '''
    result = ''
    result += str(id(x))+' -> '+str(id(x.left_prediction)) + ' [label="' + str(x.attr_idx) +'_'+str(x.split.split_rule[0] if x.split.attr_type == 1 else x.split.split_rule)+'"];\n' #左
    result += str(id(x))+' -> '+str(id(x.right_prediction)) + ' [label="'+str(x.attr_idx)+'_'+str(x.split.split_rule[1] if x.split.attr_type == 1 else x.split.split_rule)+'"];\n' #右
    result += str(id(x)) + '[label=" "];\n' #当前节点
    result += str(id(x.left_prediction)) + '[label="'+ str(round(x.left_prediction,5)) +' "];\n' #左预测节点
    result += str(id(x.right_prediction)) + '[label="'+ str(round(x.right_prediction,5)) +' "];\n' #右预测节点
    return result

def traverse_plot_h(x):
    '''画图时半终点使用函数
    '''
    result = ''
    result += str(id(x)) + '[label=" "];\n' #当前节点
    if x.left_child_branch == None:
        result += str(id(x))+' -> '+str(id(x.left_prediction)) + ' [label="' + str(x.attr_idx) +'_'+str(x.split.split_rule[0] if x.split.attr_type == 1 else x.split.split_rule)+'"];\n'
        result += str(id(x.left_prediction)) + '[label="'+ str(round(x.left_prediction,5)) +' "];\n'
    else:
        result += str(id(x))+' -> '+str(id(x.left_child_branch)) + ' [label="'+str(x.attr_idx)+'_'+str(x.split.split_rule[0] if x.split.attr_type == 1 else x.split.split_rule)+'"];\n'  #左
    if x.right_child_branch == None:
        result += str(id(x))+' -> '+str(id(x.right_prediction)) + ' [label="'+str(x.attr_idx)+'_'+str(x.split.split_rule[1] if x.split.attr_type == 1 else x.split.split_rule)+'"];\n'
        result += str(id(x.right_prediction)) + '[label="'+ str(round(x.right_prediction,5)) +' "]' + ';\n'
    else:
        result += str(id(x))+' -> '+str(id(x.right_child_branch)) + ' [label="'+str(x.attr_idx)+'_'+str(x.split.split_rule[1] if x.split.attr_type == 1 else x.split.split_rule)+'"];\n' #右
    return result

def GBDT(file_name,attrs_type,stump_number,sq_error_delta,max_depth,target_label,model_pickle,log_file_name):
    '''
    测试代码
    '''
    model_log = '----------GBDT模型训练结果---------------\n'
    #attrs_type属性值类型: 0定距或定序(interval or ordinal), 1名义(nominal)
    #这里没有对定序变量的拆分进行处理，因为定序变量需要指定一个序
    #attrs_type = sys.argv[1].split(',')
    #the_stump_number = int(sys.argv[2])
    #the_sq_error_delta = float(sys.argv[3])
    #the_max_depth = int(sys.argv[4])
    #attrs_type = [int(the_attr_type) for the_attr_type in attrs_type]
    #第5个参数
    #target_label=sys.argv[5]
    #第6个参数 日志存储位置
    #log_file_name=sys.argv[6]
    model_log += '变量类型列表(0定距或定序(interval or ordinal), 1名义(nominal)):' + str(attrs_type) + '\n'
    model_log += '模型中决策树的数量限制:' + str(stump_number) + '\n'
    model_log += '模型训练的平方误差阈值:' + str(sq_error_delta) + '\n'
    model_log += '模型中树的最大深度:' + str(max_depth) + '\n'
    model_log += '模型目标类型mean或者var:' + target_label + '\n'
    #the_data为训练数据,以字典形式存放数据，stdin中抽取，
    #并把属性值和通过模板和StarTree查询的目标值合并成训练数据
    #the_data中每个元素为数组表示一个case，包括属性值、查得目标值、目标值、case在历史中的数量。
    #the_data = [[[the_attrs_value, the_similar_target_value, the_target_value], the_count],...]
    the_data = [] 
    #for line in sys.stdin:
    for line in open(file_name):
        #the_attr_values 一个case的各个属性的值
        #the_similar_target_value 通过模板和StarTree查找到的目标值
        #the_target_value 真实的目标值
        #the_count 该case(由attr_values唯一确定)在历史数据中数量
        (the_attrs_value, the_similar_target_value, the_target_value, the_count) = line.split('\t')
        the_attrs_value = the_attrs_value.split('|')
        the_attrs_value.append(float(the_similar_target_value))
        the_target_value = float(the_target_value)
        #检查数据合法性
        if the_target_value <= 0:
            continue

        the_count =  float(the_count)
        the_data.append( [the_attrs_value + [the_target_value], the_count])
        #count可以作为样本的权重，这里模型中暂时不考虑
    #model_log += '样本数量:' + str(len(the_data)) + '\n'
    model_log += '样本数量:' + str(sum([d[1] for d in the_data])) + '\n'
    #添加两个属性类型，对应于similar_target_value
    #均为0,0 因为这里是回归问题
    attrs_type += [0]
    (the_is_train, the_model ) = lsq_gbdt(the_data, attrs_type, stump_number, sq_error_delta, max_depth)
    if the_is_train == False:
        model_log += '训练数据无法拆分\n'
        return

    #存储模型到pickle文件中
    #f_AdditiveRegressionTrees =open('AdditiveRegressionTrees_' + target_label + '.pickle','w')
    f_AdditiveRegressionTrees =open(model_pickle,'w')
    cPickle.dump(the_model, f_AdditiveRegressionTrees)
    f_AdditiveRegressionTrees.close()

    #total error
    #tmp_f = lambda x:x.left_sq_error_list
    # edge function
    dot_text = the_model.recurse_all_stumps(traverse_plot_f, traverse_plot_g, traverse_plot_h)

    #print dot_text
    tmp_text = ''
    for t in dot_text:
        t.append(str(id(the_model.stump_list[0].root_branch)) + " [label="+str(round(the_model.target_mean,5))+"];")
        tmp_text += reduce(lambda x,y:x+y,t) 

    model_log += '训练所得模型最终加权相对误差:' + str(the_model.cal_relative_sq_error(the_data)) + '\n'
    model_log += '训练所得模型最终加权绝对误差:' + str(the_model.cal_sq_error(the_data)) + '\n'
    model_log += '模型中树数量:' + str(len(the_model.get_stump_list())) + '\n'
    model_log += '模型结构的dot文件:\n'+'digraph G { \n' + tmp_text + '}\n'

    #测试一些数据
    test_result = ''
    for i in range(0,len(the_data),1):
        try:
            predict_result = the_model.get_prediction(the_data[i][0])
        except Exception,e:
            predict_result='无法预测'
    	test_result += '样本' +str(the_data[i][0])+'\t数量'+str(the_data[i][1])+'\t真实目标'+str(the_data[i][0][-1]) + '\t预测目标值' + str(predict_result) + '\n'
    model_log += test_result

    open(log_file_name,'a').write(model_log)
    #print the_model.stump_list[0].root_branch.split.split_rule
    #print the_model.stump_list[0].root_branch.right_child_branch.split.split_rule
    #print the_model.stump_list[0].root_branch.right_child_branch.right_child_branch.split.split_rule


if __name__ == "__main__":
    pass
