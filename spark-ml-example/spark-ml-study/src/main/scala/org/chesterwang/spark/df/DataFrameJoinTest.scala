package org.chesterwang.spark.df

import org.apache.spark.sql.{Row, SQLContext}
import org.chesterwang.spark.df.util.LocalSparkContext
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types.StringType

import scala.collection.mutable

/**
  * Created by chester on 17-2-18.
  */
object DataFrameJoinTest {

  implicit val sqlContext = LocalSparkContext.getLocalSQLContext("DataFrame2Map")

  import sqlContext.implicits._

  def main(args: Array[String]) {

    val df = sqlContext.createDataFrame(Array[(String,Int)]((null,1),("2",2)))

    df.show(10)

    df.where(
        not(col("_1").equalTo(col("_2")))
    ).show(10)

    df.where(
      not(col("_2").equalTo(col("_1")))
    ).show(10)

    df.where(
      (col("_1").isNull and col("_2").isNotNull) or
        (col("_2").isNull and col("_1").isNotNull) or
        not(col("_1").equalTo(col("_2")))
    ).show(10)

  }
}
