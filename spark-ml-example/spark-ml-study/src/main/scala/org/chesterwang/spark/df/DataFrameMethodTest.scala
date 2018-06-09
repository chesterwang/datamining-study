package org.chesterwang.spark.df

import org.apache.spark.sql.{Row, SQLContext}
import org.chesterwang.spark.df.util.LocalSparkContext
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types.StringType

import scala.collection.mutable

/**
  * Created by chester on 17-2-18.
  */
object DataFrameMethodTest {

  implicit val sqlContext = LocalSparkContext.getLocalSQLContext("DataFrame2Map")

  import sqlContext.implicits._

  def main(args: Array[String]) {

    //1. dataframe create
    //    arraytupletuple
    //    createDf()
    //    testGetWildCardFiles()
    //    emptyDataFrame
    //    emptyDataFrame2()

    //2. 列操作
    //    withColumn()
    //    selectColumn
    //    columnCompare()
    //    dfLeftJoin()
    //    nullValueJoin
    //    orderDf()
    //    groupCount()
    //    collectSetCol()
    //    explodeCol

    //3. udf
    //    userDefinedType
    //    arrayUdf()
    //    rowArray()
    //    mapTypeColumn()

    //4. struct字段操作
    //    structTuple
    //    structParameter
    //    outputStruct
    //    structModify
    //    struct2Map
    rowGetAfterStruct


  }

  /**
    * 含有array类型的udf
    */
  def arrayUdf(): Unit = {
    sqlContext.udf.register("flat_concat_json",
      (x: mutable.WrappedArray[String]) => x.mkString(",")
      //      (x: Seq[String]) => x.mkString(",")//也可以
      //      (x: Array[String]) => x.mkString(",")//报错
    )
    val data = Array(Some(-3), None)
    val df = sqlContext.createDataFrame(data.map(Tuple1.apply)).toDF("features")
    val newdf = df.selectExpr("""flat_concat_json(array("a","b")) as hh""")
    newdf.printSchema()
    newdf.show(10)

    val initial_df = sqlContext.createDataFrame(Array(Tuple1(Array(1, 2)))).toDF("id")
    initial_df.printSchema()
    initial_df.show(10)

    //1. seq
    initial_df
      .withColumn("hh", udf((x: Seq[Int]) => x.sum).apply($"id"))
      .show(10)

    //2. wrappedArray
    initial_df
      .withColumn("hh", udf((x: mutable.WrappedArray[Int]) => x.sum).apply($"id"))
      .show(10)

  }

  /**
    * 文件操作
    */
  def testGetWildCardFiles(): Unit = {
    val data = Array(Some(-3), None)
    val df = sqlContext.read.text("/tmp/*.sql")
    df.show(100)

    val opts = Map[String, String](
      "header" -> "true",
      "delimiter" -> "\t"
    )
    val df2 = sqlContext.read.format("com.databricks.spark.csv")
      .options(opts).load("/tmp/hh/{a,c}")
    df2.show(10)

  }

  /**
    * sort = orderby
    * sortWithinPartitions = 类型与sql的sortby
    *
    */
  def orderDf(): Unit = {
    val df = sqlContext.createDataFrame(
      Array(2, 1).map(Tuple1.apply)
    ).toDF("h")
    df.orderBy("h")
      .show(10)
    df.sort("h").show(10)
    df.sortWithinPartitions("h").show(10)
  }


  /**
    * struct字段转化为map,或者整个Row转化为一个RDD[Map]
    */
  def struct2Map(): Unit = {
    val df = sqlContext.createDataFrame(
      Array((1, 2), (3, 4))
    ).toDF("a", "b").withColumn("merge", struct("a", "b"))
    //dataframe,必须要求子字段是同类型,不要要强转为统一类型
    df.withColumn("merge_map",
      udf[Map[String, Int], Row](
        x => x.getValuesMap[Int](x.schema.fieldNames)
      ).apply($"merge")
    ).show(10)
    //rdd
    df.rdd.map(
      row => {
        val struct_field = row.getAs[Row]("merge")
        struct_field.getValuesMap[String](struct_field.schema.fieldNames)
      }
    ).take(10).foreach(println)
  }

