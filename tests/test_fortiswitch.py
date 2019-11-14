
import pytest
import os

import nefila
import nefila.utils

hostname = os.getenv('FORTISWITCH_HOSTNAME', '192.168.0.40')
username = os.getenv('NEFILA_USERNAME', 'nefila-admin')
password = os.getenv('NEFILA_PASSWORD', 'nefila-password')

credentials = {'username': username, 'password': password}

@pytest.fixture
def device():
    '''Device setup and teardown'''
    device = nefila.FortiSwitch(hostname)
    device.open(**credentials)
    yield device
    device.close()


# Login
def test_login(device):
    print(device.status)
    assert device.hostname == hostname

def test_login_credentials_file():
    device = nefila.FortiSwitch(hostname)
    device.open()
    assert device.hostname == hostname

def test_device_status(device):
    status = device.status

    expected_status = {
        'version': '',
        'serial': '',
        'hostname': '',
        'model': '',
        'uptime': '',
        'forticare': '',
    }

    # check if keys exist
    assert status.keys() == expected_status.keys()

def test_device_basic_status(device):
    device.basic_status()
