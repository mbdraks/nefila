import requests
from .utils import get_credentials
from .fortiManagerAnalyzerCore import FortiManagerAnalyzerCore

class FortiManager(FortiManagerAnalyzerCore):

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
        self.devices = Devices(self.session, self.timeout, self.base_url, self.session_id)


class Devices(object):
    def __init__(self, session, timeout, base_url, session_id):
        self.session = session
        self.timeout = timeout
        self.base_url = base_url
        self.session_id = session_id
