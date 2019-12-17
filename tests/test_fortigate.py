
import pytest
import os
from pprint import pprint

import nefila
import nefila.utils

hostname = os.getenv('FORTIGATE_HOSTNAME', '192.168.0.30')
username = os.getenv('NEFILA_USERNAME', 'nefila-admin')
password = os.getenv('NEFILA_PASSWORD', 'nefila-password')
token = os.getenv('NEFILA_TOKEN', '')
credentials = {'username': username, 'password': password}

@pytest.fixture
def device():
    '''Device setup and teardown'''
    device = nefila.FortiGate(hostname)
    device.open(**credentials)
    yield device
    device.close()


# Login
def test_login_live(device):
    r = device.status
    print(r)
    print(device.hostname)
    assert device.hostname == hostname

def test_login_credentials_file():
    nefila.utils.set_credentials(hostname, **credentials)
    device = nefila.FortiGate(hostname)
    r = device.open()
    print(r)
    assert r.status_code == 200

# def test_login_failure():
#     pass

# def test_login_token():
#     pass

def test_device_status(device):
    r = device.status
    expected_status = {
        'version': '',
        'serial': '',
        'forticare': '',
        'hostname': '',
        'model': '',
        'uptime': 0,
    }
    assert r.keys() == expected_status.keys()


# System
## DNS Database
def test_dns_database(device):
    device.system.dns_database.list()
    device.system.dns_database.name = 'exampleZone'
    device.system.dns_database.create()
    device.system.dns_database.add(ip='192.2.0.1', hostname='example')
    device.system.dns_database.get()
    device.system.dns_database.delete()


## Firmware
def test_system_firmware_list(device):
    r = device.system.firmware.list()
    assert r.status_code == 200

# def test_system_firmware_upgrade_latest(device):
    # device.system.firmware.upgrade()
    # pass

# def test_system_firmware_upgrade_specific(device):
    # r = device.system.firmware.upgrade('v6.2.0')
    # expected_response = {
    #     'http_method': 'POST',
    #     'results': {'status': 'success'},
    #     'vdom': 'root',
    #     'path': 'system',
    #     'name': 'firmware',
    #     'action': 'upgrade',
    #     'status': 'success',
    #     'serial': 'FGVULVTM19000XXX',
    #     'version': 'v6.2.0',
    #     'build': 799
    # }
    # assert r.json() == expected_response
    # pass

# def test_system_firmware_upgrade_valid_image(device):
    # device.system.firmware.upgrade_file('./var/valid.out')
    # pass

# def test_system_firmware_upgrade_invalid_image(device):
    # device.system.firmware.upgrade_file('./var/invalid.out')

    # '''
    # Expected response
    # {
    #     'http_method': 'POST',
    #     'results': {'status': 'error',
    #     'error': {'message': 'Firmware image is not valid.', 'code': -593}},
    #     'vdom': 'root',
    #     'path': 'system',
    #     'name': 'firmware',
    #     'action': 'upgrade',
    #     'status': 'success',
    #     'serial': 'FGVULVTM19000XXX',
    #     'version': 'v6.2.0',
    #     'build': 866
    # }
    # '''
    # pass


## Interface
def test_system_interface(device):
    pprint(device.system.interface.list().json())
    # device.system.interface.create()
    # device.system.interface.get()
    # device.system.interface.get(name='wan1')
    # device.system.interface.delete()


## Config
### TODO consolidate slow tests on another file using betamax
# def test_system_config_restore(device):
#     filename = './var/test_system_config_01.conf'
#     r = device.system.config.restore(filename=filename)

#     expected_response = {
#         'http_method': 'POST',
#         'results': {'config_restored': True},
#         'vdom': 'root',
#         'path': 'system',
#         'name': 'config',
#         'action': 'restore',
#         'status': 'success',
#         'serial': 'FGVULVTM19000152',
#         'version': 'v6.2.1',
#         'build': 932
#     }

#     assert r.json() == expected_response

#   device.system.config.backup(filename='config.cfg')
#   device.system.config.backup(filename='config.cfg', vdom='vd01')

## ApiUser
def test_system_api_user(device):
    device.system.api_user.list()
    device.system.api_user.create()
    device.system.api_user.token
    device.system.api_user.get()
    device.system.api_user.delete()
    device.system.api_user.name = 'custom-api-admin'
    device.system.api_user.create(accprofile='prof_admin',
                        ipv4_trusthosts=['192.0.2.0/24'])
    device.system.api_user.delete()

## License - VM only
# def test_system_license_restore(device):
#     device.system.license.restore(filename='./var/licenses/license.lic')