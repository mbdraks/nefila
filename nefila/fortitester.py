import requests
import json
import os
from .modelmeta import DataModelProxy

import logging
import daiquiri
import sys
from collections import OrderedDict

# logging

# loglevel = os.getenv("FORTITESTER_LOGLEVEL", "DEBUG")
# logfile = "/dev/null"
logfile = "logfile.json"

daiquiri.setup(
    outputs=(
        daiquiri.output.Stream(sys.stdout),
        daiquiri.output.File(logfile, formatter=daiquiri.formatter.JSON_FORMATTER),
    ),
)

log = daiquiri.getLogger(__name__)
log.setLevel(os.environ.get("LOGLEVEL", "INFO"))


class FortiTester(object):
    def __init__(self, host):
        self.host = host
        self.base_url = f"https://{self.host}/api"
        self.username = None
        self.session = requests.session()
        self.session.verify = False
        self.timeout = 10
        # Endpoints
        self.system = DataModelProxy(wrapper=self, name="system")
        self.user = DataModelProxy(wrapper=self, name="user")
        self.objectConfig = DataModelProxy(wrapper=self, name="objectConfig")

    def open(self, username=None, password=None):
        """
        Login
        :param username (string): Username
        :param password (string): Password

        This function will load credentials from env vars if available:
            - NEFILA_USERNAME
            - NEFILA_PASSWORD
        """
        if username is None:
            username = os.getenv("NEFILA_USERNAME", "admin")
            password = os.getenv("NEFILA_PASSWORD", "")

        self.username = username

        credentials = {"name": username, "password": password}
        path = "/user/login"
        return self._post(path, **credentials)

    def close(self):
        # url = f"{self.base_url}/user/logout"
        path = "/user/logout"
        return self._get(path)
        # r = self.session.get(url=url, timeout=self.timeout)
        # return r

    @property
    def status(self):
        return self.system.status.get()

    def _get(self, path, *args, **kwargs):
        url = f"{ self.base_url }{ path }"

        for key, value in kwargs.items():
            url = url + "&%s=%s" % (key, value)

        r = self.session.get(url=url, timeout=self.timeout)

        func_name = sys._getframe().f_code.co_name
        self.gen_log(r, func_name)

        self.raw = r

        r = self.try_json_response(r)
        return r

    def _post(self, path, *args, **kwargs):
        url = f"{ self.base_url }{ path }"
        if args is not None:
            for arg in args:
                kwargs = arg

        r = self.session.post(url=url, json=kwargs)

        func_name = sys._getframe().f_code.co_name
        self.gen_log(r, func_name)

        self.raw = r

        r = self.try_json_response(r)
        return r

    def _put(self, path, value, *args, **kwargs):
        url = f"{ self.base_url }{ path }"

        if args is not None:
            for arg in args:
                print(arg)
                kwargs = arg

        r = self.session.put(url=url, json=kwargs)
        return r

    # user
    @staticmethod
    def _user_operations_create(self, *args, **kwargs):
        """
        Create user
        :param name (string): User name
        :param password (string): Password
        :param role (string): Role of the user
        """
        path = "/user"
        return self._wrapper._post(path, *args, **kwargs)

    @staticmethod
    def _user_operations_delete(self, *args, **kwargs):
        """
        Delete user
        :param ids (array): List of User IDs
        """
        path = "/user/delete"
        return self._wrapper._post(path, **kwargs)

    # network
    @staticmethod
    def _objectConfig_network_operations_create(self, *args, **kwargs):
        """
        Create Network
        :param config (string): The json of network config
        """
        path = "/objectConfig/network"
        return self._wrapper._post(path, *args, **kwargs)

    @staticmethod
    def _objectConfig_network_operations_delete(self, *args, **kwargs):
        """
        Delete Network
        :param ids (array): Network configuration IDs
        """
        path = "/objectConfig/network/delete"
        return self._wrapper._post(path, *args, **kwargs)

    @staticmethod
    def _objectConfig_network_operations_find(self, *args, **kwargs):
        """
        Get Network By IDs
        :param ids (array): IDs of network configuration
        """
        path = "/objectConfig/network/find"
        return self._wrapper._post(path, *args, **kwargs)

    # utils
    def gen_log(self, r, func_name, level="INFO"):
        # breakpoint()
        resp_body = self.try_json_response(r)

        if type(r.request.body) == bytes:
            req_body = r.request.body.decode("utf-8")
            req_body = json.loads(req_body)
        else:
            req_body = r.request.body

        # message = OrderedDict()
        message = {
            "httpRequest": {
                "method": r.request.method,
                "path": r.request.path_url,
                "headers": dict(r.request.headers),
                "body": req_body,
            },
            "httpResponse": {
                "statusCode": r.status_code,
                "reasonPhrase": r.reason,
                "headers": dict(r.headers),
                "cookies": dict(r.cookies.items()),
                "body": resp_body,
            },
        }

        module_name = f"{ __name__ }.{ func_name }"

        debug_paths = ["/api/user/login", "/api/user/logout"]
        error_codes = [401]

        if r.request.path_url in debug_paths:
            level = "DEBUG"

        if r.status_code in error_codes:
            level = "ERROR"

        if level == "CRITICAL":
            log.critical(module_name, **message)
        elif level == "ERROR":
            log.error(module_name, **message)
        elif level == "WARNING":
            log.warning(module_name, **message)
        elif level == "INFO":
            log.info(module_name, **message)
        else:
            log.debug(module_name, **message)

    def try_json_response(self, r):
        if r.content is not None:
            try:
                return r.json()
            except json.decoder.JSONDecodeError as e:
                return r.text
        else:
            return r