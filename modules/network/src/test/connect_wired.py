#! /usr/bin/env python

from nmlib.nm_remote_settings import NMRemoteSettings
from nmlib.nmclient import NMClient

nmclient = NMClient()

conn_path = NMRemoteSettings().new_wired_connection()
device_path = nmclient.get_wired_device()
spefic_path = "/"

nmclient.activate_connection(conn_path, device_path, spefic_path)


conn_path = NMRemoteSettings().new_wired_connection()
device_path = nmclient.get_wired_device()
spefic_path = "/"

nmclient.activate_connection(conn_path, device_path, spefic_path)

