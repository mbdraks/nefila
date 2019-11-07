
import pytest

import nefila.utils

creds_filename = './var/credentials.test'
config_filename = './var/config.test'

TEST_PROFILE = '192.0.2.200:4000'

def test_set_credentials_default():
    nefila.utils.set_credentials(filename=creds_filename)

def test_set_credentials_custom():
    parameters = {
        'profile': TEST_PROFILE,
        'filename': creds_filename, 
        'username': 'test-admin', 
        'password': 'test-password', 
        'token': 'test-token',
    }
    nefila.utils.set_credentials(**parameters)

# def test_get_credential_default_file():
#     nefila.utils.get_credentials(filename=creds_filename)

def test_get_credential_no_file():
    nefila.utils.get_credentials(filename='')

# def test_get_credential_custom_profile():
#     parameters = {
#         'filename': creds_filename,
#         'profile': TEST_PROFILE,
#     }
#     nefila.utils.get_credentials(**parameters)

def test_set_config_default():
    nefila.utils.set_config(filename=config_filename)

def test_set_config_custom():
    parameters = {
        'filename': config_filename,
        'profile': TEST_PROFILE,
        'hostname': TEST_PROFILE,
    }
    nefila.utils.set_config(**parameters)

def test_get_config_default_file():
    nefila.utils.get_config(filename=config_filename)

def test_get_config_no_file():
    nefila.utils.get_config(filename='')

def test_get_config_custom_profile():
    parameters = {
        'filename': config_filename,
        'profile': TEST_PROFILE,
    }
    nefila.utils.get_config(**parameters)