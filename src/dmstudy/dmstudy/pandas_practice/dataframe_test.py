# coding:utf8
import pandas as pd
import numpy as np


def create_df():
    print __file__
    #csv
    df = pd.read_csv("example.csv")
    print df.head(10)
    #csv选项
    #其他格式


def column_operation():
    df = pd.read_csv("example.csv")
    print df.head(10)
    # df2 = pd.DataFrame([[1,2,3,4],[4,5,6,7]],columns=[["a","b"],["c","d"]])


    #multiIndex初始构造
    cols = pd.MultiIndex.from_arrays([["agroup", "agroup", "bgroup", "bgroup"], ["c", "d", "h", "c"]], names=['ticker', 'field'])
    df2 = pd.DataFrame(np.random.randn(3, 4),columns=cols)
    print df2.head(10)

    #multiIndex选择(列模式)
    print df2["agroup"]
    print df2["agroup","c"]
    # print df2.loc[0,idx[:,"c"]]

    #multiIndex赋值
    # df2["cgroup"] = df2[:,[["agroup","c"],df2["bgroup","h"]]]
    # print df2.loc[:,[["agroup","c"],["bgroup","h"]]]
    idx = pd.IndexSlice
    print df2.loc[:,[idx["agroup","c"],idx["bgroup","h"]]]


if __name__ == "__main__":
    # create_df()
    column_operation()

