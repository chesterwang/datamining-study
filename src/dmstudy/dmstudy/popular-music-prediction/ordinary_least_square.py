#!/usr/bin/env python
# coding:utf8
'''使用最小二乘法律以及五个最简单的特征来建模'''

import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
from sklearn import linear_model

# 设定dataframe的csv解析用到的日期解析函数
dt_parser = lambda x: datetime.strptime(x, "%Y%m%d")


class ordinary_least_square():

    def get_all_date_play_counts(self, date_begin, date_end, song_info, user_action):
        '''对song_info里的每一首歌按照(date_begin到date_end里的每一天)展开成song_features,
        并根据user_action统计每一首歌的每天播放量，并加入到结果song_features中
        '''
        # 统计song每日的播放量 song_daily_play_counts
        song_daily_base = pd.DataFrame(song_info.song_id)
        date_seq = [ts for ts in pd.date_range('20150301', periods=183, freq='D').tolist()]
        song_daily_play_counts = pd.DataFrame()
        for tmpds in date_seq:
            tmpdf = user_action[user_action.ds == tmpds].groupby("song_id", as_index=False)["ds"].agg(
                {"play_count": "count"})
            tmpdf2 = pd.merge(song_daily_base, tmpdf, on=["song_id"], how="left")
            tmpdf2["ds"] = tmpds
            song_daily_play_counts = song_daily_play_counts.append(tmpdf2)
        song_daily_play_counts.fillna(0, inplace=True)
        return song_daily_play_counts

    def get_train(self, song_info, user_action):
        """生成训练数据
        song_info:
        user_action:
        return: train
        """
        song_daily_play_counts = self.get_all_date_play_counts("", "", song_info=song_info, user_action=user_action)

        # 读取静态信息,并添加每日播放数，发布时间之久两个特征，存储到song_features
        song_features = pd.merge(song_daily_play_counts, song_info, on=["song_id"])
        song_features["publish_diff"] = (song_features.ds - song_features.publish_time).apply(
            lambda x: pd.to_timedelta(x).days)

        # 生成一个历史的DF,song_ds_cnt，存储当前的前一天的歌曲播放数
        song_ds_cnt = user_action.groupby(["song_id", "ds"], as_index=False)["user_id"].agg({"cnt": "count"})
        song_ds_cnt["today"] = song_ds_cnt.ds + timedelta(days=60)

        # 根据歌曲静态信息song_features和每日的动态特征song_ds_cnt来生成最终的特征组
        song_features = pd.merge(song_features, song_ds_cnt[["song_id", "today", "cnt"]],
                                 left_on=["song_id", "ds"], right_on=["song_id", "today"],
                                 how="left")
        del song_features["today"]
        song_features.rename(columns={'cnt': 'yesterday_cnt'}, inplace=True)
        song_features["yesterday_cnt"] = song_features["yesterday_cnt"].fillna(0)

        # msk = np.random.rand(len(song_features)) < 0.8
        # train=song_features[msk]
        # test=song_features[~msk]

        train = song_features[song_features.ds < "2015-09-01"]
        return train


if __name__ == '__main__':
    # 读取用户行为日志user_action, 读取歌曲信息song_info
    datapath = "/home/chester/data/2016-06/231531/"
    song_info_path = datapath + "p2_mars_tianchi_songs.csv"
    user_action_path = datapath + "p2_mars_tianchi_user_actions.csv"
    song_info = pd.read_csv(song_info_path, sep=",",
                            names=["song_id", "artist_id", "publish_time", "song_init_plays", "language", "gender"],
                            parse_dates=["publish_time"], date_parser=dt_parser,
                            dtype={"publish_time": datetime})
    user_action = pd.read_csv(user_action_path, sep=",",
                              names=["user_id", "song_id", "gmt_create", "action_type", "ds"],
                              parse_dates=["ds"], date_parser=dt_parser,
                              dtype={"ds": datetime})
    ols = ordinary_least_square()
    print ols.get_train(song_info, user_action).first(10)

