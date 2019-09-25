
import nefila
import pytest

hostname = 'fortigate.fortidemo.com'
username = 'demo'
password = 'demo'

def test_login():
    device = nefila.FortiGate(hostname)
    device.open(username=username, password=password)
    device.close
    assert device.hostname == hostname

def test_url_prefix():
    device = nefila.FortiGate(hostname)
    device.open(username=username, password=password)
    device.close
    assert device.url_prefix == f'https://{hostname}'

def test_device_status():
    device = nefila.FortiGate(hostname)
    device.open(username=username, password=password)
    status = device.status
    device.close

    expected_status = {
        'version': 'v6.2.1',
        'serial': 'FGT2KE3917900165',
        'forticare': 'registered',
        'hostname': 'NGFW_PRI',
        'model': 'FortiGate-2000E',
    }

    assert status == expected_status
