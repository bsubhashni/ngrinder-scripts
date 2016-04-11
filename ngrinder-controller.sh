#!/bin/sh

PIDFILE=/var/run/ngrinder-controller.pid
LOGFILE=/var/log/ngrinder-controller.log
NGHOME=/home/user/ngrinder

start() {
    echo "Starting ngrinder controller" 
    rm -rf $LOGFILE
    rm -rf $PIDFILE
    rm -rf $NGHOME
    CMD="java -XX:MaxPermSize=200m -jar wars/ngrinder-controller-3.3.war --ngrinder-home $NGHOME &> \"$LOGFILE\" & echo \$!"
    su -c "export JAVA_HOME=/usr/java/jdk1.7.0_79/; $CMD" > "$PIDFILE"
}

stop() {
     PID=`cat $PIDFILE`
     kill -9 $PID
}

case "$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  *)
    echo "Usage: $0 {start|stop}"
esac
