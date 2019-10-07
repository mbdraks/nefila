import requests
from .utils import get_credentials
import json

class FortiGate(object):
    def __init__(self, hostname):
        #: Use the same session for all requests
        self.session = requests.session()

        #: SSL Verification default.
        self.verify = False

        #: How long to wait for the server to send data before giving up
        self.timeout = 10

        #: Device hostname
        self.hostname = hostname
        self.base_url = f'https://{self.hostname}/api/v2'

        # Subsystems init
        self.system = System(self.session, self.timeout, self.base_url)


    def open(self, username=None, password=None, token=None, profile=None):

        # self.profile = profile

        # If credentials are not supplied, check file
        if not username:
            credentials = get_credentials(profile)
            username = credentials['username']
            password = credentials['password']
            token = credentials['token']

        # Update parameters
        self.username = username
        url_login = f'https://{self.hostname}/logincheck'

        if not token:
            self.session.post(url=url_login,
                            data=f'username={username}&secretkey={password}',
                            verify = self.verify,
                            timeout = self.timeout,
            )

            for cookie in self.session.cookies:
                if cookie.name == 'ccsrftoken':
                    csrftoken = cookie.value[1:-1]
                    self.session.headers.update({'X-CSRFTOKEN': csrftoken})

        else:
            self.session.headers.update({'Authorization': f'Bearer {token}'})
            self.token = True
        
        response = self.license_status()
        
        # self.serial = response.json()['serial']
        
        # version = response.json()['version']
        # build = str(response.json()['build'])
        # self.version = f'{version},build{build}'

        return response


    def close(self):
        url_logout = f'https://{self.hostname}/logout'
        response = self.session.post(url_logout, timeout=self.timeout)
        return response.status_code


    def _get_status(self):
        url = f'{self.base_url}/monitor/license/status'
        response = self.session.get(url, timeout=self.timeout)
        if response.status_code == 200:
            status = {}
            status['version'] = response.json()['version']
            status['serial'] = response.json()['serial']
            status['forticare'] = response.json()['results']['forticare']['status']

        url = f'{self.base_url}/monitor/web-ui/state'
        response = self.session.get(url, timeout=self.timeout)
        if response.status_code == 200:
            model_name = response.json()['results']['model_name']
            model_number = response.json()['results']['model_number']
            status['hostname'] = response.json()['results']['hostname']
            status['model'] = f'{model_name}-{model_number}'
            return status
        else:
            return response.status_code

    @property
    def status(self):
        return self._get_status()


    def basic_status(self):
        '''Retrieve basic system status.'''
        url = f'{self.base_url}/monitor/system/status'
        response = self.session.get(url, timeout=self.timeout)
        return response


    def license_status(self):
        '''Get current license & registration status.'''
        url = f'{self.base_url}/monitor/license/status'
        response = self.session.get(url, verify = self.verify, timeout=self.timeout)

        if response.status_code == 200:
            self.version = response.json()['version']
            self.serial = response.json()['serial']
            self.forticare = response.json()['results']['forticare']['status']

        return response


class System(object):
    def __init__(self, session, timeout, base_url):
        self.session = session
        self.timeout = timeout
        self.base_url = base_url
        self.dns_database = DnsDatabase(self.session, self.timeout, self.base_url, name=None)


class DnsDatabase(object):
    '''Add or check records on the DNS Database.

    Usage:
        device.system.dns_database.list()
        device.system.dns_database.name = 'exampleZone'
        device.system.dns_database.create()
        device.system.dns_database.add(ip='192.2.0.1', hostname='example')
        device.system.dns_database.get().json()
        device.system.dns_database.delete()
    '''

    def __init__(self, session, timeout, base_url, name):
        self.session = session
        self.timeout = timeout
        self.base_url = base_url
        self.name = name


    def list(self):
        '''List all DNS zones'''
        url = f'{self.base_url}/cmdb/system/dns-database'
        response = self.session.get(url=url, timeout=self.timeout)
        return response


    def create(self):
        '''Create a new DNS Zone'''
        url = f'{self.base_url}/cmdb/system/dns-database'
        data = {'name': self.name, 'domain': self.name}
        response = self.session.post(url=url, json=data)
        return response

    def add(self, ip, hostname):
        '''Add a new entry on a specific existing DNS Zone, preserving 
        existing entries.
        '''
        # Obtain existing list
        url = f'{self.base_url}/cmdb/system/dns-database/{self.name}'
        response = self.session.get(url=url, timeout=self.timeout)
        dns_entry_list = response.json()['results'][0]['dns-entry']

        # prepare the new entry
        dns_entry_id = len(dns_entry_list) + 1
        dns_entry = {
                'id': dns_entry_id,
                'ip': ip,
                'hostname': hostname,
        }

        # prepare new dns table
        dns_entry_list.append(dns_entry)
        dns_entry = {'dns-entry': dns_entry_list}

        # update zone
        response = self.session.put(url, json=dns_entry)
        
        return response


    def get(self):
        '''Get all entries of a specific DNS Zone'''
        url = f'{self.base_url}/cmdb/system/dns-database/{self.name}'
        response = self.session.get(url=url, timeout=self.timeout)
        return response


    def delete(self):
        '''Delete DNS Zone'''
        url = f'{self.base_url}/cmdb/system/dns-database/{self.name}'
        response = self.session.delete(url=url, timeout=self.timeout)
        return response