  /**
    * 创建dataframe
    */
  def createDf(): Unit = {
    val data = Array(-3, -0.5, -0.3)

    //rdd
    val rdd = sqlContext.sparkContext.parallelize(data.map(Tuple1.apply))
    sqlContext.createDataFrame(rdd).toDF("hh").show(10)
    //seq(array 到 seq的隐式转换)
    val df = sqlContext.createDataFrame(data.map(Tuple1.apply)).toDF("features").show(10)

    //这种方法还没有探索清楚
    case class tmp_class(a: Int, b: Int)
    val rdd2 = sqlContext.sparkContext.parallelize(Array((4, 1)))
    sqlContext.createDataFrame(rdd2, classOf[tmp_class]).show(10)

  }

  def groupCount(): Unit = {
    val df = sqlContext.createDataFrame(
      Array((2, 1), (2, 1), (3, 4))
    ).toDF("h", "b")
    df.groupBy("h")
      .agg(count("*"))
      .show(10)

    df.groupBy("h").agg(count("b"), sum("b"), mean("b")).show(10)

    //mean方法说明,其他max/min/sum/avg/都类似
    //    Compute the mean value for each numeric columns for each group.
    // The resulting DataFrame will also contain the grouping columns.
    // When specified columns are given, only compute the mean values for them.
    df.groupBy("h").mean().show(10)
  }

  //todo
  def groupFlat(): Unit = {

    val df = sqlContext.createDataFrame(
      Array(
        (1, 2, 3),
        (3, 2, 3),
        (1, 9, 3)
      )
    ).toDF("h", "x", "y")
    val a = df.groupBy("h")
  }

  /**
    * map类型的列进行udf输入和输出操作
    */
  def mapTypeColumn(): Unit = {
    val df = sqlContext.createDataFrame(
      Array(Tuple1(1), Tuple1(3), Tuple1(1))
    ).toDF("h")


    //输出
    val df2 = df.withColumn("mm",
      udf[Map[Int, Int], Int] {
        (x: Int) =>
          Map(x -> 1)
      }.apply($"h")
    )
    df2.show(10)
    df2.printSchema()

    //输入
    df2.withColumn("mmm", udf((mm: Map[Int, Int]) => mm.getOrElse(1, -1)).apply($"mm")).show(10)
  }

  /**
    * null value join的时候 null === null 是为true的,可以join成功
    */
  def nullValueJoin(): Unit = {
    val df = sqlContext.createDataFrame(
      Array(null, "2", "3").map(Tuple1.apply)
    ).toDF("id")
    df.printSchema()
    df.show(10)
    val joindf = df.join(df, df("id") === df("id"), "left")
    joindf.printSchema()
    joindf.show(10)
  }

  /**
    * 自定义类型支持
    * 具体类型支持需要看代码 ScalaReflection.schemaFor 方法
    * 1. SQLUserDefinedType注解类(Vectors/Matrices)
    * 2. Option[_]
    * 3. 容器类型 Array[_] Seq[_] Map[_]
    * 4. Product[_] (所有的case class/tuple) 内部实现是StructType
    * 5. 基础类型string/double/int/long/byte/float/short/boolean
    * 6. 时间 timestampe/date
    */
  def userDefinedType(): Unit = {

    val df = sqlContext.createDataFrame(Array((1, 2), (3, 4))).toDF("a", "b")
    try {

      df.select(
        udf[Personas, Int, Int]((a, b) => new Personas().addPersona(a, b))
          .apply($"a")
      ).show(10)

    } catch {
      case e: Exception => println("不支持Persona这种类型")
    }

    df.select(
      udf[PersonasObject, Int, Int]((a, b) => PersonasObject(a, b))
        .apply($"a", $"a").as("PersonasObject")
    ).show(10)
  }

  /**
    * withColumn添加列的几种形式
    */
  def withColumn(): Unit = {

    val df = sqlContext.createDataFrame(
      Array(null.asInstanceOf[String], "2", "3").map(Tuple1.apply)
    ).toDF("id")
    df.show(10)

    val df2 = sqlContext.createDataFrame(
      Array("h", "p").map(Tuple1.apply)
    ).toDF("a1")

    //1. 内置函数形式
    df.withColumn("co", lit(true)).show(10)
    //2. udf形式
    df.withColumn("co", udf[Int, Int] { x: Int => x + 1 }.apply(col("id"))).show(10)
    df.withColumn("co", udf { x: Int => x + 1 }.apply(col("id"))).show(10)
    //3. 原始列直接复制
    df.withColumn("co", col("id")).show(10)
  }

