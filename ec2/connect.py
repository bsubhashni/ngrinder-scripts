import boto.ec2
from constants import *
from ec2 import constants as ec2constants
from boto.manage.cmdshell import sshclient_from_instance


class Connect(object):
    def __init__(self, **kwargs):
        self.access_key = kwargs['access_key']
        self.secret_key = kwargs['secret_key']
        self.pem_file = kwargs['pem_file']
        self.conn = None
        self.ssh_client_map = dict()

    def _needs_connection(func):
        def wrapper(self, *args, **kwargs):
            if self.conn == None:
                self._start_connection()
            result = func(self, *args, **kwargs)
            return result
        return wrapper

    def _get_ssh_clients(self, iids):
        ssh_clients = []
        for i in iids:
            instance = self.conn.get_all_instances([i])[0].instances[0]
            try:
                client = sshclient_from_instance(instance, self.pem_file, user_name='ec2-user')
                ssh_clients.append(client)
            except Exception as e:
                print "Caught error creating ssh connection"
        return ssh_clients

    def _start_connection(self):
        self.conn = boto.ec2.connect_to_region("us-east-1", aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key)


    @_needs_connection
    def get_ngrinder_controller_ip(self):
        instance = self.conn.get_all_instances([ngrinder_controller_iid])[0].instances[0]
        return instance.ip_address

    @_needs_connection
    def start_ssh_conns(self, node_type=''):
        ssh_clients = []
        if node_type == 'index':
            ssh_clients = self._get_ssh_clients(indexer_iids)
        elif node_type == 'query':
            ssh_clients = self._get_ssh_clients(query_iids)
        elif node_type == 'kv':
            ssh_clients = self._get_ssh_clients(kv_iids)
        elif node_type == 'cb':
            ssh_clients = self._get_ssh_clients(server_iids)
        elif node_type == 'ngrinder':
            ssh_clients = self._get_ssh_clients(ngrinder_iids)
        else:
            print "Unknown mode for options"
        self.ssh_client_map[node_type] = ssh_clients

    @_needs_connection
    def start_instances(self):
        instance_ids = self.conn.start_instances(instance_ids=server_iids)
        assert (instance_ids == server_iids), "server instances start up failure"
        instance_ids = self.start_instances(instance_ids=ngrinder_iids)
        assert (instance_ids == ngrinder_iids), "ngrinder instances start up failure"

    @_needs_connection
    def stop_instances(self):
        instance_ids = self.conn.stop_instances(instance_ids=server_iids)
        assert (instance_ids == server_iids), "server instances start up failure"
        instance_ids = self.conn.stop_instances(instance_ids=ngrinder_iids)
        assert (instance_ids == ngrinder_iids), "ngrinder instances start up failure"

    @_needs_connection
    def get_all_instance_status(self):
        instances = self.conn.get_all_instance_status()
        return instances

