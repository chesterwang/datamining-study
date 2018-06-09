package org.chesterwang.brain

import scala.util.parsing.json.JSON
import scala.util.parsing.json.JSONObject

/**
* Created by chester on 16-12-21.
*/
object MapJson {
def main(args: Array[String]) {
  test2()

}

  def test(): Unit ={
    //失败

//    implicit  val ChildFormat = Json.format[Map[String,String]]
//    val child =Json.parse("""{"age":4,"name":"asdf"}""").asOpt[Map[String,String]]
//    println(child)
//    println(child.map(x => x.get("age").get))
//    println(Json.toJson(child).toString())

  }
  def test2(): Unit ={
    JSON.parseFull("""{"age":4,"name":"asdf"}""") match {
      case Some(map:Map[String, Any]) => println(map)
      case _ => println("Parsing failed")
    }
    println(JSONObject(Map("3" -> 4)))

  }
}
