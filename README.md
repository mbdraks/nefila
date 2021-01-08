# nefila

<p align=center><img src="img/nefila.png" width="40%">

<p align=center>
Nefila is an elegant and simple Fortinet Security Fabric library for Python.

---

```python
Python 3.7.4 (default, Sep  7 2019, 18:27:02)
>>> import nefila
>>> device = nefila.FortiGate('192.0.2.1')
>>> device.open()
>>> device.status
{'version': 'v6.2.2', 'serial': 'FG81EP4Q17002000', 'forticare': 'registered', 'hostname': 'FW01', 'model': 'FortiGate-81E-POE', 'uptime': 22625}
```


## Features

- Environment variables based authentication
- Standard methods across all supported devices


## Supported Devices

- FortiOS v6.2
- FortiAnalyzer v6.2
- FortiManager v6.2
- FortiTester v4.0
- FortiSwitch v6.0


## Requirements and Installation

Nefila requires Python 3.7. You can install `nefila` using pip:

    pip install nefila


## Credentials

You can pass device credentials during requests or you can load them 
automatically using the following methods:

1. Setup your device credentials at ~/.nefila/credentials in the 
following format:
```INI
    [DEFAULT]
    username = <your username>
    password = <your password>
```

- You can also have device specific credentials:
```INI
    [192.0.2.1]
    username = <your username>
    password = <your password>
```

2. Alternatively you can also use an access token:
```INI
    [DEFAULT]
    token = <your access token>
```

3. Environment Variables
```bash
    export NEFILA_HOSTNAME=10.10.10.10
    export NEFILA_USERNAME=admin
    export NEFILA_PASSWORD=password
```



## License

This library is distributed under the 
[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/).
