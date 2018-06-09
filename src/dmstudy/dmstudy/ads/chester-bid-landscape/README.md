# chester-bid-landscape
GBDT model for bid landscape



Cui bid landscape算法/GBDT_version文件夹
所有代码均用python脚本来完成。去除了所有hadoop操作。
如果真正要用hadoop,则另外再添加相应操作的hadoop版本。

1. joinlog2features_table 将源数据转化为指定特征的类csv格式文件features_table。
2. compute_entropy.compute_su_from_table 从features_table里计算symmetry uncertainty
3. fcbf.fcbf 从symmetry uncertainty里进行特征选择，结果为selected_feat
4. statistic.extract 从源数据抽取选择的特征转化为statistics文件
5. StarTree.build 从statistics文件里构建StarTree，结果存为expand_sample
6. TemplateSelection.template_select 从expand_sample里进行模板选择
7. statistic.extract 从expand_sample里产生GBDT模型所用数据，即进行mean和var的统计
8. GBDT.GBDT 生成GBDT模型
9. prediction.sample_predict 从GBDT模型对sample进行预测
10. prediction.campaign 从GBDT模型对campaign进行预测，(与sample预测不同的是，要进行模型混合)。


ftrl version bid landscape model/ftrl_version 文件夹
