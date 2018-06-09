#!/usr/bin/env python
#coding:utf-8

import sys,cPickle
#sys.setrecursionlimit(10) #例如这里设置为一百万  

def fuzzy_value(attr, target, sample):
    #判断值是否应该匹配STAR值
    #另外更多的细节需要添加:数量阈值，属性特异性STAR值(如空格等)
    if ((not sample.has_key(attr)) or
        sample[attr] is None):
        return True

class NormalNode:
    #self.value_child : dict format: value->child
    def __init__(self, node_attr):
        self.attr = node_attr
        self.value_child = {}

class TerminalNode:
    def __init__(self, attr, count, sum, sq_sum):
        #真正实现时这里self.attr就应该是target属性
        self.attr = attr
        self.count = count
        self.sum = sum
        self.sq_sum = sq_sum

class StarTree:

    def __init__(self, attr_hierarchy, target):
        if not attr_hierarchy[-1] == target:
            print 'error'
            raise NameError
        self.root = NormalNode(attr_hierarchy[0])
        self.attr_hierarchy = attr_hierarchy
        self.target = target

    def insert_sample(self, sample):
        #该方法会对一个sample匹配多条path,也就是sample分解成fined samples进行统计
        self.path_stat(self.root, sample)

    def path_stat(self, path_top, sample):
        #默认认为target应该是attr_hierarchy最后一个属性
        #format:  sample{a:b,c:d},target="a"
        cur_node = path_top
        #sample中没有相关属性值，或者属性值不是具体值，或者对应sample数量非常好少，
        #则顺路而下不分叉，一路设置为STAR值，
        #能走多远走多远(中间可能会新建节点),并更新cur_node到最后所到达的节点
        cur_node = self.direct_path(cur_node, sample)
        #direct_path方法退出则会出现两种情况
        #1.direct_path走到了终端节点
        #2.sample中出现当前属性的具体值
        #若1.cur_node是终端节点，则添加统计信息
        if self.is_last_target(cur_node.attr):
            cur_node.count += sample[self.target]['count']
            cur_node.sum += sample[self.target]['sum']
            cur_node.sq_sum += sample[self.target]['sq_sum']
            return
        #若2.sample中有当前节点的属性具体值时，退出循环,并分叉
        if sample[cur_node.attr] == '':
            branch_values = ['*']
        else:
            branch_values = ['*', sample[cur_node.attr]]
        for cur_attr_value in branch_values:
            if ((not cur_node.value_child.has_key(cur_attr_value)) or
                (cur_node.value_child[cur_attr_value] is None)): 
                #上面第1种情况则保证第2种情况不是最后的终端节点
                new_attr = self.attr_hierarchy[
                    self.attr_hierarchy.index(cur_node.attr) + 1]
                nn = self.new_node(new_attr)#新建
                cur_node.value_child[cur_attr_value] = nn
            self.path_stat(cur_node.value_child[cur_attr_value], sample)

    def direct_path(self, cur_node, sample):
        cur_attr_value = '*'
        while (fuzzy_value(cur_node.attr, self.target, sample) and
            not self.is_last_target):
            #树中这个属性值尚未设置STAR
            if not cur_node.value_child.has_key(cur_attr_value):
                cur_node.value_child[cur_attr_value] = self.new_node(cur_node.attr)
            #若已经设置STAR值，则遍历到下一个或者最终统计
            cur_node = cur_node.value_child[cur_attr_value]
        return cur_node

    def is_last_target(self, attr):
        #是否是最后一个属性
        return self.attr_hierarchy.index(attr) == len(self.attr_hierarchy)-1

    def new_node(self, attr):
        #检验参数是否荣誉，仅仅使用cur_node的attr
        #如果cur_node的属性不是最后一个属性，则建立一个正常中间节点
        if not self.is_last_target(attr):
            new_node = NormalNode(attr)
            return new_node
        #如果cur_node的属性是最后一个属性，则建立终端节点，用来存储统计结果
        else:
            return TerminalNode(attr, 0, 0, 0)
       
    def tree(self, path_top, pre_string):
        #打印树形结构,未完全实现
        if path_top.attr == self.target:
            print  ': ',path_top.count, path_top.sum, path_top.sq_sum
            return
        else:
            print ''
        for key in path_top.value_child.keys():
            print pre_string + '├──' + str(key),
            self.tree(path_top.value_child[key], pre_string + '   ')
    #def recurse(self, path_top, pre_string,result_list):
    def recurse(self, path_top, tmp_list,result_list):
        #打印树形结构,未完全实现
        if path_top.attr == self.target:
            result_list.append(tmp_list + [path_top.count, path_top.sum, path_top.sq_sum])
            return
        else:
            pass
        for key in path_top.value_child.keys():
            self.recurse(path_top.value_child[key], tmp_list + [key] ,result_list)
    def query(self, path):
        '''严格匹配查找
        返回终端节点信息，即count,sum,sq_sum
        '''
        cur_node = self.root
        for p in path:
            if isinstance(cur_node, NormalNode):
                if cur_node.value_child.has_key(p):
                    cur_node = cur_node.value_child[p]
                else:
                    return (False,{})
        if isinstance(cur_node, TerminalNode):
            return (True,{'count':cur_node.count,'sum':cur_node.sum, 'sq_sum':cur_node.sq_sum})
        else:
            raise NameError, 'asjdfajlsdfk'
    def query_by_template(self, template_list,sample):
        '''通过模板查询样本
        结果为模板以及类似路径等内容
        result:
            is_include:是否能在startree中查找到
            result:查找到的信息 见StarTree.query方法
            template: 查找到结果所用的模板
            similar_path:查找到结果所用的类似路径
        '''
        for template in template_list:
            similar_path = template.mask_path(sample)
            if similar_path != None:
                (is_include, result) = self.query(similar_path)
                if is_include is True:
                    return (True,result,template,similar_path)
        return (False,{},None,None)

    def prune(self, path_imp_delta):
        '''剪掉impression较少的枝,需要对树进行递归
        剪掉一个节点时，树的其他部分不会收到任何影响
        但是如果同时剪掉一个节点的两个子节点，那么该节点也需要剪掉
        '''
        #一次剪枝
        stack = []
        stack.append(self.root)
        while len(stack) != 0:
            cur_node = stack[-1]
            del stack[-1]
            if isinstance(cur_node, NormalNode):
                #stack += [for  in cur_node.value_child]
                for k in cur_node.value_child.keys():
                    if isinstance(cur_node.value_child[k],TerminalNode):
                        if cur_node.value_child[k].count <  path_imp_delta:
                            tmp_node = cur_node.value_child
                            del tmp_node[k]
                    elif isinstance(cur_node.value_child[k],NormalNode):
                        stack.append(cur_node.value_child[k])
        #对于那些没有路径通往终端节点的节点，删除之,删除之后要检查父节点
        stack = []
        stack.append(self.root)
        attr_no = len(self.attr_hierarchy)
        # 为了保证修建完整，循环多次，次数为特征数目
        # 因为每次循环可能只删除一个特征
        for prune_no in range(0,attr_no):
            while len(stack) != 0:
                cur_node = stack[-1]
                del stack[-1]
                if isinstance(cur_node, NormalNode):
                    #stack += [for  in cur_node.value_child]
                    for k in cur_node.value_child.keys():
                        if isinstance(cur_node.value_child[k], NormalNode):
                            if k == '480':
                                print '480-----'
                                print cur_node.value_child[k].value_child
                                print cur_node.value_child[k].value_child['320'].value_child
                                print cur_node.value_child[k].value_child['*'].value_child
                            if cur_node.value_child[k].value_child == {}:
                                del cur_node.value_child[k]
                            else:
                                stack.append(cur_node.value_child[k])
        #对于最靠近根节点下的一层节点，可能删除不干净，下面代码保证删除干净
        cur_node = self.root
        for k in cur_node.value_child.keys():
            tmp_node = cur_node.value_child[k]
            if tmp_node.value_child == {}:
                del cur_node.value_child[k]

