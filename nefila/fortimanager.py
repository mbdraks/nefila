import requests
# from .utils import get_credentials
from .fortiManagerAnalyzerCore import FortiManagerAnalyzerCore

class FortiManager(FortiManagerAnalyzerCore):
    '''FortiManager class, implements methods specific to FMG'''
    def __init__(self, hostname):
        #: Inherit all attributes from FortiManagerAnalyzerCore Class
        super().__init__(hostname)

        # #: Use the same session for all requests
        # self.session = requests.session()

        # #: SSL Verification default.
        # self.session.verify = False

        # #: How long to wait for the server to send data before giving up
        # self.timeout = 10

        # #: Device hostname
        # self.hostname = hostname

        # #: Base URL for all requests
        # self.base_url = f'https://{self.hostname}/jsonrpc'

        # # : Session ID
        # self.session_id = None

        # Subsystems init
        # self.devices = Devices(self.session, self.timeout, self.base_url, self.session_id)
        self.devices = Devices(self)


    def prepare_json(self, url, method='get', data=None):
        '''Prepare FMG JSON request with appropriate parameters'''
        params = {}
        params['url'] = url
        params['data'] = data
        
        json = {}
        json['id'] = 1
        json['method'] = method
        json['session'] = self.session_id
        json['jsonrpc'] = '2.0'
        json['params'] = [params]

        return json

class Devices(object):
    def __init__(self, fmg):
        self.fmg = fmg

    def proxy(self, device, http_method='get', endpoint='monitor/system/status'):
        '''Send a JSON request to a managed device'''
        data = {}
        data['target'] = [f'/device/{device}']
        data['action'] = http_method
        data['resource'] = f'/api/v2/{endpoint}'

        url = f'/sys/proxy/json'
        method = 'exec'

        json = self.fmg.prepare_json(data=data, url=url, method=method)

        r = self.fmg.session.post(url=self.fmg.base_url, json=json, timeout=self.fmg.timeout)
        return r

    # def list(self, adom='root'):
    #     '''List managed devices
        
    #     mgmt_mode
    #         2 Unauthorized
        
    #     '''
    #     url = f'dvmdb/device'
    #     json = self.fmg.prepare_json(url=url)
    #     r = self.fmg.session.post(url=self.fmg.base_url, json=json, timeout = self.fmg.timeout)
    #     return r
