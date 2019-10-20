
import pytest

import nefila
import nefila.utils

creds_filename = './var/test_login_credentials'
config_filename = './var/test_login_config'
TEST_PROFILE = 'TEST_LOGIN'

device_config = nefila.utils.get_config(profile=TEST_PROFILE, filename=config_filename)
credentials = nefila.utils.get_credentials(profile=TEST_PROFILE, filename=creds_filename)
hostname = device_config['hostname']


@pytest.fixture
def device():
    '''Device setup and teardown'''
    device = nefila.FortiGate(hostname)
    device.open(**credentials)
    yield device
    device.close()

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
    }

    # check if keys exist
    assert status.keys() == expected_status.keys()
