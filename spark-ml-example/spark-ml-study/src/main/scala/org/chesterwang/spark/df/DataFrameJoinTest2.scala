package org.chesterwang.spark.df

import org.apache.spark.mllib.linalg.Vectors
import org.apache.spark.mllib.linalg.{Vector => MLVector}
import org.apache.spark.sql.functions._
import org.chesterwang.spark.df.util.LocalSparkContext

/**
  * Created by chester on 17-2-18.
  */
object DataFrameJoinTest2 {

  implicit val sqlContext = LocalSparkContext.getLocalSQLContext("DataFrame2Map")

  def main(args: Array[String]) {

    val df = sqlContext.createDataFrame(Array[(String,Int)]((null,1),("2",2))).toDF("x","y")

    val df2 = df.withColumn("a",udf((y:Int) => Vectors.sparse(5,Array(2),Array(y))).apply(col("y")))
    df2.show(100)

    df2.withColumn("xxxll",udf((x:MLVector) => x.apply(2)).apply(col("a"))).show(100)

    df.rdd.map(row => row.getAs[Any]("x")).take(10).foreach(println)

  }
}
