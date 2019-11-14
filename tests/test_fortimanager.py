
import pytest
import os

import nefila
import nefila.utils

hostname = os.getenv('FMG_HOSTNAME', '192.168.0.20')
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

def test_login_live(manager):
    print(manager.status)
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
