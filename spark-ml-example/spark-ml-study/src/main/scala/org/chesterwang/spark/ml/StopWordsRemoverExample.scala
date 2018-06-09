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

// scalastyle:off println
package org.chesterwang.spark.ml

import org.apache.spark.{SparkConf, SparkContext}
// $example on$
import org.apache.spark.ml.feature.StopWordsRemover
// $example off$
import org.apache.spark.sql.SQLContext

object StopWordsRemoverExample {
  def main(args: Array[String]): Unit = {
    val conf = new SparkConf().setAppName("StopWordsRemoverExample").setMaster("local[*]")
    val sc = new SparkContext(conf)
    sc.setLogLevel("ERROR")
    val sqlContext = new SQLContext(sc)

    // $example on$
    val remover = new StopWordsRemover()//tongpeng:默认英文停止词
      .setInputCol("raw")
      .setOutputCol("filtered")

    val dataSet = sqlContext.createDataFrame(Seq(
      (0, Seq("I", "saw", "the", "red", "baloon")),
      (1, Seq("Mary", "had", "a", "little", "lamb"))
    )).toDF("id", "raw")

    remover.transform(dataSet).show()
    // $example off$
    sc.stop()
  }
}
// scalastyle:on println
