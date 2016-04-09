import requests, json

class Ngrinder(object):
    def __init__(self, *args, **kwargs):
        '''
        self.duration = kwargs['duration']
        self.test_name = kwargs['test_name']
        self.agent_count = kwargs['agent_count']
        self.vuser_per_agent = kwargs['vuser_per_agent']
        '''
        self.controller_ip = kwargs['controller_ip']
        self.controller_port = kwargs['controller_port']
        self.controller_host = "http://" + self.controller_ip + ":" + self.controller_port
        self.last_test_id = None

    def start_test(self):
        data = dict()
        data['agentCount'] = self.agent_count
        data['vuserPerAgent'] = self.vuser_per_agent
        data['duration'] = self.duration
        response = requests.put(self.controller_host + "/perftest/api/" + self.test_name, data=data, auth=('admin', 'admin'))
        if response.status_code != 200:
            print "Update test failed with error status "+ response.status_code

        response = requests.post(self.controller_host + "/perftest/api/" + self.test_name + "/clone_and_start", auth=('admin', 'admin'))
        if response.status_code != 200:
            print "Clone and start test failed"

    def stop_test(self):
        response = requests.put(self.controller_host + "/perftest/api/"+ self.test_name + "?action=stop",  auth=('admin', 'admin'))
        if response.status_code != 200:
            print "Stop test failed"

    def get_test_status(self):
        print self.controller_host
        response = requests.get(self.controller_host + "/perftest/api?size=1", auth=('admin', 'admin'))
        if response.status_code != 200:
            print "Response failed with status " + str(response.status_code)
        else:
            content = json.loads(response._content)
            self.last_test_id = content[0]['id']
            return content[0]['status']

