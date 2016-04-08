import boto.ec2,argparse
from boto.manage.cmdshell import sshclient_from_instance
import threading

ngrinder_iids = ['i-21db39bc', 'i-20db39bd', 'i-20db39bd']
server_iids = ['i-400eefc7', 'i-470eefc0', 'i-2201e0a5', 'i-c3ec0144', 'i-de38d059', 'i-d938d05e']
indexer_iids = ['i-c3ec0144', 'i-2201e0a5']
query_iids = server_iids
kv_iids = ['i-400eefc7', 'i-470eefc0', 'i-de38d059', 'i-d938d05e']
conn = None

class Installer(threading.Thread):
    def __init__(self, ssh_client, server_rpm_url, debug_rpm_url):
        self.client = ssh_client
        self.server_rpm_url = server_rpm_url
        self.debug_rpm_url = debug_rpm_url

    def run_command(self, cmd):
        stdin, stdout, stderr = self.client.run(cmd)
        print stdout, stderr

    def run(self):
        run_command(self.client, 'sudo /etc/init.d/couchbase-server stop')
        run_command(self.client, 'sudo pkill -f memcached')
        run_command(self.client, 'sudo pkill -f indexer')
        run_command(self.client, 'sudo pkill -f projector')
        run_command(self.client, 'sudo pkill -f beam.smp')
        run_command(self.client, 'sudo pkill -f cbq-engine')
        run_command(self.client, 'sudo rpm -e $(rpm -qa |grep couchbase-server)')
        run_command(self.client, 'sudo wget -O server.rpm ' + self.server_rpm_url)
        run_command(self.client, 'sudo rpm -ivh server.rpm')
        if self.debug_rpm_url != '':
            run_command(self.client, 'sudo wget -O server.rpm ' + self.debug_rpm_url)
            run_command(self.client, 'sudo rpm -Uvh server.rpm')

def start_connection(access_key, secret_key):
    try:
        conn = boto.ec2.connect_to_region("us-east-1", aws_access_key_id=access_key,
            aws_secret_access_key=secret_key)
    except Exception as e:
        print e
    return conn

def start_all_instances():
    #start all server instances first
    iids = conn.start_instances(instance_ids=server_iids)
    assert (iids == server_iids), "server instances start up failure"
    iids = conn.start_instances(instance_ids=ngrinder_iids)
    assert (iids == ngrinder_iids), "ngrinder instances start up failure"

def stop_all_instances():
    iids = conn.stop_instances(instance_ids=server_iids)
    assert (iids == server_iids), "server instances stop failure"
    iids = conn.stop_instances(instance_ids=ngrinder_iids)
    assert (iids == ngrinder_iids), "ngrinder instances stop failure"

def run_command(client, cmd):
    stdin, stdout, stderr = client.run(cmd)
    print stdout, stderr


def install_server(nodetype, pem_file, install_rpm_url, debug_rpm_url):
    iids = []
    if nodetype == 'kv':
        iids = kv_iids
    elif nodetype == 'indexer':
        iids = indexer_iids
    elif nodetype == 'query':
        iids = query_iids
    elif nodetype == 'all':
        iids = server_iids

    threads = []
    for i in iids:
        instance = conn.get_all_instances([i])[0].instances[0]
        ssh_client = sshclient_from_instance(instance, pem_file, user_name='ec2-user')
        thread = Installer(ssh_client, install_rpm_url, debug_rpm_url)
        threads.append(thread)

    for t in threads:
        t.join()

def stop_all_instances(conn):
    iids = conn.stop_instances(instance_ids=server_iids)
    assert (iids == server_iids), "server instances stop failure"
    iids = conn.stop_instances(instance_ids=ngrinder_iids)
    assert (iids == ngrinder_iids), "ngrinder instances stop failure"

parser = argparse.ArgumentParser()
parser.add_argument('--secret_key', default='')
parser.add_argument('--access_key', default='')
parser.add_argument('--pem_file', default='')
parser.add_argument('--install_server_rpm_url', default='', help="kv,")
parser.add_argument('--install_debug_rpm_url', default='')
parser.add_argument('--install_nodes', default='Nodes are all,kv,indexer,query')
parser.add_argument('--mode', default='', help="Modes are install, start_test, start_instances, stop_instances")
opts = parser.parse_args()

conn = start_connection(opts.access_key, opts.secret_key)
instances = conn.get_all_instance_status()
print instances

if opts.mode == 'install':
    install_server(opts.install_nodes,opts.install_server_rpm_url, opts.install_debug_rpm_url)
elif opts.mode == 'start_instances':
    start_all_instances()
elif opts.mode == 'stop_instances':
    stop_all_instances()

#install_server(opts.pem_file, opts.server_rpm_url, opts.debug_rpm_url)
