import boto.ec2,time,argparse
from boto.manage.cmdshell import sshclient_from_instance

ngrinder_iids = ['i-21db39bc', 'i-20db39bd', 'i-20db39bd']
server_iids = ['i-400eefc7', 'i-470eefc0', 'i-2201e0a5', 'i-c3ec0144', 'i-de38d059', 'i-d938d05e']
 
def start_connection(access_key, secret_key):
    try:
        conn = boto.ec2.connect_to_region("us-east-1", aws_access_key_id=access_key, 
            aws_secret_access_key=secret_key)
    except Exception as e:
        print e

    return conn

def start_all_instances(conn):
    #start all server instances first
    iids = conn.start_instances(instance_ids=server_iids)
    assert (iids == server_iids), "server instances start up failure"
    iids = conn.start_instances(instance_ids=ngrinder_iids)
    assert (iids == ngrinder_iids), "ngrinder instances start up failure"
    
def run_command(client, cmd):
    stdin, stdout, stderr = client.run(cmd)
    print stdout, stderr

def install_server(pem_file, rpm_url):
    for i in server_iids:
        instance = conn.get_all_instances([i])[0].instances[0]
        ssh_client = sshclient_from_instance(instance, pem_file, user_name='ec2-user')
        run_command(ssh_client, 'sudo /etc/init.d/couchbase-server stop')
        run_command(ssh_client, 'sudo pkill -f memcached')
        run_command(ssh_client, 'sudo pkill -f indexer')
        run_command(ssh_client, 'sudo pkill -f projector')
        run_command(ssh_client, 'sudo pkill -f beam.smp')
        run_command(ssh_client, 'sudo pkill -f cbq-engine')
        run_command(ssh_client, 'wget -O server.rpm ' + rpm_url)
        run_command(ssh_client, 'rpm -ivh server.rpm')
       
def stop_all_instances(conn):
    iids = conn.stop_instances(instance_ids=server_iids)
    assert (iids == server_iids), "server instances stop failure"
    iids = conn.stop_instances(instance_ids=ngrinder_iids)
    assert (iids == ngrinder_iids), "ngrinder instances stop failure"

parser = argparse.ArgumentParser()
parser.add_argument('--secret_key')
parser.add_argument('--access_key')
parser.add_argument('--pem_file')
parser.add_argument('--server_rpm_url')
parser.add_argument('--mode')
opts = parser.parse_args() 

conn = start_connection(opts.access_key, opts.secret_key)
instances = conn.get_all_instance_status()
print instances
if opts.mode == 'stop':
    stop_all_instances(conn)
else if opts.mode == 'start':
    start_all_instances(conn)
