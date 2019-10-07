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


def test_dns_database(device):
    device.system.dns_database.list()
    device.system.dns_database.name = 'exampleZone'
    device.system.dns_database.create()
    device.system.dns_database.add(ip='192.2.0.1', hostname='example')
    device.system.dns_database.get().json()
    device.system.dns_database.delete()
