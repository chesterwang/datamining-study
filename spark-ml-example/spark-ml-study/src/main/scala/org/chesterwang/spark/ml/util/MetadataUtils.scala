package org.chesterwang.spark.ml.util

import org.apache.spark.ml.attribute._
import org.apache.spark.sql.types.StructField

/**
  * Created by chester on 16-12-23.
  */
object MetadataUtils {

  /**
    * Examine a schema to identify the number of classes in a label column.
    * Returns None if the number of labels is not specified, or if the label column is continuous.
    */
  def getNumClasses(labelSchema: StructField): Option[Int] = {
    Attribute.fromStructField(labelSchema) match {
      case binAttr: BinaryAttribute => Some(2)
      case nomAttr: NominalAttribute => nomAttr.getNumValues
      case _: NumericAttribute | UnresolvedAttribute => None
    }
  }

}
