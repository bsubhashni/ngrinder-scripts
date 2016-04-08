import threading
import ec2

class Installer(threading.Thread):
    def __init__(self, **kwargs):
        threading.Thread.__init__(self)
        self.client = kwargs['ssh_client']
        self.server_rpm_url = kwargs['server_rpm_url']
        self.debug_rpm_url = kwargs['debug_rpm_url']

    def run(self):
        self.run_command("ls -l")
        '''
        self.run_command(self.client, 'sudo /etc/init.d/couchbase-server stop')
        self.run_command(self.client, 'sudo pkill -f memcached')
        self.run_command(self.client, 'sudo pkill -f indexer')
        self.run_command(self.client, 'sudo pkill -f projector')
        self.run_command(self.client, 'sudo pkill -f beam.smp')
        self.run_command(self.client, 'sudo pkill -f cbq-engine')
        self.run_command(self.client, 'sudo rpm -e $(rpm -qa |grep couchbase-server)')
        self.run_command(self.client, 'sudo wget -O server.rpm ' + self.server_rpm_url)
        self.run_command(self.client, 'sudo rpm -ivh server.rpm')
        if self.debug_rpm_url != '':
            self.run_command(self.client, 'sudo wget -O server.rpm ' + self.debug_rpm_url)
            self.run_command(self.client, 'sudo rpm -Uvh server.rpm')
        '''

    def run_command(self, cmd):
        stdin, stdout, stderr = self.client.run(cmd)
        print stdout, stderr


def install_nodes(ssh_clients, server_rpm_url, debug_rpm_url):
    threads = []
    for client in ssh_clients:
        print "Starting a new installer thread"
        thread = Installer(ssh_client=client, server_rpm_url=server_rpm_url, debug_rpm_url=debug_rpm_url)
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
