# nefila

Nefila is an elegant and simple Fortinet Security Fabric library for Python.

---

```python
Python 3.7.4 (default, Sep  7 2019, 18:27:02)
>>> import nefila
>>> device = nefila.FortiGate('192.0.2.1')
>>> device.open()
>>> device.status
```
<!-- 
## Features

- File-based authentication


## Requirements

Nefila requires Python 3.6 You can install `nefila` using pip:

    pip install nefila -->


<!-- ## Credentials

You can pass device credentials during requests or you can load them 
automatically using the following methods:

1. Setup your device credentials at ~/.nefila/credentials in the 
following format:
```
    [default]
    username = <your username>
    password = <your password>
```

2. Alternatively you can also use an access token:
```
    [default]
    token = <your access token>
``` -->


## License

This library is distributed under the 
[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/).
