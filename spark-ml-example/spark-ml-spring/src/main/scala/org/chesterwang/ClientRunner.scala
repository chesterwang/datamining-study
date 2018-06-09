package org.chesterwang

import com.ximalaya.data.task.spark.BaseSparkTask
import org.apache.spark.ml.feature.HashingTF
import org.springframework.context.support.ClassPathXmlApplicationContext

/**
  * Created by chester on 16-12-24.
  */
object ClientRunner {
  def main(args: Array[String]) {
//    val applicationContext = new ClassPathXmlApplicationContext("classpath:application-context.xml")
    val applicationContext = new ClassPathXmlApplicationContext("classpath:model1.xml")
    val tf:HashingTF = applicationContext.getBean("tf",classOf[HashingTF])
    println(tf.getNumFeatures)

    //error 失败
    val job = applicationContext.getBean("ALSExample",classOf[BaseSparkTask])
    job.execute()

  }

}
