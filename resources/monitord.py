'''
monitor stats for cb processes
'''
import os, socket, json, threading, psutil, subprocess, shlex, time

processes = ['memcached', 'cbq-engine', 'index', 'projector']

class Perfmon(object):
    def __init__(self, port=8420):
        self.port = port
        self.sock = None
        self.collector = None

    def _decode_list(self, data):
        rv = []
        for item in data:
            if isinstance(item, unicode):
                item = item.encode('utf-8')
            elif isinstance(item, list):
                item = self._decode_list(item)
            elif isinstance(item, dict):
                item = self._decode_dict(item)
            rv.append(item)
        return rv

    def _decode_dict(self,data):
        rv = {}
        for key, value in data.iteritems():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            elif isinstance(value, list):
                value = self._decode_list(value)
            elif isinstance(value, dict):
                value = self._decode_dict(value)
            rv[key] = value
        return rv

    def handleConnection(self, conn):
        data = conn.recv(1024)
        print "data",data
        request = json.loads(data, object_hook=self._decode_dict)
        if request['command'] == 'START MONITOR':
            self.startMonitor(request)
            res = 'OK'
        elif request['command'] == 'STOP MONITOR':
            res = self.stopMonitor()
            print res
        elif request['command'] == 'STOP':
             self.stop()
        conn.sendall(res)
        conn.close()

    def startMonitor(self, request):
        self.collector = Collector(request=request)
        self.collector.start()

    def stopMonitor(self):
        self.collector.stopCollecting()
        res = self.collector.getResponse()
        del self.collector
        return res

    def stop(self):
        self.sock.close()
        #look for core dumps and add to response
        os._exit(0)

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.bind(('',self.port))
        except socket.error as msg:
            print 'Bind failed. Error code:' + str(msg[0])
        self.sock.listen(10)
        while 1:
            conn, addr = self.sock.accept()
            self.handleConnection(conn)


class Collector(threading.Thread):
    def __init__(self, request=None, cancelled=False):
        threading.Thread.__init__(self, group=None, target=None, name=None, verbose=None)
        self.cancelled = cancelled
        self.request = request
        self.mem_usage = dict()
        self.cpu_usage = dict()
        self.rss_usage = dict()

        for p in processes:
            self.mem_usage[p] = ["mem_usage"]
            self.cpu_usage[p] = ["cpu_usage"]
            self.rss_usage[p] = ["rss_usage"]

        self._done = False

    def run(self):
        self.startCollecting()

    def startCollecting(self):
        while not self.cancelled:
            try:
                for p in psutil.process_iter():
                    if p.name() in processes:
                        vms =  p.as_dict(attrs=['memory_info']).get('memory_info').vms
                        rss =  p.as_dict(attrs=['memory_info']).get('memory_info').rss
                        cpu_percent = self.cpu_usage.append(p.as_dict(attrs=['cpu_percent']).get('cpu_percent'))
                        self.mem_usage[p.name()].append(vms)
                        self.cpu_usage[p.name()].append(cpu_percent)
                        self.rss_usage[p.name()].append(rss)
                    time.sleep(self.request['thinktime'] if self.request['thinktime'] == None else 1)
            except Exception as e:
                print e.message

        self._done = True

    def stopCollecting(self):
        self.cancelled = True

    def getResponse(self):
        response = dict()
        for p in processes:
            response[p + "mem_usage"] = self.mem_usage[p]
            response[p + "cpu_usage"] = self.cpu_usage[p]
            response[p + "rss_usage"] = self.rss_usage[p]
        return json.dumps(response)

perfmon = Perfmon()
perfmon.start()


