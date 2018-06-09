package org.chesterwang.librec

import java.io.PrintWriter

import net.librec.conf.Configuration
import net.librec.conf.Configuration.Resource
import net.librec.data.model.TextDataModel
import net.librec.eval.rating.MAEEvaluator
import net.librec.filter.GenericRecommendedFilter
import net.librec.recommender.RecommenderContext
import net.librec.recommender.baseline.ConstantGuessRecommender
import net.librec.recommender.cf.UserKNNRecommender
import net.librec.similarity.PCCSimilarity

import scala.collection.JavaConversions._
import net.librec.recommender._

/**
  * Created by chester on 17-4-3.
  */
object ExamplesUserDefined {

  def main(args: Array[String]) {
    // recommender configuration
    val conf = new Configuration()
    val resource = new Resource("librec-userdefined.properties")
    conf.addResource(resource)

    // build data model
    val dataModel = new TextDataModel(conf)
    dataModel.buildDataModel()

    // set recommendation context
    val rcontext = new RecommenderContext(conf, dataModel)
    val similarity = new PCCSimilarity()
    similarity.buildSimilarityMatrix(dataModel)
    rcontext.setSimilarity(similarity)

    // training
//    val recommender = new UserKNNRecommender()
//    recommender.recommend(rcontext)

    //models

    val recommenders = List(
      new baseline.ConstantGuessRecommender
//      new baseline.GlobalAverageRecommender
//      new baseline.ItemAverageRecommender
//      new baseline.ItemClusterRecommender
//      new baseline.MostPopularRecommender
//      new baseline.RandomGuessRecommender
//      new baseline.UserAverageRecommender
//      new baseline.UserClusterRecommender
//      new cf.ranking.AoBPRRecommender
//      new cf.ranking.AspectModelRecommender
//      new cf.BHFreeRecommender
//      new cf.ranking.BPRRecommender
//      new cf.BUCMRecommender
//      new cf.ranking.CLIMFRecommender
//      new cf.ranking.EALSRecommender
//      new cf.ranking.FISMaucRecommender
//      new cf.ranking.FISMrmseRecommender
//      new cf.ranking.GBPRRecommender
//      new cf.ranking.ItemBigramRecommender
//      new cf.ranking.LDARecommender
//      new cf.ranking.ListRankMFRecommender
//      new cf.ranking.PLSARecommender
//      new cf.ranking.RankALSRecommender
//      new cf.ranking.RankSGDRecommender
//      new cf.ranking.SLIMRecommender
//      new cf.ranking.WBPRRecommender
//      new cf.ranking.WRMFRecommender
//      new cf.rating.ASVDPlusPlusRecommender
//      new cf.rating.AspectModelRecommender
//      new cf.rating.BiasedMFRecommender
////      new cf.rating.BNPoissMFRecommender
//      new cf.rating.BPMFRecommender
//      new cf.rating.BPoissMFRecommender
////      new cf.rating.CPTFRecommender
//      new cf.rating.FMALSRecommender
//      new cf.rating.FMSGDRecommender
//      new cf.rating.GPLSARecommender
//      new cf.ItemKNNRecommender
//      new cf.rating.LDCCRecommender
//      new cf.rating.LLORMARecommender
//      new cf.rating.MFALSRecommender
//      new cf.rating.NMFRecommender
//      new cf.rating.PMFRecommender
//      new cf.rating.RBMRecommender
//      new cf.rating.RFRecRecommender
//      new cf.rating.SVDPlusPlusRecommender
//      new cf.rating.URPRecommender
//      new cf.UserKNNRecommender
//      new content.EFMRecommender
//      new content.HFTRecommender
////      new content.TopicMFATRecommender
//      new context.ranking.SBPRRecommender
////      new context.rating.BPTFRecommender
////      new context.rating.PITFRecommender
//      new context.rating.RSTERecommender
//      new context.rating.SocialMFRecommender
//      new context.rating.SoRecRecommender
//      new context.rating.SoRegRecommender
//      new context.rating.TimeSVDRecommender
//      new context.rating.TrustMFRecommender
//      new context.rating.TrustSVDRecommender
//      new ext.AssociationRuleRecommender
//      new ext.ExternalRecommender
//      new hybrid.HybridRecommender
//      new ext.PersonalityDiagnosisRecommender
//      new ext.PRankDRecommender
//      new ext.SlopeOneRecommender
    )


    val recommender = recommenders(0)

    recommender.recommend(rcontext)

    // recommendation results
    var recommendedItemList = recommender.getRecommendedList
    val filter = new GenericRecommendedFilter()
    recommendedItemList = filter.filter(recommendedItemList)

    recommender.saveModel("/tmp/model")
    recommender.getRecommendedList.map(x => s"${x.getUserId},${x.getItemId},${x.getValue}")
      .take(10).foreach(println)
    val writer = new PrintWriter("/tmp/result/a")
    recommender.getRecommendedList.map(x => s"${x.getUserId},${x.getItemId},${x.getValue}")
      .foreach(writer.println(_))


  }

}
