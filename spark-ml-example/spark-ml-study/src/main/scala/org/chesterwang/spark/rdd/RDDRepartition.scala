package org.chesterwang.spark.rdd

import org.chesterwang.spark.df.util.LocalSparkContext

/**
  * Created by chester on 17-2-11.
  */
object RDDRepartition {
  def main(args: Array[String]) {

    val sc = LocalSparkContext.getLocalSparkContext("DataFrameOrder")
    val rdd =  sc.parallelize(Seq(1,2,3,4,5),numSlices = 8)
    println(rdd.getNumPartitions)
    println(rdd.repartition(3).getNumPartitions)


  }

}