  /**
    * 判断一行中是否有空值
    */
  def anyNullColumn(): Unit = {

    val df = sqlContext.createDataFrame(
      Array(null.asInstanceOf[String], "2", "3").map(Tuple1.apply)
    ).toDF("id")
    df.show(10)

    df.withColumn("merge_cnt",
      udf[Boolean, Row] {
        x: Row => x.anyNull
      }.apply(col("merge"))
    ).show(10)

  }

  /**
    * select的几种形式
    */
  def selectColumn(): Unit = {

    val df = sqlContext.createDataFrame(
      Array(null.asInstanceOf[String], "2", "3").map(Tuple1.apply)
    ).toDF("id")
    df.show(10)

    //1. 所有列
    df.selectExpr("*").show(10)
    df.select($"*").show(10)
    //2. 列名 和函数混合
    df.selectExpr("id", "isnull(id)").show(10)
    df.select($"id", isnull($"id")).show(10)
    //3. select方法只能选择列名
    df.select("id").show(10)
    //4. struct内字段选择
    df.select(struct("id").as("hh"))
      .select("hh.id").show(10)

  }

  /**
    * 空df,未指定schema
    */
  def emptyDataFrame(): Unit = {
    val df = sqlContext.emptyDataFrame
    df.printSchema()
    df.show(10)
  }

  /**
    * 空df,但是指定了schema
    */
  def emptyDataFrame2(): Unit = {
    //    val df = sqlContext.emptyDataFrame.toDF("id")
    //    df.printSchema()
    val df = sqlContext.createDataFrame(Array[Tuple1[String]]()).toDF("id")
    df.printSchema()
    df.show(10)
  }

  def columnCompare(): Unit = {

    val df = sqlContext.createDataFrame(
      Array(("2", "4"), ("3", "3"))
    ).toDF("id", "id2")
    df.filter(df("id") =!= df("id2"))
      .show(10)
    val df2 = sqlContext.createDataFrame(
      Array((2.0, 4.0), (3.0, 3.0))
    ).toDF("id", "id2")
    df2.where(col("id") =!= col("id2"))
      .show(10)

  }

  /**
    * left join
    */
  def dfLeftJoin(): Unit = {
    val initial_df = sqlContext.createDataFrame(Array(Tuple1("hh"))).toDF("id")
    val right_df = sqlContext.createDataFrame(Array(Tuple1("hh"), Tuple1("hh2"))).toDF("id")
    val mainKey = "id"
    initial_df
      .join(right_df, initial_df.col("id") === right_df.col("id"), joinType = "outer")
      .show(10)

    initial_df
      .join(right_df, Seq("id"), joinType = "outer")
      .show(10)


  }

  /**
    * collect_list,在1.6的时候不支持对struct等复杂类型操作,2.0支持
    */
  def collectSetCol(): Unit = {
    val initial_df = sqlContext.createDataFrame(Array(Tuple2("1", "hh"))).toDF("id", "hh")
    initial_df.select(col("id"), struct("hh")).toDF("id", "hh_struct")
      .groupBy("id")
      .agg(col("id"), collect_list("hh_struct"), collect_set("hh_struct"))
      .show(10)


  }

  /**
    * Row中array字段的解析获取 seq方式
    */
  def rowArray(): Unit = {
    val initial_df = sqlContext.createDataFrame(Array(Tuple1(Array[Int](1, 2, 3)))).toDF("id")
    initial_df.show(10)
    //报错
    //    initial_df.map(x => x.getAs[mutable.WrappedArray[Int]]("id"))
    //      .take(10).foreach(println)
    initial_df.map(x => x.getAs[Seq[Int]]("id"))
      .take(10).foreach(println)

  }

  def udf2(): Unit = {
    val initial_df = sqlContext.createDataFrame(Array(Tuple1(Array[Int](1, 2, 3)))).toDF("id")
    initial_df.withColumn("", udf((x: Int, y: Int) => x + y).apply($"", $""))
  }

  /**
    * row.getAs[Map[Int,Int]]
    */
  def structTuple(): Unit = {
    val initial_df = sqlContext.createDataFrame(Array(Tuple1(Map(1 -> 2)))).toDF("id")
    initial_df.printSchema()
    initial_df.show(10)
    initial_df.rdd.map(row => row.getAs[Map[Int, Int]]("id"))
      .take(10).foreach(println)
  }

  /**
    * rdd[Tuple2] -> struct field
    */
  def arraytupletuple(): Unit = {
    val initial_df = sqlContext.createDataFrame(Array(Tuple1(Tuple2(1, 2)))).toDF("id")
    initial_df.printSchema()
    initial_df.show(10)
    initial_df
  }

