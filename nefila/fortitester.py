import requests
from .utils import get_credentials


class FortiTester(object):
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
        self.base_url = f'https://{self.hostname}/api'
        
        # Subsystems init
        self.user = User(self.session, self.timeout, self.base_url)
        self.system = System(self.session, self.timeout, self.base_url)


    def open(self, username=None, password=None):
        credentials = {}
        
        # If credentials are not supplied, check file
        if not (username):
            credentials = get_credentials(self.hostname)
            username = credentials['username']
            password = credentials['password']

        url = f'{self.base_url}/user/login'

        data = {
            'name': username,
            'password': password
        }

        r = self.session.post(url=url, json=data, timeout=self.timeout)
        return r


    def close(self):
        url = f'{self.base_url}/user/logout'

        r = self.session.get(url=url, timeout=self.timeout)
        return r


    def _get_status(self):
        '''Obtain general status
        '''
        status = {}
        url = f'{self.base_url}/system/status'
        r = self.session.get(url=url, timeout=self.timeout)
        status['hostname'] = r.json()['Data']['hostname']
        status['uptime'] = r.json()['Data']['uptime']

        url = f'{self.base_url}/system/info'
        r = self.session.get(url=url, timeout=self.timeout)
        status['forticare'] = r.json()['Data']['License']['Status']
        status['version'] = r.json()['Data']['Version']
        status['model'] = r.json()['Data']['Platform']
        status['serial'] = r.json()['Data']['SN']
        
        return status

    @property
    def status(self):
        return self._get_status()


    def basic_status(self):
        '''Retrieve basic system status.'''
        url = f'{self.base_url}/system/status'
        r = self.session.get(url=url, timeout=self.timeout)
        return r


class User(object):
    def __init__(self, session, timeout, base_url):
        self.session = session
        self.timeout = timeout
        self.base_url = base_url
        self.username = None

    def list(self):
        '''List users
        
        Usage:
            device.user.list()
        '''

        url = f'{self.base_url}/user'
        r = self.session.get(url=url, timeout=self.timeout)
        return r

    def info(self):
        '''Obtain info from specific user
        
        Usage:
            device.user.username = 'admin'
            device.user.info()
        '''

        # Obtain UserId from name
        # Obtain all users
        userList = self.list().json()['payload']

        for user in userList:
            if user['name'] == self.username:
                self.userId = user['_id']

        # Once UserId is set, obtain info
        url = f'{self.base_url}/user/{self.userId}'
        r = self.session.get(url=url, timeout=self.timeout)
        return r

    def modify_password(self, oldpassword, newpassword):
        '''Modify user password
        
        Usage:
            device.user.username = 'admin'
            device.user.modify_password(oldpassword='oldpwd', newpassword='newpwd')
        '''

        # Obtain UserId from name

        # Obtain all users
        userList = self.list().json()['payload']

        for user in userList:
            if user['name'] == self.username:
                self.userId = user['_id']

        # Once UserId is set, change pwd

        url = f'{self.base_url}/user/{self.userId}/modifyPassword'

        data = {
            'oldPsw': oldpassword,
            'newPsw': newpassword,
            'cfmNewPsw': newpassword,
            '_id': self.userId,
        }

        r = self.session.put(url=url, json=data, timeout=self.timeout)
        return r


class System(object):
    def __init__(self, session, timeout, base_url):
        self.session = session
        self.timeout = timeout
        self.base_url = base_url

    def reboot(self):
        '''Reboot system
        
        Usage:
            device.system.reboot()
        '''

        url = f'{self.base_url}/system/reboot'
        r = self.session.post(url=url, timeout=self.timeout)
        return r

    # def license_upload(self, filename=None, timeout=300):
    #     '''Upload license'''
    #     url = f'{self.base_url}/system/upload/license'

    #     data = {'source': 'upload', 'scope': 'global'}
    #     f = open(filename, 'rb')
    #     firmware_file = {'file': (filename, f, 'text/plain')}

    #     r = self.session.post(
    #                         url=url,
    #                         data=data,
    #                         files=firmware_file,
    #                         timeout=timeout
    #     )

    #     return r

    # Request URL: https://hostname/api/system/upload/license
    # Request URL: https://hostname/api/system/licenseUploadStatus?t=1573603039259
