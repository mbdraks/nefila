import requests
from .utils import get_credentials
import json
import time
import datetime


class FortiGate(object):
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
        self.vdom = 'root'
        self.token = False

        # Subsystems init
        self.system = System(self.session, self.timeout, self.base_url, device=self)

    def open(self, username=None, password=None, token=None, profile=None):
        # If credentials are not supplied, check file
        if not (username or token or profile):
            credentials = get_credentials(self.hostname)
            username = credentials['username']
            password = credentials['password']
            token = credentials['token']

        # Update parameters
        self.username = username

        if token:
            self.session.headers.update({'Authorization': f'Bearer {token}'})
            self.token = True
        else:
            authenticated = self._api_authentication_login(username, password)

            if not authenticated:
                self._logincheck_login(username, password)

        # Call to license status during login to auto set device details
        r = self.license_status()
        return r

    def _api_authentication_login(self, username, password):
        """
        Authenticate using FortiOS API-based username/password flow.

        This supports newer FortiOS versions where POST /api/v2/authentication
        may return the session in two different formats:

        1. JSON-based session:
           {
               "session_key": "..."
           }

           In this case, use:
           Authorization: Bearer <session_key>

        2. Cookie-based session:
           session_key_443_xxx=...
           ccsrf_token_443_xxx=...

           In this case, use:
           Cookie: session_key_...=...; ccsrf_token_...=...
           x-csrftoken: <ccsrf_token value>

        Returns True when authentication appears successful.
        Returns False when the endpoint is unavailable or login failed, so callers
        can fall back to the legacy /logincheck flow.
        """
        url = f'{self.base_url}/authentication'

        payload = {
            'username': username,
            'secretkey': str(password),
            'password': str(password),
            'ack_post_disclaimer': True,
            'ack_pre_disclaimer': True,
            'request_key': True,
        }

        response = self.session.post(
            url=url,
            json=payload,
            timeout=self.timeout,
        )

        if response.status_code != 200:
            return False

        try:
            data = response.json()
        except ValueError:
            return False

        if data.get('status_message') != 'LOGIN_SUCCESS':
            return False

        json_session_key = data.get('session_key')

        if json_session_key:
            self.session.headers.update({'Authorization': f'Bearer {json_session_key}'})
            return True

        cookie_header = []
        csrf_token = None
        has_session_cookie = False

        for cookie in self.session.cookies:
            cookie_name = cookie.name.lower()

            if cookie_name.startswith('session_key'):
                has_session_cookie = True
                cookie_header.append(f'{cookie.name}={cookie.value}')

            elif (
                cookie_name.startswith('ccsrf_token')
                or cookie_name.startswith('ccsrftoken')
                or cookie_name.startswith('ccsrf')
            ):
                csrf_token = cookie.value.strip('"')
                cookie_header.append(f'{cookie.name}={cookie.value}')

            elif cookie_name.startswith('cmgmt_override'):
                cookie_header.append(f'{cookie.name}={cookie.value}')

            elif cookie_name.startswith('apscookie'):
                cookie_header.append(f'{cookie.name}={cookie.value}')

        if has_session_cookie:
            self.session.headers.update({'Cookie': '; '.join(cookie_header)})

            if csrf_token:
                self.session.headers.update({'x-csrftoken': csrf_token})

            return True

        return False

    def _logincheck_login(self, username, password):
        """
        Legacy FortiOS GUI/session login used by older nefila versions.

        This preserves backward compatibility with the original login flow.
        If the original payload does not create a session, it also tries the
        ajax=1 format used by newer FortiOS clients.
        """
        url_login = f'https://{self.hostname}/logincheck'

        response = self.session.post(
            url=url_login,
            data=f'username={username}&secretkey={password}',
            timeout=self.timeout,
        )

        self._apply_csrf_from_cookies()

        if self._has_session_cookie():
            return response

        response = self.session.post(
            url=url_login,
            data={
                'username': username,
                'secretkey': password,
                'ajax': '1',
            },
            timeout=self.timeout,
        )

        self._apply_csrf_from_cookies()
        return response

    def _has_session_cookie(self):
        """
        Return True if the current session has a FortiOS session cookie.
        """
        for cookie in self.session.cookies:
            cookie_name = cookie.name.lower()

            if (
                cookie_name.startswith('session_key')
                or cookie_name.startswith('apscookie')
            ):
                return True

        return False

    def _apply_csrf_from_cookies(self):
        """
        Apply FortiOS CSRF token from cookies to the session headers.

        Older FortiOS versions may use ccsrftoken.
        Newer FortiOS versions may use ccsrf_token_<port>_<hash>.
        """
        cookie_header = []
        csrf_token = None

        for cookie in self.session.cookies:
            cookie_name = cookie.name.lower()

            if (
                cookie_name.startswith('session_key')
                or cookie_name.startswith('apscookie')
                or cookie_name.startswith('cmgmt_override')
                or cookie_name.startswith('ccsrf_token')
                or cookie_name.startswith('ccsrftoken')
                or cookie_name.startswith('ccsrf')
            ):
                cookie_header.append(f'{cookie.name}={cookie.value}')

            if 'ccsrftoken' in cookie_name:
                csrf_token = cookie.value.strip('"')

            elif (
                cookie_name.startswith('ccsrf_token')
                or cookie_name.startswith('ccsrf')
            ):
                csrf_token = cookie.value.strip('"')

        if cookie_header:
            self.session.headers.update({'Cookie': '; '.join(cookie_header)})

        if csrf_token:
            self.session.headers.update({'X-CSRFTOKEN': csrf_token})
            self.session.headers.update({'x-csrftoken': csrf_token})

    def close(self):
        url_logout = f'https://{self.hostname}/logout'
        response = self.session.post(url_logout, timeout=self.timeout)
        return response.status_code

    def _get_status(self):
        '''Obtain general status

        Uptime in seconds

        '''
        status = {}

        url = f'{self.base_url}/monitor/license/status'
        response = self.session.get(url, timeout=self.timeout)

        if response.status_code == 200:
            data = response.json()
            status['version'] = data.get('version')
            status['serial'] = data.get('serial')
            status['forticare'] = data.get('results', {}).get('forticare', {}).get('status')

        url = f'{self.base_url}/monitor/web-ui/state'
        response = self.session.get(url, timeout=self.timeout)

        if response.status_code == 200:
            data = response.json()
            results = data.get('results', {})

            model_name = results.get('model_name')
            model_number = results.get('model_number')

            ticks = results.get('utc_last_reboot')

            if ticks is not None:
                ticks_to_seconds = ticks / 1000
                uptime = time.time() - ticks_to_seconds
                uptime = datetime.timedelta(seconds=uptime)
                status['uptime'] = uptime.seconds
            else:
                status['uptime'] = None

            status['hostname'] = results.get('hostname')
            status['model'] = f'{model_name}-{model_number}'

            return status

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
        response = self.session.get(url, timeout=self.timeout)

        if response.status_code == 200:
            data = response.json()
            self.version = data.get('version')
            self.serial = data.get('serial')
            self.forticare = data.get('results', {}).get('forticare', {}).get('status')

        return response


