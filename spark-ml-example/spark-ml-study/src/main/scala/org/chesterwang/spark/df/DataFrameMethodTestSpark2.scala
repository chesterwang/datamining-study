package org.chesterwang.spark.df

import org.chesterwang.spark.df.util.LocalSparkContext
import org.apache.spark.sql.{Dataset, SparkSession}
import org.apache.spark.sql.functions._

/**
  * Created by chester on 17-2-20.
  */
object DataFrameMethodTestSpark2 {

  val sparkSession = SparkSession.builder
    .master("local")
    .appName("my-spark-app")
//    .config("spark.some.config.option", "config-value")
    .getOrCreate()

  def main(args: Array[String]) {

//    val ds = sparkSession.read.text("data/mllib/gmm_data.txt").as[String]
//    ds.show(10)
//    val ds2 = ds.map(_.split(","))
//
//    Thread.sleep(100000)
  }
}
