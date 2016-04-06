#!/bin/sh

LOGFILE=/var/log/ngrinder-agent.log
CTLR=""
start() {
    echo "Starting ngrinder agent"
    if [ -z "$CLTR" ];
    then
        CLTR="127.0.0.1"
    fi
    echo "$CLTR"
    rm -rf $LOGFILE
    if [ ! -d /opt/ngrinder/$CTLR/ngrinder-agent ];
    then
        mkdir -p /opt/ngrinder/$CTLR
        wget -O /opt/ngrinder/$CTLR/agent.tar http://$CTLR:8080/agent/download
        tar xvf /opt/ngrinder/$CTLR/agent.tar -C /opt/ngrinder/$CTLR
    fi
    su -c "/opt/ngrinder/$CTLR/ngrinder-agent/run_agent.sh &> $LOGFILE &"
}

stop() {
    echo "Stopping ngrinder agent"
    if [ -z "$CLTR" ];
    then
        CLTR="127.0.0.1"
    fi

     su -c "/opt/ngrinder/$CTLR/ngrinder-agent/stop_agent.sh"
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
