#!/bin/sh

# ${project_name}
#
# chkconfig:   - 95 25 
# description:  ${project_name} project

export JAVA_BIN=$(which java)
project_name=spark-ml-spring

#获得当前路径
#. /etc/rc.d/init.d/functions
#. /etc/sysconfig/network
#[ "${NETWORKING}" = "no" ] && exit 0

currentdir=`dirname $0`
#currentdir='/usr/local/${project_name}'
JAVA_OPTS="-Dlog4j.configuration=log4j-client.properties -XX:PermSize=512M -XX:MaxPermSize=512M -Xmx1024M -Xms128M -Xss256k -XX:ParallelGCThreads=10 -XX:+UseConcMarkSweepGC -XX:+UseParNewGC"
EXEC_COMMAND="${JAVA_BIN} $JAVA_OPTS -jar ${currentdir}/${project_name}.jar"
pidfile='/tmp/${project_name}.pid'
#currentdir=`cd "$currentdir" > /dev/null ; pwd`

#判断是否已经启动,kill已经启动的client
#for pid in `ps -ef | grep ${project_name}。jar | grep -v grep | awk '{print $2}'`
#  do kill -9 $pid
#done
usage() {
   echo "$0 start|stop|restart"
   exit 1
}

[ $# -ne 1 ] && usage

start() {
    if [ -f $pidfile ]
      then
         echo '${project_name} has already started.'
         echo process pid:$pid
         exit 1
    fi
    if [ -f ${currentdir}/${project_name}.jar ]
    then
        echo "start ${project_name}"
        nohup $EXEC_COMMAND > $currentdir/stat-${project_name}-out.log 2>&1 &
        echo "end of start ${project_name}"
    else
      echo "${project_name}.jar is not exists!"
    fi
    RETVAL=$?
    echo
    return $RETVAL
}

stop() {
    pid=`ps -ef | grep ${project_name}.jar | grep -v grep | awk "{print $2}"`
    echo "process pid='${pid}' stopping..."
    [ ! -n "$pid" ] || kill -9 $pid || failure
    echo "done"
    RETVAL=$?
    echo
    return $RETVAL
}

restart(){
    stop
    start
}

case $1 in
    start)
    start
    ;;
    stop)
    stop
    ;;
    restart)
    restart
    ;;
    *)
    usage
    ;;
esac
