package org.chesterwang.spark.df.parseJson

import com.fasterxml.jackson.databind.ObjectMapper
import org.apache.spark.sql.SQLContext
import org.apache.spark.sql.functions._
import org.apache.spark.{SparkConf, SparkContext}

import scala.beans.BeanProperty

/**
  * Created by chester on 16-12-10.
  */
object JacksonParser {
  def main(args: Array[String]) {
    val conf = new SparkConf().setAppName("test jackson parser")
      .setMaster("local[*]")

    val sc = new SparkContext(conf)

    val sqlContext = new SQLContext(sc)

    val df = sqlContext.createDataFrame(List(
      """[{"metadataId":19,"metadataName":"内容","displayName":"内容","metadataValueList":[{"metadataValueId":1006,"displayValue":"疾病预防","metadataValue":"疾病预防"},{"metadataValueId":215,"displayValue":"心理","metadataValue":"心理"}]}]"""
    ).map(Tuple1.apply))
      .toDF("metaInfo")

    val mapper = new ObjectMapper();
    val reader = mapper.reader(classOf[MetaIdInfoList])

    df.select(
      col("*"),
      udf[String, String](x => reader.readValue(x).asInstanceOf[MetaIdInfoList].toString)
        .apply(col("metaInfo"))
    ).show(10,truncate = false)


  }

}


class MetaIdInfo() {

  @BeanProperty
  var metadataId: Int = _
  @BeanProperty
  var metadataName: String = _
  @BeanProperty
  var displayName: String = _
  @BeanProperty
  var metadataValueList:Array[MetaValueInfo] = _
}

case class MetaValueInfo() {

  @BeanProperty
  var metadataValueId: Int = _
  @BeanProperty
  var displayValue: String = _
  @BeanProperty
  var metadataValue:String = _

}

class MetaIdInfoList extends java.util.ArrayList[MetaIdInfo]
