/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.chesterwang.spark.model

import breeze.util.TopK
import org.apache.spark.sql.SparkSession
import org.apache.spark.{SparkConf, SparkContext}
// $example on$
import org.apache.spark.ml.feature.Binarizer
// $example off$
import org.apache.spark.sql.{DataFrame, SQLContext}

object BinarizerExample {
  def main(args: Array[String]): Unit = {
//    val conf = new SparkConf().setAppName("BinarizerExample").setMaster("local[1]")
//    val sc = new SparkContext(conf)
//    sc.setLogLevel("ERROR")
//    val sqlContext = SparkSession.builder().master("local[1]").getOrCreate()

    // Load training data
//    val training =sqlContext
//      .read
//      .format("libsvm")
//      .load("/home/chester/gitlab.chesterwang.org/spark-ml-example/data/mllib/sample_multiclass_classification_data.txt")
//
//    training.show(100)

//    val df = sqlContext.createDataFrame(List(
//      (1,2),
//      (3,null.asInstanceOf[Int]),
//      (3,null.asInstanceOf[Int])
//    )).toDF("a","b")
//    df.show(100)

    val a = Array(8,2,3).zipWithIndex

    TopK(3,a)(Ordering.by[Tuple2[Int,Int],Int](x => x._1))
    .foreach(println)


  }
}