class System(object):
    def __init__(self, session, timeout, base_url, device):
        self.session = session
        self.timeout = timeout
        self.base_url = base_url
        self.device = device

        self.dns_database = DnsDatabase(self.session, self.timeout, self.base_url, name=None, device=device)
        self.firmware = Firmware(self.session, self.timeout, self.base_url)
        self.api_user = ApiUser(self.session, self.timeout, self.base_url, name='nefila-api-admin')
        self.interface = Interface(self.session, self.timeout, self.base_url)
        self.config = Config(self.session, self.timeout, self.base_url)
        self.license = License(self.session, self.timeout, self.base_url)
        self.config_revision = ConfigRevision(self.session, self.timeout, self.base_url)


class License(object):
    '''Manage VM License upload

    Usage:
        device.system.license.restore(filename='license.lic')
    '''

    def __init__(self, session, timeout, base_url):
        self.session = session
        self.timeout = timeout
        self.base_url = f'{base_url}/monitor/system/vmlicense'

    def restore(self, filename=None):
        '''Update VM license using uploaded file'''
        url = f'{self.base_url}/upload'

        data = {
            'source': 'upload',
            'scope': 'global',
        }

        f = open(filename, 'rb')
        files = {'file': (filename, f, 'text/plain')}

        r = self.session.post(
            url=url,
            data=data,
            files=files,
            timeout=self.timeout
        )
        return r


