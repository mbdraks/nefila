import pytest
import os

import urllib3

urllib3.disable_warnings()

import nefila
import nefila.utils

hostname = os.getenv("NEFILA_HOSTNAME_FTS", "localhost:1080")
username = os.getenv("NEFILA_USERNAME", "admin")
password = os.getenv("NEFILA_PASSWORD", "password")

credentials = {"username": username, "password": password}

# Return Code OK
t = {}
t["ErrorCode"] = 0
t["Data"] = {}


@pytest.fixture
def device():
    """Device setup and teardown"""
    device = nefila.FortiTester(hostname)
    device.open(**credentials)
    yield device
    device.close()


def test_login(device):
    assert device.host == hostname


def test_login_with_env(device):
    device.close()

    os.environ["NEFILA_USERNAME"] = username
    os.environ["NEFILA_PASSWORD"] = password

    r = device.open()
    assert r["ErrorCode"] == t["ErrorCode"]

    device.close()


def test_get_not_logged(device):
    device.close()
    r = device.system.status.get()
    assert r["ErrorCode"] != t["ErrorCode"]


def test_device_status(device):
    r = device.system.status.get()

    d = {}
    d["ErrorCode"] = 0
    d["Data"] = {}

    # check if keys exist and rc eq 0
    assert r.keys() == d.keys()
    assert d["ErrorCode"] == r["ErrorCode"]


def test_device_status_property(device):
    r = device.status

    d = {}
    d["ErrorCode"] = 0
    d["Data"] = {}

    assert r.keys() == d.keys()
    assert d["ErrorCode"] == r["ErrorCode"]


# User
def test_user_get(device):
    r = device.user.get()

    t = {}
    t["payload"] = None
    t["total"] = None

    assert t.keys() == r.keys()


def test_user_create_delete(device):
    d = {
        "name": "newuser",
        "password": "newpassword",
        "cfmPsw": "newpassword",
        "role": "admin",
    }
    r = device.user.create(d)

    assert t["ErrorCode"] == r["ErrorCode"]

    uid = r["Data"]
    d = {"ids": [uid]}
    r = device.user.delete(**d)

    assert t["ErrorCode"] == r["ErrorCode"]


# network
def test_objectConfig_network_get(device):
    r = device.objectConfig.network.get()

    t = {}
    t["payload"] = None
    t["total"] = None

    assert t.keys() == r.keys()


def test_objectConfig_network_create_delete(device):
    nn_config = {
        "DUTRole": "Gateway",
        "IPVersion": "v4",
        "ClientConfig": {
            "SlaveHost": [
                {
                    "Host": "localhost",
                    "Ports": [
                        {
                            "Subnets": [
                                {"IpAddrRange": "17.1.2.2-17.1.2.201", "Netmask": "16"},
                                {"IpAddrRange": "17.2.2.2-17.2.2.201", "Netmask": "16"},
                            ],
                            "Interface": "port1",
                        },
                        {
                            "Subnets": [
                                {"IpAddrRange": "18.1.2.2-18.1.2.201", "Netmask": "16"},
                                {"IpAddrRange": "18.2.2.2-18.2.2.201", "Netmask": "16"},
                            ],
                            "Interface": "port2",
                        },
                    ],
                }
            ]
        },
        "ServerConfig": {
            "SlaveHost": [
                {
                    "Host": "localhost",
                    "Ports": [
                        {
                            "Subnets": [
                                {"IpAddrRange": "17.1.1.100", "Netmask": "16"},
                                {"IpAddrRange": "17.2.1.100", "Netmask": "16"},
                            ],
                            "Interface": "port3",
                        },
                        {
                            "Subnets": [
                                {"IpAddrRange": "18.1.1.100", "Netmask": "16"},
                                {"IpAddrRange": "18.2.1.100", "Netmask": "16"},
                            ],
                            "Interface": "port4",
                        },
                    ],
                }
            ]
        },
        "WorkMode": "Standalone",
        "Name": "NetworkConfig_NEFILA_TEST",
        "TestMode": "TP",
        "User": "admin",
        "Networks": {},
    }

    r = device.objectConfig.network.create(**nn_config)
    assert t["ErrorCode"] == r["ErrorCode"]

    uid = r["Data"]
    d = {"ids": [uid]}
    r = device.objectConfig.network.delete(d)

    assert t["ErrorCode"] == r["ErrorCode"]


