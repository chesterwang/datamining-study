package org.chesterwang.spark.df.parseJson

/**
  * Created by chester on 16-12-10.
  */
import com.fasterxml.jackson.annotation.{JsonCreator, JsonProperty}
import com.fasterxml.jackson.databind.ObjectMapper
import org.apache.spark.sql.SQLContext
import org.apache.spark.{SparkConf, SparkContext}
import org.apache.spark.sql.functions._

import scala.beans.BeanProperty

/**
  * Created by chester on 16-12-10.
  */
object JacksonParserCaseClass {
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
    val reader = mapper.reader(classOf[Array[MetaIdInfo2]])
    val MetaIdInfo2Parser = (x:String) => {
      reader.readValue(x).asInstanceOf[Array[MetaIdInfo2]]
    }

    df.select(
      col("*"),
      udf[String, String](
        x =>
        MetaIdInfo2Parser(x)
        .flatMap(x => x.metadataValueList.map(y => x.metadataName + ":" +y.metadataValue))
        .mkString(",")
      ).apply(col("metaInfo"))
    ).show(10,truncate = false)

  }

}


//这种方法可行 但是在正式集群上不可行 报错是PropertyBasedCreator无法序列化
//case class MetaIdInfo2 (@JsonProperty("metadataId") metadataId:Int,
//                                     @JsonProperty("metadataName") metadataName:String,
//                                     @JsonProperty("displayName") displayName:String,
//                                     @JsonProperty("metadataValueList") metadataValueList:Array[MetaValueInfo2])
//case class MetaValueInfo2 (@JsonProperty("metadataValueId") metadataValueId:Int,
//                                         @JsonProperty("displayValue") displayValue:String,
//                                         @JsonProperty("metadataValue") metadataValue:String)



class MetaIdInfo2{

  @BeanProperty
  var metadataId:Int =_
  @BeanProperty
  var metadataName:String =_
  @BeanProperty
  var displayName:String=_
  @BeanProperty
  var metadataValueList:Array[MetaValueInfo2] = _

}
class MetaValueInfo2{
  @BeanProperty
  var metadataValueId:Int =_
  @BeanProperty
  var displayValue:String =_
  @BeanProperty
  var metadataValue:String =_
}


//这种方式不行
//case class MetaIdInfo2 (metadataId:Int,
//                        metadataName:String,
//                        displayName:String,
//                        metadataValueList:Array[MetaValueInfo])
//case class MetaValueInfo2 (metadataValueId:Int,
//                           displayValue:String,
//                           metadataValue:String)
//
//class MetaIdInfoList2 extends java.util.ArrayList[MetaIdInfo2]

//这种也不行
//case class MetaIdInfo2 @JsonCreator (@JsonProperty("metadataId") metadataId:Int,
//                        @JsonProperty("metadataName") metadataName:String,
//                        @JsonProperty("displayName") displayName:String,
//                        @JsonProperty("metadataValueList") metadataValueList:Array[MetaValueInfo])
//case class MetaValueInfo2 @JsonCreator (@JsonProperty("metadataValueId") metadataValueId:Int,
//                           @JsonProperty("displayValue") displayValue:String,
//                           @JsonProperty("metadataValue") metadataValue:String)
//
//class MetaIdInfoList2 extends java.util.ArrayList[MetaIdInfo2]


//这种方法也可行
//@JsonIgnoreProperties(ignoreUnknown = true)
//class MetaIdInfo{
//
//  @BeanProperty
//  var metadataId:Int =_
//  @BeanProperty
//  var metadataName:String =_
//  @BeanProperty
//  var displayName:String=_
//  @BeanProperty
//  var metadataValueList:Array[MetaValueInfo] = _
//
//}
//@JsonIgnoreProperties(ignoreUnknown = true)
//class MetaValueInfo{
//  @BeanProperty
//  var metadataValueId:Int =_
//  @BeanProperty
//  var displayValue:String =_
//  @BeanProperty
//  var metadataValue:String =_
//}


//这种方法也可行
//  case class MetaIdInfo (@JsonProperty("metadataId") metadataId:Int,
//                         @JsonProperty("metadataName") metadataName:String,
//                         @JsonProperty("displayName") displayName:String,
//                         @JsonProperty("metadataValueList") metadataValueList:Array[MetaValueInfo])
//  case class MetaValueInfo (@JsonProperty("metadataValueId") metadataValueId:Int,
//                            @JsonProperty("displayValue") displayValue:String,
//                            @JsonProperty("metadataValue") metadataValue:String)