class Config(object):
    '''Manage system configuration

    Usage:
        device.system.config.restore(filename='config.cfg')
        device.system.config.restore(filename='config.cfg')
        device.system.config.backup(filename='config.cfg')
        device.system.config.backup(filename='config.cfg', vdom='vd01')

    '''

    def __init__(self, session, timeout, base_url):
        self.session = session
        self.timeout = timeout
        self.base_url = f'{base_url}/monitor/system/config'

    def restore(self, filename=None, config_id=None):
        '''Restore system configuration from uploaded file'''
        url = f'{self.base_url}/restore'

        if filename:
            data = {
                'source': 'upload',
                'scope': 'global',
            }

            f = open(filename, 'rb')
            files = {'file': (filename, f, 'text/plain')}

            r = self.session.post(
                url=url,
                data=data,
                files=files,
                timeout=self.timeout
            )
            return r

        elif config_id:
            data = {
                'source': 'revision',
                'config_id': config_id,
                'scope': 'global',
            }

            r = self.session.post(
                url=url,
                json=data,
                timeout=self.timeout
            )
            return r

        else:
            return None


class ConfigRevision(object):
    '''Manage system configuration

    Usage:
        device.system.config_revision.create()
        device.system.config_revision.list()

    '''

    def __init__(self, session, timeout, base_url):
        self.session = session
        self.timeout = timeout
        self.base_url = f'{base_url}/monitor/system/config-revision'

    def list(self):
        '''Return a list of system configuration revisions'''
        url = f'{self.base_url}/select'

        r = self.session.get(url=url, timeout=self.timeout)
        return r


class Interface(object):
    '''List and configure interfaces

    Usage:
        device.system.interface.list()
        device.system.interface.create()
        device.system.interface.get()
        device.system.interface.get(name='wan1')
        device.system.interface.delete()
    '''

    def __init__(self, session, timeout, base_url):
        self.session = session
        self.timeout = timeout
        self.base_url = base_url

    def list(self):
        '''List all interfaces'''
        url = f'{self.base_url}/monitor/system/available-interfaces'
        r = self.session.get(url=url, timeout=self.timeout)
        return r


class ApiUser(object):
    '''List and configure API users.

    Default API user is nefila-api-admin using super_admin profile and
    trusted hosts 192.168.0.0/16.

    Usage:
        device.system.api_user.list()
        device.system.api_user.create()
        device.system.api_user.token
        device.system.api_user.get()
        device.system.api_user.delete()

        device.system.api_user.name = 'custom-api-admin'
        device.system.api_user.create(accprofile='prof_admin',
                            ipv4_trusthost='192.0.2.0/24')
    '''

    def __init__(self, session, timeout, base_url, name):
        self.session = session
        self.timeout = timeout
        self.base_url = base_url
        self.name = name

    def list(self):
        '''List all API users'''
        url = f'{self.base_url}/cmdb/system/api-user'
        response = self.session.get(url=url, timeout=self.timeout)
        return response

    def create(self, accprofile='super_admin', ipv4_trusthosts=['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16'], vdom='root'):
        '''Create a new API user and generate an access key'''
        url = f'{self.base_url}/cmdb/system/api-user'
        name = self.name
        token = None

        trusthosts = []
        for host in ipv4_trusthosts:
            d = {
                'id': 0,
                'type': 'ipv4-trusthost',
                'ipv4-trusthost': host,
            }
            trusthosts.append(d)

        data = {
            'name': name,
            'accprofile': accprofile,
            'trusthost': trusthosts,
            'vdom': [{'name': vdom}],
        }

        r = self.session.post(url=url, json=data)

        if r.status_code == 200:
            data = {'api-user': self.name}
            url = f'{self.base_url}/monitor/system/api-user/generate-key'
            r = self.session.post(url=url, json=data)
            token = r.json()['results']['access_token']
            self.token = token

        return r

    def get(self):
        '''Get details of a specific API user'''
        url = f'{self.base_url}/cmdb/system/api-user/{self.name}'
        response = self.session.get(url=url, timeout=self.timeout)
        return response

    def delete(self):
        '''Delete API user'''
        url = f'{self.base_url}/cmdb/system/api-user/{self.name}'
        response = self.session.delete(url=url, timeout=self.timeout)
        return response