def test_objectConfig_network_create_simple_tp(device):
    # fmt: off
    nn_config = {
        "Name": "nn_simple_tp_nefila",
        "TestMode": "TP",
        "DUTRole": "Gateway",
        "ClientConfig": {
            "SlaveHost": [{
                "Ports": [{
                    "Subnets": [{"IpAddrRange": "17.1.2.2","Netmask": "16"}],
                    "Interface": "port1"
                }]
            }]
        },
        "ServerConfig": {
            "SlaveHost": [{
                "Ports": [{
                    "Subnets": [{"IpAddrRange": "17.1.1.100","Netmask": "16"}],
                    "Interface": "port2"
                }]
            }]
        },
    }
    # fmt: on

    r = device.objectConfig.network.create(nn_config)
    assert t["ErrorCode"] == r["ErrorCode"]
    uid = r["Data"]
    d = {"ids": [uid]}
    r = device.objectConfig.network.delete(d)
    assert t["ErrorCode"] == r["ErrorCode"]


def test_objectConfig_network_create_simple_vpnssl(device):
    # fmt: off
    nn_config = {
        "Name": "nn_simple_vpnssl_nefila",
        "TestMode": "NAT",
        "DUTRole": "Gateway",
        "UseVpn": True,
        "ClientConfig": {
            "SlaveHost": [{
                "Ports": [{
                        "Subnets": [{
                                "IpAddrRange": "17.1.2.2-17.1.3.245",
                                "Netmask": "16",
                                "Route": {
                                    "Gateway": "17.1.1.1",
                                    "PeerNetwork": "19.1.0.0/16",
                                    "VpnGateway": "17.129.1.1"
                                }
                            },
                        ],
                        "Interface": "port1"
                    },
                ]
            }]
        },
        "ServerConfig": {
            "SlaveHost": [{
                "Ports": [{
                        "Subnets": [{
                                "IpAddrRange": "19.1.1.100",
                                "Netmask": "16",
                                "Route": {
                                    "Gateway": "19.1.1.1",
                                    "PeerNetwork": "17.1.0.0/16"
                                }
                            },
                        ],
                        "Interface": "port3"
                    },
                ]
            }]
        },
    }
    # fmt: on

    r = device.objectConfig.network.create(nn_config)
    assert t["ErrorCode"] == r["ErrorCode"]
    uid = r["Data"]
    d = {"ids": [uid]}
    r = device.objectConfig.network.delete(d)
    assert t["ErrorCode"] == r["ErrorCode"]


def test_objectConfig_network_create_nn_v4_gw_nat_vr(device):
    # fmt: off
    nn_config = {
        "Name": "nn_v4_gw_nat_vr",
        "TestMode": "NAT",
        "IPVersion": "v4",
        "DUTRole": "Gateway",
        "ClientConfig": {
            "SlaveHost": [{
                "Ports": [{
                    "Subnets": [{
                        "IpAddrRange": "8.1.1.1-8.1.1.254",
                        "Netmask": "24",
                        "Route": {
                            "Gateway": "172.17.81.254",
                            "PeerNetwork": "9.2.1.1/24"
                        }
                    }],
                    "Interface": "port1",
                    "VirtualRouterIP": "172.17.81.1",
                    "VirtualRouterNetmask": "24"
                }]
            }]
        },
        "ServerConfig": {
            "SlaveHost": [{
                "Ports": [{
                    "Subnets": [{
                        "IpAddrRange": "9.2.1.1-9.2.1.254",
                        "Netmask": "24",
                        "Route": {
                            "Gateway": "172.17.91.254",
                            "PeerNetwork": "8.1.1.1/24"
                        }
                    }],
                    "Interface": "port2",
                    "VirtualRouterIP": "172.17.91.1",
                    "VirtualRouterNetmask": "24"
                }]
            }]
        },
    }
    # fmt: on

    r = device.objectConfig.network.create(nn_config)
    assert t["ErrorCode"] == r["ErrorCode"]
    uid = r["Data"]
    d = {"ids": [uid]}
    r = device.objectConfig.network.delete(d)
    assert t["ErrorCode"] == r["ErrorCode"]


def test_objectConfig_network_find(device):
    r = device.objectConfig.network.get()

    for i in r["payload"]:
        uid = i["_id"]
        d = {"ids": [uid]}
        r = device.objectConfig.network.find(d)
        assert t.keys() == r.keys()
        assert t["ErrorCode"] == r["ErrorCode"]
