import requests
from .utils import get_credentials
from datetime import datetime


class FortiCare(object):
    def __init__(self, username):
        '''
        username: email registered on support.fortinet.com with token access
        '''
        #: Use the same session for all requests
        self.session = requests.session()

        self.username = username

        #: SSL Verification default.
        self.session.verify = False

        #: How long to wait for the server to send data before giving up
        self.timeout = 10

        #: Base URL for all requests
        self.base_url = 'https://support.fortinet.com/ES/FCWS_RegistrationService.svc/REST'

        # token
        self.token = None

    def open(token=None):
        if not (token):
        credentials = get_credentials(self.username)
        token = credentials['token']

    def get_assets(serial_number=None, expire_date='3000/12/30'):
        '''
        Input expire_data in the format 'YYYY/MM/DD'
        '''
        url = f'{self.base_url}/REST_GetAssets'
        
        data = {'Token': self.token, 'Version': '1.0'}

        datetime_obj = datetime.strptime(expire_date, '%Y/%m/%d')
        expire_before = datetime_obj.isoformat()
        data['Expire_Before'] = expire_before

        r = session.post(url, json=data)
        return r

    def get_assets_by_serial(serial_number):
        url = f'{self.base_url}/REST_GetAssets'
        
        data = {'Token': self.token, 'Version': '1.0'}

        data['Serial_Number'] = serial_number

        r = session.post(url, json=data)
        return r
