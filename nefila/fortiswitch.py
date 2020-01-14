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
        self.switch = Switch(self.session, self.timeout, self.base_url)


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

        # FortiSwitch v3.6 does not support system_time
        url = f'https://{self.hostname}/resource/system_time'
        r = self.session.get(url, timeout=self.timeout)
        if r == 200:
            status['uptime'] = r.json()['uptime']
        else:
            url = f'https://{self.hostname}/system/status/status?getModuleContent=1'
            r = self.session.get(url, timeout=self.timeout)
            l = r.text.split('Uptime</TD><TD>')
            uptime = l[1].split('</TD>')
            status['uptime'] = uptime[0]

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


class Switch(object):
    def __init__(self, session, timeout, base_url):
        self.session = session
        self.timeout = timeout
        self.base_url = base_url

        self.lldp = Lldp(self.session, self.timeout, self.base_url)


class Lldp(object):
    '''LLDP Information

    Usage:
        device.switch.lldp.neighbors()
        device.switch.lldp.neighbors(port='port1')
    '''

    def __init__(self, session, timeout, base_url):
        self.session = session
        self.timeout = timeout
        self.base_url = base_url
        # self.base_url = f'{base_url}/monitor/system/vmlicense'

    def neighbors(self, port=None):
        '''
        Retrieves LLDP information. Equivalent to the
        get switch lldp neighbors-summary CLI command.
        '''
        url = f'{self.base_url}/monitor/switch/lldp-state/'

        params = {'port_name': port}
        r = self.session.get(url=url, params=params, timeout=self.timeout)
        neighbors = {}

        for neighbor in r.json()['results'][2:]:
            port = neighbor['port']
            neighbors[port] = []
            neighbor_info = {}
            neighbor_info['hostname'] = neighbor['system_name']
            neighbor_info['port'] = neighbor['port_id'].strip(' (ifname)')
            neighbors[port].append(neighbor_info)
        return neighbors

    def neighbors_detail(self, port=None):
        '''
        Retrieves LLDP information. Equivalent to the
        get switch lldp neighbors-detail CLI command.
        '''
        url = f'{self.base_url}/monitor/switch/lldp-state/'

        params = {'port_name': port}
        r = self.session.get(url=url, params=params, timeout=self.timeout)
        neighbors = {}

        for neighbor in r.json()['results'][2:]:
            port = neighbor['port']
            neighbors[port] = []
            neighbor_info = {}

            # check if aggregate interface, if yes put the agg name here
            neighbor_info['parent_interface'] = ''
            neighbor_info['remote_chassis_id'] = neighbor['chassis_id']
            neighbor_info['remote_system_name'] = neighbor['system_name']
            neighbor_info['remote_port'] = neighbor['port_id'].strip(' (ifname)')
            neighbor_info['remote_port_description'] = neighbor['port_description']
            neighbor_info['remote_system_description'] = neighbor['system_description']
            neighbor_info['remote_system_capab'] = neighbor['system_capabilities']
            neighbor_info['remote_system_enable_capab'] = neighbor['enabled_capabilities']
            neighbors[port].append(neighbor_info)
        return neighbors

    def neighbors_full(self, port=None):
        '''
        Retrieves LLDP information. Equivalent to the
        get switch lldp neighbors-detail CLI command.
        '''
        url = f'{self.base_url}/monitor/switch/lldp-state/'
        params = {'port_name': port}
        r = self.session.get(url=url, params=params, timeout=self.timeout)
        return r
