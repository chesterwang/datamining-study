package org.chesterwang.spark.graphx

import org.apache.spark.graphx.{Edge, Graph, VertexId}
import org.apache.spark.{SparkConf, SparkContext}
import org.apache.spark.rdd.RDD

/**
  * Created by chester on 16-11-23.
  */
object GraphxApi {
  def main(args: Array[String]) {

    val conf = new SparkConf().setAppName("ALSExample").setMaster("local[*]")
    val sc = new SparkContext(conf)
    sc.setLogLevel("ERROR")


    val users: RDD[(VertexId, (String, String))] =
      sc.parallelize(
        Array(
          (3L, ("rxin", "student")),
          (7L, ("jgonzal", "postdoc")),
          (5L, ("franklin", "prof")),
          (2L, ("istoica", "prof")),
          (4L, ("peter", "student"))
        )
      )
    // Create an RDD for edges
    val relationships: RDD[Edge[String]] =
      sc.parallelize(
        Array(
          Edge(3L, 7L, "collab"),
          Edge(5L, 3L, "advisor"),
          Edge(2L, 5L, "colleague"),
          Edge(5L, 7L, "pi"),
          Edge(4L, 0L, "student"),
          Edge(5L, 0L, "colleague")
        )
      )
    // Define a default user in case there are relationship with missing user
    val defaultUser = ("John Doe", "Missing")
    val graph = Graph(users,relationships,defaultUser)
    graph.triplets.map(
      triplet => s"${triplet.srcAttr._1} is the ${triplet.attr} of ${triplet.dstAttr._1}"
    ).collect().foreach(println)
    val validGraph = graph.subgraph(vpred = (id,attr) => attr._2 != "Missing")
    validGraph.vertices.collect.foreach(println(_))
    validGraph.triplets.map(
      triplet => triplet.srcAttr._1 + " is the " + triplet.attr + " of " + triplet.dstAttr._1
    ).collect.foreach(println(_))

    graph.connectedComponents().triplets.map(
      triplet => triplet.srcAttr
    ).collect.foreach(println(_))
  }

}
