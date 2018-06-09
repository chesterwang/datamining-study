package org.chesterwang.spark.python

import org.apache.spark.deploy.SparkSubmit

/**
  * Created by chester on 17-2-22.
  */
object SparkPython {

  def main(args: Array[String]) {
    SparkSubmit.main(
      Array(
        "--master",
        "local[*]",
        "--py-files",
        "/opt/spark-1.6.1-bin-hadoop2.6/python/lib/py4j-0.9-src.zip,/opt/spark-1.6.1-bin-hadoop2.6/python",
//        "/home/chester/a.py"
        "/tmp/a.py"
      )
    )
  }

}
