
import pytest
import os

import nefila
import nefila.utils

hostname = os.getenv('FMG_HOSTNAME', '192.168.0.31')
username = os.getenv('NEFILA_USERNAME', 'nefila-admin')
password = os.getenv('NEFILA_PASSWORD', 'nefila-password')
credentials = {'username': username, 'password': password}


@pytest.fixture
def manager():
    '''Device setup and teardown'''
    manager = nefila.FortiManager(hostname)
    manager.open(**credentials)
    yield manager
    manager.close()


# Login
def test_login_live(manager):
    print(manager.status)
    assert manager.hostname == hostname

def test_login_credentials_file():
    manager = nefila.FortiManager(hostname)
    manager.open()
    assert manager.hostname == hostname

def test_device_status(manager):
    status = manager.status

    expected_status = {
        'serial': '',
        'version': '',
        'forticare': '',
        'hostname': '',
        'model': ''
    }

    # check if keys exist
    assert status.keys() == expected_status.keys()

def test_basic_status(manager):
    manager.basic_status()

# Devices
## List
def test_devices_list(manager):
    # manager.devices.device_list()
    manager.devices.list()

# Proxy
def test_devices_proxy_no_arguments(manager):
    # Obtain first managed device
    r = manager.devices.list()
    managed_device_name = r.json()['result'][0]['data'][0]['name']
    
    manager.devices.proxy(device=managed_device_name)
