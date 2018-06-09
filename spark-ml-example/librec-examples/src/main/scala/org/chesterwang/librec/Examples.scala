package org.chesterwang.librec

import net.librec.conf.Configuration
import net.librec.conf.Configuration.Resource
import net.librec.data.model.TextDataModel
import net.librec.eval.rating.MAEEvaluator
import net.librec.filter.GenericRecommendedFilter
import net.librec.recommender.RecommenderContext
import net.librec.recommender.cf.UserKNNRecommender
import net.librec.similarity.PCCSimilarity

/**
  * Created by chester on 17-4-3.
  */
object Examples {

  def main(args: Array[String]) {
    // recommender configuration
    val conf = new Configuration()
    val resource = new Resource("rec/cf/userknn-test.properties")
    conf.addResource(resource)
    conf.set("dfs.data.dir","data")
    conf.set("dfs.result.dir","/tmp/librec/")

    // build data model
    val dataModel = new TextDataModel(conf)
    dataModel.buildDataModel()

    // set recommendation context
    val context = new RecommenderContext(conf, dataModel)
    val similarity = new PCCSimilarity()
    similarity.buildSimilarityMatrix(dataModel)
    context.setSimilarity(similarity)

    // training
    val recommender = new UserKNNRecommender()
    recommender.recommend(context)

    // evaluation
    val evaluator = new MAEEvaluator()
    recommender.evaluate(evaluator)

    // recommendation results
    var recommendedItemList = recommender.getRecommendedList
    val filter = new GenericRecommendedFilter()
    recommendedItemList = filter.filter(recommendedItemList)

  }

}
