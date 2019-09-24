import requests
from .utils import get_credentials
from .system import dns_database

class FortiGate(object):
    def __init__(self):
        #: Use the same session for all requests
        self.session = requests.session()

        #: SSL Verification default.
        self.verify = False

        #: How long to wait for the server to send data before giving up
        self.timeout = 10

        #: Device hostname
        self.hostname = None

        #: Default username
        self.username = 'admin'


    def open(self, hostname, username='admin', password='', token=None,
        verify=False):

        # credentials = get_credentials(hostname)

        # if credentials:
        #     username = credentials['username']
        #     password = credentials['password']

        # Update parameters
        self.hostname = hostname
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