# clf = linear_model.Ridge(alpha = .5)
# clf.fit (train[["song_init_plays","language","gender","publish_diff","yesterday_cnt"]].values,
#          train["play_count"].values)
# #LinearRegression(copy_X=True, fit_intercept=True, n_jobs=1, normalize=False)
# coef=clf.coef_
#
# predict = np.matrix(test[["song_init_plays","language","gender","publish_diff","yesterday_cnt"]].values)*[[x] for x in coef]
# predict = [[x[0]] if x[0]>0 else [0] for x in predict]
#
# test["predict_play_count"] = [round(x[0]) for x in predict]
#
#
# artist_play_count = test.groupby(["artist_id","ds"],as_index=False)["play_count"].agg({"cnt":"sum"})
# artist_play_count = artist_play_count[artist_play_count.cnt != 0]
# predict_artist_play_count = test.groupby(["artist_id","ds"],as_index=False)["predict_play_count"].agg({"cnt":"sum"})
# old_predict = pd.merge(artist_play_count,predict_artist_play_count,on=["artist_id","ds"])
# old_predict["diff_sq"] = ((old_predict["cnt_y"]-old_predict["cnt_x"])/old_predict["cnt_x"])**2
# tmp_df=old_predict.groupby(["artist_id"],as_index=False).agg({"ds":"count","diff_sq":"sum"})
# artist_play_count = test.groupby(["artist_id"],as_index=False)["play_count"].agg({"cnt":"sum"})
# final_data = pd.merge(tmp_df,artist_play_count[["artist_id","cnt"]],on=["artist_id"])
# sigma=final_data["cnt"]**0.5 *( 1- (final_data["diff_sq"]/final_data["ds"])**0.5)
#
#
#
#
# #预测
# #song_features["publish_diff"]=(song_features.ds - song_features.publish_time).apply(lambda x:pd.to_timedelta(x).days)
#
# #test_song_info存储歌曲在预测时间范围内的静态信息
# test_song_info = pd.DataFrame()
# date_seq = [ts for ts in pd.date_range('20150901', periods=60, freq='D').tolist()]
#
# for tmpds in date_seq:
#     tmp_song_info=song_info.copy()
#     tmp_song_info["ds"] = tmpds
#     test_song_info=  test_song_info.append(tmp_song_info)
# test_song_info["publish_diff"]=(test_song_info.ds - test_song_info.publish_time).apply(lambda x:pd.to_timedelta(x).days)
#
# #生成一个历史的DF,song_ds_cnt，存储当前的前一天的歌曲播放数,推后60天，以便和预测时间范围内的静态信息进行join
# song_ds_cnt = user_action.groupby(["song_id","ds"],as_index=False)["user_id"].agg({"cnt":"count"})
# song_ds_cnt["today"] = song_ds_cnt.ds + timedelta(days=61)
#
#
#
#
# sampled_df[["song_init_plays","language","gender","publish_diff","yesterday_cnt"]].values
#
#
# test_song_features = pd.merge(test_song_info,song_ds_cnt,left_on=["song_id","ds"],right_on=["song_id","today"])
# test_song_features[["song_init_plays","language","gender","publish_diff","cnt"]].values
#
# predict = np.matrix(test_song_features[["song_init_plays","language","gender","publish_diff","cnt"]].values)*[[x] for x in coef]
# predict = [[x[0]] if x[0]>0 else [0] for x in predict]
#
# #test_song_features[["song_init_plays","language","gender","publish_diff","cnt"]]
# test_song_features["predict_play_count"] = [round(x[0]) for x in predict]
# artist_play_count = test_song_features.groupby(["artist_id","today"],as_index=False)["predict_play_count"].agg({"cnt":"sum"})
#
#
# artist_play_count.to_csv("/tmp/a.csv")
#
#
# dt_parser = lambda x: datetime.strftime(x,"%Y%m%d")
# artist_play_count["formatds"] = artist_play_count["today"].apply(dt_parser)
# artist_play_count["cnt"] = artist_play_count["cnt"].astype(int)
# artist_play_count[["artist_id","cnt","formatds"]].to_csv("/tmp/mars_tianchi_artist_plays_predict.csv",header=False,index=False)
