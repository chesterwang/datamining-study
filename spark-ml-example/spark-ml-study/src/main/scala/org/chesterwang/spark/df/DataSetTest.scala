package org.chesterwang.spark.df

import org.chesterwang.spark.df.util.LocalSparkContext
import org.apache.spark.sql.functions._

/**
  * Created by chester on 17-8-4.
  */
object DataSetTest {

  implicit val sqlContext = LocalSparkContext.getLocalSQLContext("DataFrame2Map")

  def main(args: Array[String]): Unit = {
//    val ds = sqlContext.createDataset(Seq(1,2,3))

    val df = sqlContext.createDataFrame(Seq((1,2),(3,4)))
    .toDF("a","b")

    val p0 = df.withColumn("hh",struct(col("a"),col("b")))

    val p1 = df.withColumn("hh",lit(null).cast(p0.schema("hh").dataType))

    p0.show(10)
    p1.show(10)


    p0.printSchema()
    p1.printSchema()

    p0.union(p1).show(100)







  }

  def test1(): Unit ={
//    sqlContext.sparkContext.parallelize(Seq(LabeledPoint()))

  }

}
