# !/usr/bin/env python
# coding:utf-8

import bid_paras_optimization
import ConfigParser
#
class Test():
    def test2015(self):
        '''
        使用base下的wzn模型文件
        '''
        #get ctr feature weight file
        #strategy_type = 'threshold'
        strategy_type = 'lin'
        #strategy_type = 'ortb'
        ctr_fw_file = bid_paras_optimization.get_latest_files("/data/data_workspace/featonline/base")[0]
        #ctr_fw_file = '/home/chester/data/wzn'
        #get join log file
        #price_clear_files = ["/home/chester/data/data1424838250795.COMPLETED.nonyouku.10733"]
        price_clear_files = ["/data/data_workspace/tongpeng/2015-03-06bid_para_optimization/nonyouku.data"]
        min_para =  0.03
        max_para =  1.5
        max_ecpc = 0.05
        out_file = "/data/data_workspace/tongpeng/2015-03-06bid_para_optimization/nonyouku.data.bid"
        #out_file = "/home/chester/data/test"
        print ctr_fw_file
        print price_clear_files
        print max_para
        print min_para
        print out_file

        bpo_logger.info('----------test-----------')
        bid_paras_optimization.strategy_optimization("new",strategy_type, ctr_fw_file, price_clear_files, '*', min_para, max_para, max_ecpc,1, out_file)
    def test2014(self):
        '''
        使用老模型,和老数据20141231投放数据
        老模型为原来的特征权重文件
        '''
        strategy_type = 'threshold'
        strategy_type = 'lin'
        strategy_type = 'ortb'
        strategy_type = 'lin'
        ctr_fw_file = "/data/data_workspace/online/fw/fw1420051801.89"
        price_clear_files=["/data/data_workspace/tongpeng/20141231bid_paras_optimization/data"]
        min_para =  0.03
        max_para =  1.5
        max_ecpc = 0.3
        out_file = "/data/data_workspace/tongpeng/20141231bid_paras_optimization/data.bid"
        print ctr_fw_file
        print price_clear_files
        print max_para
        print min_para
        print out_file
        
        bpo_logger.info('----------test-----------')
        bid_paras_optimization.strategy_optimization("old",strategy_type, ctr_fw_file, price_clear_files, '*', min_para, max_para, max_ecpc,1,out_file)

if __name__ == '__main__':
    #test_instance = Test()
    #test_instance.test2014() #test_instance.test2015()

    #main_cmd()
    main_file()


