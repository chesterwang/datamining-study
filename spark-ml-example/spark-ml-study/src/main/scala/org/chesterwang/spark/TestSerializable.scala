package org.chesterwang.spark

import org.chesterwang.spark.df.util.LocalSparkContext
import org.apache.spark.sql.functions._

/**
  * Created by chester on 17-5-24.
  */
object TestSerializable {

  var a:A = new A(1)

  def main(args: Array[String]): Unit = {

    implicit val sqlContext = LocalSparkContext.getLocalSQLContext("DataFrame2Map")

//    a = new A(3)
    val b = new A(5)

    val df = sqlContext.createDataFrame(Seq((1,2),(3,4))).toDF("a","b")

    df.withColumn("c",udf((x:Int) => x+b.i).apply(col("a"))).show(10)

  }

}

class A(val i:Int){

}
