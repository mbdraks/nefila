
import os
import configparser

nefila_dir = os.path.expanduser("~") + "/.nefila"
creds_filename = nefila_dir + "/credentials"
config_filename = nefila_dir + "/config"


profile = 'DEFAULT'
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = ''
DEFAULT_TOKEN = ''
DEFAULT_HOSTNAME = '192.168.1.99'

def set_credentials(profile=profile,
                    filename=creds_filename,
                    username=DEFAULT_USERNAME,
                    password=DEFAULT_PASSWORD,
                    token=None):
    '''Create credential file, will overwrite if file already exist'''
    config = configparser.ConfigParser()

    # Check if file/profile already exist
    if os.path.exists(filename):
        config.read(filename)

    if not profile in config:
        # Token or Password based
        if token:
            config[profile] = {
                'username': username,
                'token': token,
            }
        else:
            config[profile] = {
                'username': username,
                'password': password,
            }

        os.makedirs(nefila_dir, exist_ok=True)

        with open(filename, 'w') as configfile:
            config.write(configfile)
        return 'Credentials file set'
    else:
        return 'Profile already exist'

def get_credentials(profile=profile, filename=creds_filename):
    '''Obtain credentials from file'''
    # Assign default credentials if file does not exist
    config = configparser.ConfigParser()
    credentials = {}
    if os.path.exists(filename):
        config.read(filename)
        # If file exist, check if profile exist
        if profile in config:
            credentials = {
                'username': config[profile].get('username', DEFAULT_USERNAME),
                'password': config[profile].get('password', DEFAULT_PASSWORD),
                'token': config[profile].get('token', DEFAULT_TOKEN),
            }
        else:
            credentials = {
                'username': DEFAULT_USERNAME, 
                'password': DEFAULT_PASSWORD, 
                'token': DEFAULT_TOKEN,
            }
    else:
        credentials = {
            'username': DEFAULT_USERNAME, 
            'password': DEFAULT_PASSWORD, 
            'token': DEFAULT_TOKEN,
        }

    return credentials


def set_config(profile=profile, filename=config_filename, hostname=DEFAULT_HOSTNAME):
    '''Create config file'''
    config = configparser.ConfigParser()
    config[profile] = {
        'hostname': hostname,
    }

    os.makedirs(nefila_dir, exist_ok=True)

    with open(filename, 'w') as configfile:
        config.write(configfile)
    return 'Config file set'


def get_config(profile=profile, filename=config_filename):
    '''Obtain config from file'''
    config = configparser.ConfigParser()
    if not os.path.exists(filename):
        nefilaconfig = {'hostname': '192.168.1.99'}
    else:
        config.read(filename)
        
    # If file exist, check if profile exist
    if profile in config:
        nefilaconfig = {
            'hostname': config[profile].get('hostname', DEFAULT_HOSTNAME),
        }

    return nefilaconfig
