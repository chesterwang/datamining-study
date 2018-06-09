package org.chesterwang.spark.df.udfTest

import org.apache.spark.sql.{Row, SQLContext}
import org.chesterwang.spark.df.util.LocalSparkContext
import org.apache.spark.sql.functions._
import com.fasterxml.jackson.annotation.{JsonCreator, JsonProperty}
import com.fasterxml.jackson.databind.{DeserializationFeature, ObjectMapper}
import org.apache.spark.sql.types.{IntegerType, StructField, StructType}

import scala.collection.mutable
import scala.collection.JavaConversions._

/**
  * Created by chester on 17-4-7.
  */
object UdfTest {

  implicit val sqlContext = LocalSparkContext.getLocalSQLContext("DataFrame2Map")

  import sqlContext.implicits._

  def main(args: Array[String]) {
    arrayUdfTest()

  }


  /**
    * 含有array类型的udf
    */
  def arrayUdfTest(): Unit = {

    case class AlbumId @JsonCreator()(@JsonProperty("id") id:Int)
    class MetaIdInfoList extends java.util.ArrayList[AlbumId]
    val parser = new ObjectMapper().reader(classOf[MetaIdInfoList])

    val arrayudf = (x:String) => {
      parser.readValue(x).asInstanceOf[java.util.List[AlbumId]]
        .map(ele => ele.id)
    }

    sqlContext.udf.register("arrayudf",arrayudf)

    val df = sqlContext.read.json("/home/chester/gitlab.chesterwang.org/spark-ml-example/spark-ml-study/src/main/resources/hh.json")
    df.show(10,false)

    df.select("returnMap.response.docs").show(10,false)
    df.selectExpr("arrayudf(returnMap.response.docs)").show(10,false)



  }
}