def build(file_name,feature_name,path_imp_delta,expand_star_tree_file):

    hier = feature_name + ['price']
    st = StarTree(hier, 'price')
    for line in open(file_name):
        line_array= line.split('\t')
        val_list=line_array[0:-3]
        (count,old_sum,sq_sum)=line_array[-3:]
        #sample = {k:v for k ,v in zip(hier[0:-1],key.split('|'))}
        if count < 10:
            continue
        sample = {}
        for k,v in zip(hier[0:-1],val_list):
            sample[k] = v
        sample['price'] = {'count':int(count), 'sum':float(old_sum),'sq_sum':float(sq_sum)}
        st.insert_sample(sample)

    result_list = []
    st.recurse(st.root, [],result_list)
    #剪掉impression较少的枝
    st.prune(path_imp_delta)


    outfile=open(expand_star_tree_file,'w')
    for l in result_list:
        outfile.write( '%s\t%d\t%d\t%.2f\n' % ('\t'.join(l[0:-3]),l[-3],l[-2],l[-1]))
    outfile.close()
    #存储StarTree结构
    f_StarTree=open(file_name + '_StarTree.pickle','w')
    cPickle.dump(st,f_StarTree)
    f_StarTree.close()

if __name__ == '__main__':
    ##StarTree
    #st = StarTree(['co', 'ca', 'bid'], 'bid')
    ##样本形式{'co':3, 'ca':4, 'bid':{'count':1,'sum':2,'sq_sum':3}}
    ##这里字典键为value count sum ，是为了程序泛化，因为以后可能遇到其他类似bid_value的预测问题
    #st.insert_sample({'co':3, 'ca':4, 'bid':{'count':1,'sum':2,'sq_sum':3}})
    #st.insert_sample({'co':4, 'ca':5, 'bid':{'count':1,'sum':2,'sq_sum':3}})
    #print isinstance(st.root.value_child[3].value_child[4],TerminalNode)
    #st.tree(st.root, '│')
    #(is_include, result)= st.query([3,4])
    #if is_include == True:
    #    print result
    #
    ##最终结果的存储是个问题,可以考虑用pickle来存储,并且要估计其存储大小,以及内存是否能放下

    #(feat_candidate,feat_candidate_idx)
    #feat_candidate = [('device_geo_city', 2.9634816817837583e-12), ('device_carrier', 1.473694636775048e-15), ('cur', 0.0), ('user_geo_city',0.0)]
    #hier = map(lambda x:x[0],feat_candidate) + ['price']

    pass
