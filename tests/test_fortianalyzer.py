
import pytest
import os

import nefila
import nefila.utils

hostname = os.getenv('FAZ_HOSTNAME', '192.168.0.20')
username = os.getenv('NEFILA_USERNAME', 'nefila-admin')
password = os.getenv('NEFILA_PASSWORD', 'nefila-password')
credentials = {'username': username, 'password': password}

@pytest.fixture
def manager():
    '''Device setup and teardown'''
    manager = nefila.FortiAnalyzer(hostname)
    manager.open(**credentials)
    yield manager
    manager.close()

def test_login_live(manager):
    print(manager.status)
    assert manager.hostname == hostname

def test_device_status(manager):
    status = manager.status

    expected_status = {
        'serial': 'FAZ-VMTM19009199',
        'version': 'v6.2.2',
        'forticare': 'Valid',
        'hostname': 'FAZ',
        'model': 'FortiAnalyzer-VM64'
    }

    # check if keys exist
    assert status.keys() == expected_status.keys()

def test_basic_status(manager):
    manager.basic_status()

# def test_license_status(manager):
#     manager.license_status()

def test_device_list(manager):
    manager.device_list()
    # manager.devices.list()

def test_promote_unauthorized_device(manager):
    # manager.devices.authorize()
    pass


# url = '/dvm/cmd/promote/dev-list'

# params = {}
# params['url'] = url

# data = {}
# data['id'] = 1
# data['method'] = 'exec'
# data['session'] = device.session_id
# data['jsonrpc'] = '2.0'
# data['params'] = [params]

# r = device.session.post(url=device.base_url, json=data, timeout = device.timeout)

## OPCAO minima

# {
#   "id": 1, 
#   "method": "exec", 
#   "params": [
#     {
#       "data": {
#         "add-dev-list": [
#           {
#             "adm_usr": "admin", 
#             "flags": 2097216, 
#             "ip": "192.168.244.101", 
#             "name": "FGVM08REDACTED58", 
#             "oid": "143", 
#             "sn": "FGVM08REDACTED58"
#           }
#         ], 
#         "adom": "CM_LAB_001", 
#         "del-dev-list": null, 
#         "flags": [
#           "create_task", 
#           "nonblocking"
#         ]
#       }, 
#       "url": "dvm/cmd/promote/dev-list"
#     }
#   ], 
#   "session": "6uoD6pUVIMWFeU6Ci5v/RH7Hl0Vje4GVmjHQEfpFqLoBmH4IX/sUDDzGDh3cdR6hOsdOKAjmtgKCWAfR/cFhZg==", 
#   "verbose": 1
# }

# {
#   "client": "gui DVM:3208",
#   "id": 1,
#   "method": "exec",
#   "params": [
#     {
#       "data": {
#         "add-dev-list": [
#           {
#             "adm_usr": "admin",
#             "beta": -1,
#             "branch_pt": 932,
#             "build": 932,
#             "conn_mode": 0,
#             "dev_status": 0,
#             "faz.perm": 15,
#             "flags": 2097216,
#             "ip": "10.100.0.254",
#             "maxvdom": 10,
#             "mgmt_id": 446165699,
#             "mr": 2,
#             "name": "DC01",
#             "oid": 135,
#             "os_type": 0,
#             "os_ver": 6,
#             "patch": 1,
#             "platform_id": 95,
#             "platform_str": "FortiGate-VM64",
#             "sn": "FGVM04TM19006086",
#             "source": 2,
#             "tab_status": "<unknown>",
#             "version": 600
#           }
#         ],
#         "adom": 3,
#         "del-dev-list": null,
#         "flags": 3
#       },
#       "url": "dvm\/cmd\/promote\/dev-list"
#     }
#   ],
#   "session": 30350
# }
    
    pass
