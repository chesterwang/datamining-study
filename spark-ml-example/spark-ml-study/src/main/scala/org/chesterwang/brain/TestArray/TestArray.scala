package org.chesterwang.brain.TestArray

/**
  * Created by chester on 16-12-10.
  */
object TestArray {

  def main(args: Array[String]) {
    collect()

  }

  def collect(): Unit ={
    val a = Array(1,2,3)
    assert(
    a.collect{
      case 3 => "this is 2"
    } == Array("this is 2")
    )


  }

}
