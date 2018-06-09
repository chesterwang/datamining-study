package org.chesterwang.brain

import org.apache.spark.sql.SQLContext
import org.apache.spark.{SparkConf, SparkContext}

/**
  * Created by chester on 17-6-17.
  */
object TestRddOrder {

  def main(args: Array[String]): Unit = {


    val conf = new SparkConf().setAppName("h").setMaster("local[*]")
    implicit val sc = new SparkContext(conf)
    //    test()
    sc.setLogLevel("WARN")

    val sqlContext =new SQLContext(sc)

    val rdd = sc.parallelize(Array((1,2),(3,4)))

    rdd.max()(Ordering.by(-_._2))

    rdd.takeOrdered(1)( Ordering.by(-_._2) )
    .foreach(println)

    print(Seq(1,2,3).toString())


    val a = Seq(1,2,3)
    val b = Seq(1,2,3)
    assert(a == b)
    require(a == b)




  }


}
