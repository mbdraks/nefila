import requests
from .utils import get_credentials


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

        #: Default username
        self.username = 'admin'

        self.url_prefix = ''

        self.system = System(self.session, self.timeout, self.hostname)

    def open(self, username='admin', password='', token=None, verify=False):

        # credentials = get_credentials(hostname)

        # if credentials:
        #     username = credentials['username']
        #     password = credentials['password']

        # Update parameters
        hostname = self.hostname
        self.username = username
        self.verify = verify
        self.url_prefix = f'https://{hostname}'
        url_login = f'{self.url_prefix}/logincheck'

        response = self.session.post(url=url_login,
                                    data=f'username={username}&secretkey={password}',
                                    verify = verify,
                                    timeout = self.timeout,
        )

        for cookie in self.session.cookies:
            if cookie.name == 'ccsrftoken':
                csrftoken = cookie.value[1:-1] # token stored as a list
                self.session.headers.update({'X-CSRFTOKEN': csrftoken})

        return response.status_code


    def _close(self):
        url_logout = f'{self.url_prefix}/logout'
        response = self.session.post(url_logout, timeout=self.timeout)
        return response.status_code

    @property
    def close(self):
        return self._close()


    def _get_status(self):
        url = f'{self.url_prefix}/api/v2/monitor/license/status'
        response = self.session.get(url, timeout=self.timeout)
        if response.status_code == 200:
            status = {}
            status['version'] = response.json()['version']
            status['serial'] = response.json()['serial']
            status['forticare'] = response.json()['results']['forticare']['status']

        url = f'{self.url_prefix}/api/v2/monitor/web-ui/state'
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


class System(object):
    def __init__(self, session, timeout, hostname):
        self.session = session
        self.timeout = timeout
        self.hostname = hostname
        self.dns_database = DnsDatabase(self.session, self.timeout, self.hostname, name=None)

    def dns_database_test(self, action=None):
        url = f'https://{self.hostname}/api/v2/cmdb/system/dns-database?action={action}'
        response = self.session.get(url, timeout=self.timeout)
        return response

class DnsDatabase(object):
    '''Add or check records on the DNS Database.

    Usage:
        device.system.dns_database.name = 'exampleZone'
        device.system.dns_database.add(ip='192.2.0.1', hostname='example')
        device.system.dns_database.get().json()
    '''

    def __init__(self, session, timeout, hostname, name):
        self.session = session
        self.timeout = timeout
        self.hostname = hostname
        self.name = name

    def add(self, ip, hostname):
        
        # Obtain existing list
        url = f'https://{self.hostname}/api/v2/cmdb/system/dns-database/{self.name}'
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
        
        url = f'https://{self.hostname}/api/v2/cmdb/system/dns-database/{self.name}'
        response = self.session.get(url=url, timeout=self.timeout)
        return response

# zone = device.system.dns_database(name='home')
# zone.add(ip=ip, hostname=hostname)