  /**
    * explode column
    */
  def explodeCol(): Unit = {
    val initial_df = sqlContext.createDataFrame(Array(Tuple2(1, Array[String]("a,b", "a,b", "a,b")))).toDF("id", "vv")
    val a = initial_df.withColumn("vvs", explode($"vv"))
      .withColumn("a", split($"vvs", ",").apply(0))
      .withColumn("b", split($"vvs", ",").apply(1))
      .withColumn("c", lit(3))
    a.show(10)
    a.selectExpr("concat(a,c)").show(10)

  }

  def arrayudf(): Unit = {
    val initial_df = sqlContext.createDataFrame(Array(Tuple1(Array(1, 2)))).toDF("id")
    initial_df.printSchema()
    initial_df.show(10)
    initial_df
      .withColumn("hh", udf((x: Seq[Int]) => x.sum).apply($"id"))
      .show(10)
  }

  /**
    * struct字段作为整体进行操作,即struct字段整体作为udf输入参数
    * 以及多层struct字段的解析
    */
  def structParameter(): Unit = {
    val df = sqlContext.createDataFrame(Array((1, 2, 3), (4, 5, 5)))
      .toDF("a", "b", "c")
    df.show(10)

    val newdf = df.withColumn("ss", struct(col("a"), col("b")))
    newdf.show(10)

    //一层struct,但这里是整体操作
    println("一层struct")
    newdf.withColumn("fun",
      udf[Int, Row](x => x.getAs[Int]("a")).apply(col("ss"))
    ).show(10)
    newdf.withColumn("fun",
      udf[Int, Int](x => x).apply(col("ss.a"))
    ).show(10)


    //二层struct
    println("二层struct")
    val newdf2 = df.withColumn("ss", struct(col("a"), col("b")))
      .withColumn("sss", struct(col("ss"), col("ss").as("ss2"))) //临时改换名字,小技巧
    newdf2.show(10)
    newdf2.printSchema()

    //二层struct进行整体操作
    val newdf3 = newdf2.withColumn("ssss", udf[Int, Row](row =>
      row.getAs[Row]("ss").getAs[Int]("a")
    ).apply(col("sss")))
    newdf3.show(10)
  }

  /**
    * 输出为struct类型,但是输出struct类型的name无法控制
    */
  def outputStruct(): Unit = {
    val df = sqlContext.createDataFrame(Array((1, 2, 3), (4, 5, 5)))
      .toDF("a", "b", "c")
    df.show(10)

    //无法即时命名
    val newdf = df.withColumn("xx",
      udf[(Int, Int), Int](x => (x, x)).apply(col("a"))
    ) //.withColumnRenamed("_1","xx.a")
    newdf.show(10)
    newdf.printSchema()
    newdf.withColumnRenamed("xx._1", "asdf").printSchema()
    newdf.select("xx._1").show(10)

  }

  /**
    * struct的一些操作
    */
  def structModify(): Unit = {
    val df = sqlContext.createDataFrame(Array((1, 2, 3), (4, 5, 5)))
      .toDF("a", "b", "c").withColumn("xx", struct($"c", $"b"))
      .withColumn("yy", struct($"a", $"b"))
    df.show(10)
    val newdf = df.withColumn("yy", struct(
      coalesce(col("xx.c"), col("yy.a")).as("a"),
      coalesce(col("xx.b"), col("yy.b")).as("b")
    )
    )
    newdf.show(10)

    newdf.printSchema()

  }

  def rowGetAfterStruct(): Unit ={

    val df = sqlContext.createDataFrame(Array((1, 2, 3), (4, 5, 5)))
      .toDF("a", "b", "c")
      .withColumn("xx", struct(col("c"), $"b"))
      .withColumn("yy", struct($"a", $"b"))
      .withColumn("ccc", struct($"xx", $"yy"))
      .withColumnRenamed("ccc","hh")
      .drop("c")

    df.printSchema()

    val f = df.withColumn("new",
      udf( (row:Row) => row.getAs[Row]("xx").getAs[Int]("c") )
        .apply(col("hh"))
    )
    f.show(10,false)

  }

  class Personas() {
    private val a = mutable.Map[Int, Int]()

    def addPersona(inta: Int, intb: Int): Personas = {
      a.put(inta, intb)
      this
    }
  }

  case class PersonasObject(a: Int, b: Int)

}
