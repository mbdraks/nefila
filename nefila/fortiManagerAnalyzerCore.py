import requests
from .utils import get_credentials


class FortiManagerAnalyzerCore(object):

    def __init__(self, hostname):
        #: Use the same session for all requests
        self.session = requests.session()

        #: SSL Verification default.
        self.session.verify = False

        #: How long to wait for the server to send data before giving up
        self.timeout = 10

        #: Device hostname
        self.hostname = hostname

        #: Base URL for all requests
        self.base_url = f'https://{self.hostname}/jsonrpc'

        #: Session ID
        self.session_id = None

        # Subsystems init
        # self.devices = Devices(self.session, self.timeout, self.base_url, self.session_id)
        self.devices = Devices(self)

    def open(self, username=None, password=None):
        credentials = {}
        
        # If credentials are not supplied, check file
        if not (username):
            credentials = get_credentials(self.hostname)
            username = credentials['username']
            password = credentials['password']

        credentials['user'] = username
        credentials['passwd'] = password

        url = '/sys/login/user'

        # create request

        params = {}
        params['url'] = url
        params['data'] = credentials

        data = {}
        data['id'] = 1
        data['method'] = 'exec'
        data['session'] = None
        data['jsonrpc'] = '2.0'
        data['params'] = [params]

        response = self.session.post(url=self.base_url, json=data, timeout = self.timeout)

        self.session_id = response.json()['session']

        return response


    def close(self):
        url = '/sys/logout'

        # create request

        params = {}
        params['url'] = url

        data = {}
        data['id'] = 1
        data['method'] = 'exec'
        data['session'] = self.session_id
        data['jsonrpc'] = '2.0'
        data['params'] = [params]

        response = self.session.post(url=self.base_url, json=data, timeout = self.timeout)
        return response


    def _get_status(self):
        '''Obtain general status
        
        Uptime in seconds

        {'version': 'v6.2.0',
        'serial': 'FGVULVTM19000152',
        'forticare': 'registered',
        'hostname': 'FG',
        'model': 'FortiGate-VM64'}
        '''
        status = {}
        url = '/sys/status'

        params = {}
        params['url'] = url

        data = {}
        data['id'] = 1
        data['method'] = 'get'
        data['session'] = self.session_id
        data['jsonrpc'] = '2.0'
        data['params'] = [params]

        response = self.session.post(url=self.base_url, json=data, timeout = self.timeout)

        status['serial'] = response.json()['result'][0]['data']['Serial Number']
        status['version'] = response.json()['result'][0]['data']['Version'].split('-')[0]
        status['forticare'] = response.json()['result'][0]['data']['License Status']
        status['hostname'] = response.json()['result'][0]['data']['Hostname']
        status['model'] = response.json()['result'][0]['data']['Platform Full Name']

        return status

    @property
    def status(self):
        return self._get_status()


    def basic_status(self):
        '''Retrieve basic system status.'''

        url = '/sys/status'

        params = {}
        params['url'] = url

        data = {}
        data['id'] = 1
        data['method'] = 'get'
        data['session'] = self.session_id
        data['jsonrpc'] = '2.0'
        data['params'] = [params]

        response = self.session.post(url=self.base_url, json=data, timeout = self.timeout)
        return response


    # def license_status(self):
    #     '''Get current license & registration status.'''
    #     pass

    def device_list(self, adom='root'):
        '''List managed devices
        
        mgmt_mode
            2 Unauthorized
        
        '''

        # url = f'dvmdb/adom/{adom}/device'
        url = f'dvmdb/device'

        params = {}
        params['url'] = url

        data = {}
        data['id'] = 1
        data['method'] = 'get'
        data['session'] = self.session_id
        data['jsonrpc'] = '2.0'
        data['params'] = [params]

        response = self.session.post(url=self.base_url, json=data, timeout = self.timeout)
        return response


class Devices(object):
    def __init__(self, core):
        self.fmg = core

    def list(self, adom='root'):
        '''List managed devices
        
        mgmt_mode
            2 Unauthorized
        
        '''
        url = f'dvmdb/device'
        json = self.fmg.prepare_json(url=url)
        r = self.fmg.session.post(url=self.fmg.base_url, json=json, timeout = self.fmg.timeout)
        return r
