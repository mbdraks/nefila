import requests
from .utils import get_credentials


class FortiSwitch(object):
    def __init__(self, hostname):
        #: Use the same session for all requests
        self.session = requests.session()

        #: SSL Verification default.
        self.session.verify = False

        #: How long to wait for the server to send data before giving up
        self.timeout = 10

        #: Device hostname
        self.hostname = hostname
        self.base_url = f'https://{self.hostname}/api/v2'

        # Subsystems init
        # self.system = System(self.session, self.timeout, self.base_url)


    def open(self, username=None, password=None):
        credentials = {}

        # If credentials are not supplied, check file
        if not username:
            credentials = get_credentials(self.hostname)
            username = credentials['username']
            password = credentials['password']

        url = f'https://{self.hostname}/logincheck'

        data = f'username={username}&secretkey={password}'

        r = self.session.post(url=url, data=data, timeout=self.timeout)

        for cookie in self.session.cookies:
            if cookie.name == 'ccsrftoken':
                csrftoken = cookie.value[1:-1]
                self.session.headers.update({'X-CSRFTOKEN': csrftoken})
        
        return r


    def close(self):
        url = f'https://{self.hostname}/logout'
        r = self.session.post(url, timeout=self.timeout)
        return r


    def _get_status(self):
        '''Obtain general status
        '''
        status = {}
        url = f'{self.base_url}/monitor/system/status'
        r = self.session.get(url, timeout=self.timeout)
        status['version'] = r.json()['results']['version']
        status['serial'] = r.json()['results']['serial_number']
        status['hostname'] = r.json()['results']['hostname']    

        url = f'{self.base_url}/monitor/system/hardware-status'
        r = self.session.get(url, timeout=self.timeout)
        status['model'] = r.json()['results'][0]['model']

        url = f'https://{self.hostname}/resource/system_time'
        r = self.session.get(url, timeout=self.timeout)
        status['uptime'] = r.json()['uptime']

        status['forticare'] = None
        return status

    @property
    def status(self):
        return self._get_status()


    def basic_status(self):
        '''Retrieve basic system status.'''
        url = f'{self.base_url}/monitor/system/status'
        r = self.session.get(url, timeout=self.timeout)
        return r
