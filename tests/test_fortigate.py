
import pytest
import os

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
    print(device.status)
    assert device.hostname == hostname

def test_login_failure():
    pass

def test_login_token():
    pass

def test_device_status(device):
    status = device.status

    expected_status = {
        'version': 'v6.2.0',
        'serial': 'FG81EP4Q17002XXX',
        'forticare': 'registered',
        'hostname': 'example_hostaname',
        'model': 'FortiGate-81E-POE',
        'uptime': 1000,
    }

    # check if keys exist
    assert status.keys() == expected_status.keys()


# System
def test_dns_database(device):
    device.system.dns_database.list()
    device.system.dns_database.name = 'exampleZone'
    device.system.dns_database.create()
    device.system.dns_database.add(ip='192.2.0.1', hostname='example')
    device.system.dns_database.get()
    device.system.dns_database.delete()

def test_system_firmware_list(device):
    r = device.system.firmware.list()
    assert r.status_code == 200

def test_system_firmware_upgrade_latest(device):
    # device.system.firmware.upgrade()
    pass

def test_system_firmware_upgrade_specific(device):
    # device.system.firmware.upgrade('v6.2.0')
    pass


# ApiUser
def test_system_api_user(device):
    device.system.api_user.list()
    device.system.api_user.create()
    device.system.api_user.token
    device.system.api_user.get()
    device.system.api_user.delete()

    device.system.api_user.name = 'custom-api-admin'
    device.system.api_user.create(accprofile='prof_admin',
                        ipv4_trusthost='192.0.2.0/24')