
import os
import configparser

creds_dir = os.path.expanduser("~") + "/.nefila"
creds_filename = creds_dir + "/credentials"

def get_credentials(profile='default', creds_filename=creds_filename):
    config = configparser.ConfigParser()
    config.read(creds_filename)

    credentials = {
        'username': config.get(profile, 'username'),
        'password': config.get(profile, 'password'),
    }

    print(credentials)
    return credentials