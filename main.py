#!/usr/bin/env python3

from cy_config import *

if __name__ == "__main__":
    delete_cams("10.192.50.22")
    delete_cams("10.192.40.142")
    setup_remi("10.192.50.22", "xavier")
    setup_remi("10.192.40.142", "xavier")
    setup_cam("10.192.50.22", "1", "cam", "SonyFX9", "10.192.1.1", "admin", "AAAaaa111", "sony", "RIO-50-22:1", "")
    setup_cam("10.192.50.22", "2", "cam", "SonyFX9", "10.192.1.2", "admin", "AAAaaa111", "tilta", "RIO-50-22:2", "3:I:2.8:22")
    setup_cam("10.192.40.142", "3", "cam", "", "", "", "", "", "", "")
    import_cam("10.192.40.142", "cy-rio-50-22", "1")
    import_cam("10.192.40.142", "cy-rio-50-22", "2")
    delete_routers("10.192.40.142")
    setup_router("10.192.40.142", "AtemSwitcher", "ATEM1", "1.2.3.4", "1-11", "1-5,Prv1,Prg1", "AUTO", "AUTO", "1")
    link_input("10.192.40.142", "ATEM1", 1, 1)
    link_input("10.192.40.142", "ATEM1", 2, 2)
    link_output("10.192.40.142", "ATEM1", "RCP", "Aux2")
    delete_ccs("10.192.40.142")
    setup_cc("10.192.40.142", "Boxio", "CC1", "1.2.3.4")
    setup_cc("10.192.40.142", "Boxio", "CC2", "1.2.3.4")
    link_cc("10.192.40.142", "CC1:1", 3)
    link_cc("10.192.40.142", "CC1:2", 2)
    link_cc("10.192.40.142", "CC2:1", 1)
    delete_LAN_ip("10.192.40.142")
    setup_autobridge("10.192.40.142", "0")
    add_LAN_ip("10.192.40.142", "LAN1", "10.193.1.1", "255.255.0.0")