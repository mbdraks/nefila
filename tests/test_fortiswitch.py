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


def test_device_switch_lldp_neighbors(device):
    device.switch.lldp.neighbors()

    # {'port17': [{'hostname': '5R5-FGT-3401E', 'port': 'port25'}],
    #  'port18': [{'hostname': '5R5-FGT-3401E', 'port': 'port26'}],
    #  'port29': [{'hostname': 'R3-FS-548D-FPOE', 'port': 'port53'}],
    #  'port31': [{'hostname': '5R5-FS-1048E', 'port': 'port51'}],
    #  'port32': [{'hostname': '5R5-FS-1048E', 'port': 'port52'}]}

def test_device_switch_lldp_neighbors_detail(device):
    device.switch.lldp.neighbors_detail()

    # {'port17': [{'parent_interface': '',
    #    'remote_chassis_id': 'e8:1c:ba:a0:0a:60',
    #    'remote_system_name': '5R5-FGT-3401E',
    #    'remote_port': 'port25',
    #    'remote_port_description': '',
    #    'remote_system_description': 'FortiGate-3401E v6.0.7,build0302,191112 (GA)',
    #    'remote_system_capab': 'BR',
    #    'remote_system_enable_capab': 'R'}],
    #  'port18': [{'parent_interface': '',
    #    'remote_chassis_id': 'e8:1c:ba:a0:0a:61',
    #    'remote_system_name': '5R5-FGT-3401E',
    #    'remote_port': 'port26',
    #    'remote_port_description': '',
    #    'remote_system_description': 'FortiGate-3401E v6.0.7,build0302,191112 (GA)',
    #    'remote_system_capab': 'BR',
    #    'remote_system_enable_capab': 'R'}],
    #  'port29': [{'parent_interface': '',
    #    'remote_chassis_id': '08:5b:0e:f0:98:e4',
    #    'remote_system_name': 'R3-FS-548D-FPOE',
    #    'remote_port': 'port53',
    #    'remote_port_description': 'To 5R5-FS-3032D Port29',
    #    'remote_system_description': 'FortiSwitch-548D-FPOE v6.0.2,build0046,181102 (GA)',
    #    'remote_system_capab': 'BR',
    #    'remote_system_enable_capab': 'BR'}],
    #  'port31': [{'parent_interface': '',
    #    'remote_chassis_id': 'e8:1c:ba:96:ac:94',
    #    'remote_system_name': '5R5-FS-1048E',
    #    'remote_port': 'port51',
    #    'remote_port_description': 'port51',
    #    'remote_system_description': 'FortiSwitch-1048E v6.0.4,build0064,190516 (GA)',
    #    'remote_system_capab': 'BR',
    #    'remote_system_enable_capab': 'BR'}],
    #  'port32': [{'parent_interface': '',
    #    'remote_chassis_id': 'e8:1c:ba:96:ac:94',
    #    'remote_system_name': '5R5-FS-1048E',
    #    'remote_port': 'port52',
    #    'remote_port_description': 'port52',
    #    'remote_system_description': 'FortiSwitch-1048E v6.0.4,build0064,190516 (GA)',
    #    'remote_system_capab': 'BR',
    #    'remote_system_enable_capab': 'BR'}]}

def test_device_switch_lldp_neighbors_full(device):
    device.switch.lldp.neighbors_full()
