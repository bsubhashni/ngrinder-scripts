#!/bin/sh

PIDFILE=/var/run/ngrinder-controller.pid
LOGFILE=/var/log/ngrinder-controller.log

start() {
    echo "Starting ngrinder controller" 
    rm -rf $LOGFILE
    rm -rf $PIDFILE
    CMD="java -XX:MaxPermSize=200m -jar wars/ngrinder-controller-3.3.war &> \"$LOGFILE\" & echo \$!"
    su -c "$CMD" > "$PIDFILE"
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
