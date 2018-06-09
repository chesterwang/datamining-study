package org.chesterwang.spark.df

import com.fasterxml.jackson.annotation.{JsonCreator, JsonProperty}
import com.fasterxml.jackson.databind.{DeserializationFeature, ObjectMapper}

import scala.beans.BeanProperty

/**
  * Created by chester on 16-12-7.
  */

case class MetaIdInfo @JsonCreator()(@JsonProperty("metadataId") metadataId:Int,
                                     @JsonProperty("metadataName") metadataName:String,
                                     @JsonProperty("displayName") displayName:String,
                                     @JsonProperty("metadataValueList") metadataValueList:Array[MetaValueInfo])
case class MetaValueInfo @JsonCreator() (@JsonProperty("metadataValueId") metadataValueId:Int,
                         @JsonProperty("displayValue") displayValue:String,
                         @JsonProperty("metadataValue") metadataValue:String)

class MetaIdInfoList extends java.util.ArrayList[MetaIdInfo]


object JacksonParser {



  def main(args: Array[String]) {


//    val a = """[{"metadataId":19,"metadataName":"内容","displayName":"内容","metadataValueList":[{"metadataValueId":1006,"displayValue":"疾病预防","metadataValue":"疾病预防"},{"metadataValueId":215,"displayValue":"心理","metadataValue":"心理"}]}]"""
//    val mapper = new ObjectMapper();
//    val valueType = mapper.getTypeFactory.constructCollectionType(classOf[java.util.List[_]], classOf[MetaIdInfo])
//    val mm= mapper.readValue(a, valueType).asInstanceOf[java.util.List[MetaIdInfo]]
//    println(mm)



    val a = """[{"metadataId":19,"metadataName":"内容","displayName":"内容","metadataValueList":[{"metadataValueId":1006,"displayValue":"疾病预防","metadataValue":"疾病预防"},{"metadataValueId":215,"displayValue":"心理","metadataValue":"心理"}]}]"""
    val mapper = new ObjectMapper();
    val mm= mapper.readValue(a, classOf[MetaIdInfoList]).asInstanceOf[java.util.List[MetaIdInfo]]
    println(mm)

    val reader = mapper.reader(classOf[MetaIdInfoList])
    println(reader.readValue(a).getClass)

  }



}


