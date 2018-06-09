package org.chesterwang.spark.df

import play.api.libs.json._

/**
  * Created by chester on 16-12-9.
  */
object Json4s {
  def main(args: Array[String]) {



    implicit  val ChildFormat = Json.format[Child]
//    val child =Json.parse("{}").asOpt[Child]
    val child =Json.parse("""{"age":4,"name":"asdf"}""").asOpt[Child]
    println(child)
    println(child.map(x => x.age).map(_ + 1))
//    val writer = Json.writes[Child]
//    println(writer.writes(child.get))
    println(Json.toJson(child).toString())


  }

  case class Child(age:Int,name:String)

}
