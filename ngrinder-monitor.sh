#!/bin/sh

LOGFILE=/var/log/ngrinder-monitor.log
CTLR=""
start() {
    echo "Starting ngrinder monitor"
    if [ -z "$CLTR" ];
    then
        CLTR="127.0.0.1"
    fi
    echo "$CLTR"
    rm -rf $LOGFILE
    if [ ! -d /opt/ngrinder/$CTLR/ngrinder-monitor ];
    then
        mkdir -p /opt/ngrinder/$CTLR
        wget -O /opt/ngrinder/$CTLR/monitor.tar http://$CTLR:8080/monitor/download
        tar xvf /opt/ngrinder/$CTLR/monitor.tar -C /opt/ngrinder/$CTLR
    fi
    su -c "/opt/ngrinder/$CTLR/ngrinder-monitor/run_monitor.sh &> $LOGFILE &"
}

stop() {
    echo "Stopping ngrinder monitor"
    if [ -z "$CLTR" ];
    then
        CLTR="127.0.0.1"
    fi

     su -c "/opt/ngrinder/$CTLR/ngrinder-monitor/stop_monitor.sh"
}

CTLR="$2"
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
