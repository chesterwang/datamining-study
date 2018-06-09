package org.chesterwang.spark.df

import org.apache.spark.sql.{Row, SQLContext}
import org.apache.spark.{SparkConf, SparkContext}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.{DataFrame }


/**
  * Created by chester on 17-7-4.
  */
object Test {
  def main(args: Array[String]): Unit = {

    val conf = new SparkConf().setAppName("a").setMaster("local[*]")
    val sc = new SparkContext(conf)
    val sqlContext = new SQLContext(sc)
    import sqlContext.implicits._

    val df = sqlContext.createDataFrame(Array(1,2,3).map(Tuple1.apply)).toDF("p")
    val df2 = sqlContext.createDataFrame(Array(1 -> "asdf",2 -> "a32d",3 -> "98jpo")).toDF("k","v")

    val mm = sc.broadcast(df2.collect().map(row => row.getAs[Int]("k") -> row).toMap)


    val rdd = df.rdd.map(row => {
      val k = row.getAs[Int]("p")
      val row2 = mm.value.get(k).get
      val row3 = Row.merge(row,row2)
      row3.schema
      row3
    })

//    rdd.toDF()

//    df.withColumn("h",udf((x:Int) => mm.value.get(x).get).apply(col("p")))
//    .show(10)



  }

}
