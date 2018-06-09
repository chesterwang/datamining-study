#!/usr/bin/env bash

currentdir=`dirname $0`
cp ${currentdir}/target/spark-ml-spring.jar ${currentdir}/spark-ml-spring.jar
bash ${currentdir}/run.sh restart