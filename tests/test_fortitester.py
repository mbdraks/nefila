
import pytest
import os

import nefila
import nefila.utils

hostname = os.getenv('FORTITESTER_HOSTNAME', '192.168.0.40')
username = os.getenv('NEFILA_USERNAME', 'nefila-admin')
password = os.getenv('NEFILA_PASSWORD', 'nefila-password')

credentials = {'username': username, 'password': password}

@pytest.fixture
def device():
    '''Device setup and teardown'''
    device = nefila.FortiTester(hostname)
    device.open(**credentials)
    yield device
    device.close()


# Login
def test_login(device):
    print(device.status)
    assert device.hostname == hostname

def test_login_credentials_file():
    device = nefila.FortiTester(hostname)
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

# User
def test_user_list(device):
    device.user.list()

def test_user_info(device):
    device.user.username = 'admin'
    device.user.info()

def test_user_modify_password(device):
    device.user.username = 'admin'
    newpassword = password + '1'
    device.user.modify_password(oldpassword=password, newpassword=newpassword)
    device.user.modify_password(oldpassword=newpassword, newpassword=password)

# System
def test_upload_license(device):
    # device.system.license_upload(filename='license.lic')
    pass

def test_system_reboot(device):
    # device.system.reboot()
    pass

def test_network_import(device):
    # device.objects.network.import(filename=networkConfig.zip)
    pass

def test_network_list(device):
    # device.objects.network.list()
    pass
