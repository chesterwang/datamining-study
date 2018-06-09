package org.chesterwang.brain.TestArray

import org.scalatest.{FunSuite, Matchers}

import scala.collection

/**
  * Created by chester on 16-12-11.
  */
class TestArray$Test extends FunSuite with Matchers {

  val arr = Array[Int](3, 2, 1, 5, 9, 0, 2)
  val emptyArr = Array[Int]()
  val arrSmall = Array[Int](3, 2, 1)

  test("apply") {
    assert(arr.apply(3) == 5)
  }

  test("aggregate") {
    val result = arr.aggregate("")(seqop = (x, int) => x + int.toString, combop = (x, y) => x + y)
    assert(result == arr.mkString(""))
  }
  test("collect") {
    val result = arr.collect { case x: Int if x % 2 == 0 => x }
    result should be(Array(2, 0, 2))
  }

  test("collectFirst") {
    val result = arr.collectFirst { case x: Int if x % 2 == 0 => x }
    result should be(Some(2))
    val result2 = emptyArr.collectFirst { case x: Int if x % 2 == 0 => x }
    result2 should be(None)
  }
  test("combinations") {
    val result = arrSmall.combinations(2)
    result.toArray should be ( Array(Array(3, 2), Array(3, 1), Array(2, 1)))
  }
  test("contains"){
    arr.contains(3) should be(true)
  }
  test("containsSlice"){
    arr.containsSlice(Array(2,1)) should be(true)
  }
  test("copyToArray"){
    //将原array移动到另一个array的区段中
    val toArray = Array[Int](-1,-1,-1)
    arr.copyToArray(toArray,1,2)
    toArray should be(Array(-1,3,2))
  }
  test("corresponds"){
    val result =arrSmall.corresponds(Array(6,4,2)){(x,y) => x*2 == y}
    result should be(true)
  }
  test("count"){
    val result =arrSmall.count(x => x % 2 == 0)
    result should be(1)
  }


}
