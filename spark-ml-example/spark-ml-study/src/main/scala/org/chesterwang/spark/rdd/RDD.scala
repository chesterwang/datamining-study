package org.chesterwang.spark.rdd

import org.apache.spark.{SparkConf, SparkContext}

/**
  * Created by chester on 16-11-23.
  */
object RDD {
  def main(args: Array[String]): Unit = {

    val conf = new SparkConf().setAppName("AssociationRulesExample").setMaster("local[*]")
    val sc = new SparkContext(conf)
    testfor(sc)
  }

def testfor(sc:SparkContext): Unit ={

    for (idx <- 3 to 10){
      val txt = sc.textFile("/home/chester/data/2016-12/part-00000")
      txt.saveAsTextFile(s"/tmp/txt${idx}")
    }

  }


}
