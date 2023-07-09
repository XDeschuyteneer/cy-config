#!/usr/bin/env python3

from cy_config import *

if __name__ == "__main__":
    rcp_ip = "10.192.40.142"
    rio_ip = "10.192.50.22"
    delete_cams(rio_ip)
    delete_cams(rcp_ip)
    setup_remi(rio_ip, "xavier")
    setup_remi(rcp_ip, "xavier")
    setup_cam(rio_ip, "1", "cam", "SonyFX9", "10.192.1.1", "admin", "AAAaaa111", "sony", "RIO-50-22:1", "")
    setup_cam(rio_ip, "2", "cam", "SonyFX9", "10.192.1.2", "admin", "AAAaaa111", "tilta", "RIO-50-22:2", "3:I:2.8:22")
    setup_cam(rcp_ip, "3", "cam", "", "", "", "", "", "", "")
    import_cam(rcp_ip, "cy-rio-50-22", "1")
    import_cam(rcp_ip, "cy-rio-50-22", "2")
    delete_routers(rcp_ip)
    setup_router(rcp_ip, "AtemSwitcher", "ATEM1", "1.2.3.4", "1-11", "1-5,Prv1,Prg1", "AUTO", "AUTO", "1")
    link_input(rcp_ip, "ATEM1", 1, 1)
    link_input(rcp_ip, "ATEM1", 2, 2)
    link_output(rcp_ip, "ATEM1", "RCP", "Aux2")
    delete_ccs(rcp_ip)
    setup_cc(rcp_ip, "Boxio", "CC1", "1.2.3.4")
    setup_cc(rcp_ip, "Boxio", "CC2", "1.2.3.4")
    link_cc(rcp_ip, "CC1:1", 3)
    link_cc(rcp_ip, "CC1:2", 2)
    link_cc(rcp_ip, "CC2:1", 1)
    delete_LAN_ip(rcp_ip)
    setup_autobridge(rcp_ip, "0")
    add_LAN_ip(rcp_ip, "LAN1", "10.193.1.1", "255.255.0.0")
    delete_tally_actions(rio_ip)
    set_tally_action(rio_ip, 1, "1:PWR")
    set_tally_action(rio_ip, 2, "2:PWR")