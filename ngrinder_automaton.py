import argparse
from ec2 import connect as EC2Connect
from cbinstaller import install as CBInstaller

parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
parser.add_argument('--secret_key', required=True)
parser.add_argument('--access_key', required=True)
parser.add_argument('--pem_file', required=False)
parser.add_argument('--install_server_rpm_url', default='')
parser.add_argument('--install_debug_rpm_url', default='')
parser.add_argument('--install_nodes', default='', help='Nodes options are cb, kv, indexer, query, ngrinder')
parser.add_argument('--mode', default='', help='Modes are install, start_test, start_instances, stop_instances')
opts = parser.parse_args()

conn = EC2Connect.Connect(access_key=opts.access_key, secret_key=opts.secret_key, pem_file=opts.pem_file)
conn.print_all_instance_status()

if opts.mode == 'install':
    conn.start_ssh_conns(node_type=opts.install_nodes)
    CBInstaller.install_nodes(conn.ssh_client_map[opts.install_nodes], opts.install_server_rpm_url, opts.install_debug_rpm_url)
elif opts.mode == 'start_instances':
    conn.stop_instances()
elif opts.mode == 'stop_instances':
    conn.stop_instances



