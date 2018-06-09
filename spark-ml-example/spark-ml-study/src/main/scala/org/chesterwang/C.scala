package org.chesterwang

import scala.util.{Failure, Success, Try}

/**
  * Created by chester on 17-1-15.
  */
object C {
  def main(args: Array[String]) {

    val a = "3"
    val b = Try{
      a.toInt
    }
    val c = b match {
      case y:Success[_] => y.value
      case x:Failure[_] => x.exception.getMessage
    }
    println(c)


  }

}