class Firmware(object):
    '''List and upgrade device firmware.

    Usage:
        device.system.firmware.list()
        device.system.firmware.upgrade()
        device.system.firmware.upgrade('v6.2.0')
        device.system.firmware.upgrade_file('./var/FGT_VM64_KVM-v6-build1510-FORTINET.out')
    '''

    def __init__(self, session, timeout, base_url):
        self.session = session
        self.timeout = timeout
        self.base_url = base_url

    def list(self):
        '''Retrieve a list of firmware images available to use for
        upgrade on this device from FortiGuard'''
        url = f'{self.base_url}/monitor/system/firmware'
        response = self.session.get(url=url, timeout=self.timeout)
        return response

    def upgrade(self, version=None, timeout=300):
        '''Upgrade firmware image on this device
        Default timeout is longer to allow firmware download from FDN'''
        url = f'{self.base_url}/monitor/system/firmware/upgrade'

        firmware_list = self.list().json()['results']['available']

        if not version:
            version_id = firmware_list[0]['id']

        # If version is set, find corresponding version_id
        # If version equals None then update to the latest available
        if version:
            for firmware in firmware_list:
                if firmware['version'] == version:
                    version_id = firmware['id']
        else:
            version_id = firmware_list[0]['id']

        data = {'source': 'fortiguard', 'filename': version_id}
        r = self.session.post(url=url, json=data, timeout=timeout)

        return r

    def upgrade_file(self, filename=None, timeout=300):
        '''Upgrade firmware image on this device using an uploaded file
        Default timeout is longer to allow firmware download from FDN'''
        url = f'{self.base_url}/monitor/system/firmware/upgrade'

        data = {'source': 'upload', 'scope': 'global'}
        f = open(filename, 'rb')
        files = {'file': (filename, f, 'text/plain')}

        r = self.session.post(
            url=url,
            data=data,
            files=files,
            timeout=timeout
        )

        return r


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

    def __init__(self, session, timeout, base_url, name, device):
        self.session = session
        self.timeout = timeout
        self.base_url = base_url
        self.name = name
        self.device = device

    def list(self):
        '''List all DNS zones'''
        url = f'{self.base_url}/cmdb/system/dns-database'
        params = {'vdom': self.device.vdom}
        r = self.session.get(url=url, timeout=self.timeout, params=params)
        return r

    def create(self):
        '''Create a new DNS Zone'''
        url = f'{self.base_url}/cmdb/system/dns-database'
        data = {'name': self.name, 'domain': self.name}
        params = {'vdom': self.device.vdom}

        r = self.session.post(url=url, json=data, params=params)
        return r

    def add(self, ip, hostname):
        '''Add a new entry on a specific existing DNS Zone, preserving
        existing entries.
        '''
        # Obtain existing list
        url = f'{self.base_url}/cmdb/system/dns-database/{self.name}'
        response = self.session.get(url=url, timeout=self.timeout)
        dns_entry_list = response.json()['results'][0]['dns-entry']

        # Prepare the new entry
        dns_entry_id = len(dns_entry_list) + 1
        dns_entry = {
            'id': dns_entry_id,
            'ip': ip,
            'hostname': hostname,
        }

        # Prepare new DNS table
        dns_entry_list.append(dns_entry)
        dns_entry = {'dns-entry': dns_entry_list}

        # Update zone
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
