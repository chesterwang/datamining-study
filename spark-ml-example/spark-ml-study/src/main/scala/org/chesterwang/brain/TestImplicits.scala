package org.chesterwang.brain

import org.apache.spark.mllib.linalg.SparseVector
import org.apache.spark.mllib.regression.LabeledPoint
import org.apache.spark.{SparkConf, SparkContext}
import org.apache.spark.sql.{DataFrame, SQLContext}
import org.apache.spark.sql.functions._

/**
  * Created by chester on 17-6-5.
  */
object TestImplicits {

  def main(args: Array[String]): Unit = {


    val conf = new SparkConf().setAppName("h").setMaster("local[*]")
    implicit val sc = new SparkContext(conf)
//    test()
    sc.setLogLevel("WARN")

    val sqlContext =new SQLContext(sc)

    val df = sqlContext.createDataFrame(Array((1,2),(2,3))).toDF("hh","yy")

    df.rollup("hh","yy")
    .agg(count("*"))
    .show(10)


//    test2(df)



  }


  def test()(implicit sc:SparkContext): Unit ={
    sc.parallelize(Array(1,2,3)).collect().foreach(println)

    val sqlContext =new SQLContext(sc)

    val df = sqlContext.read.text("/home/chester/java_error_in_PYCHARM_30915.log,/home/chester/getui.csv")

    df.show(100)

  }

  def test2(df:DataFrame): Unit ={

    val df2 = df.withColumn("labeledpoint",
      udf((x:Int) =>
       if(x == 1) LabeledPoint(null.asInstanceOf[Double],null)
       else LabeledPoint(1,new SparseVector(10,Array(1),Array(0.1)))
      ).apply(col("hh"))
    )

    df2.show(100,false)

    df2.filter(col("labeledpoint").isNotNull).show(100,false)
    df2.filter(col("labeledpoint.label").isNotNull).show(100,false)
    df2.filter(col("labeledpoint.features").isNotNull).show(100,false)


    df2.filter(
      col("labeledpoint").isNotNull and
        col("labeledpoint.label").isNotNull and
      col("labeledpoint.features").isNotNull).show(100,false)

  }

}
