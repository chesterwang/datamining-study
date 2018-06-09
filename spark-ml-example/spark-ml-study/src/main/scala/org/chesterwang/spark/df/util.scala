package org.chesterwang.spark.df

import org.apache.spark.sql.SQLContext
import org.apache.spark.{SparkConf, SparkContext}

/**
  * Created by chester on 17-1-16.
  */
object util {

  object LocalSparkContext {
    def getLocalSQLContext(appName: String, host: String = "local[1]"): SQLContext = {
      val sc = getLocalSparkContext(appName, host)
      new SQLContext(sc)
    }

    def getLocalSparkContext(appName: String, host: String = "local[1]"): SparkContext = {
      val conf = new SparkConf().setAppName(appName)
        .setMaster(host)
      val sc = new SparkContext(conf)
      sc.setLogLevel("WARN")
      sc
    }
  }

}
