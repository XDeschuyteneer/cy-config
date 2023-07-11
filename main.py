#!/usr/bin/env python3

from cy_config import *

def main():
    rcp_ip = "10.192.40.142"
    rio_ip = "10.192.50.22"
    delete_cams(rio_ip)
    delete_cams(rcp_ip)
    setup_remi(rio_ip, "xavier")
    setup_remi(rcp_ip, "xavier")
    delete_ccs(rcp_ip)
    setup_cc(rcp_ip, "Boxio", "CC1", "1.2.3.4")
    setup_cc(rcp_ip, "Boxio", "CC2", "1.2.3.4")
    setup_cam(rio_ip, "1", "cam", "SonyFX9")
    add_cam_ip(rio_ip, "1", "10.192.1.1", "admin", "AAAaaa111")
    add_lens(rio_ip, "1", "sony", "RIO-50-22:1")
    setup_cam(rio_ip, "2", "cam", "SonyFX9")
    add_cam_ip(rio_ip, "2", "10.192.1.2", "admin", "AAAaaa111")
    add_lens(rio_ip, "2", "tilta", "RIO-50-22:2", "3:I:2.8:22")
    setup_cam(rcp_ip, "3", "cam", "")
    import_cam(rcp_ip, "cy-rio-50-22", "1")
    link_cc(rcp_ip, "CC1:1", 1)
    import_cam(rcp_ip, "cy-rio-50-22", "2")
    link_cc(rcp_ip, "CC1:2", 2)
    setup_cam(rio_ip, "2", "cam", "")
    link_cc(rcp_ip, "CC1:2", 2)
    delete_routers(rcp_ip)
    setup_router(rcp_ip, "AtemSwitcher", "ATEM1", "1.2.3.4", "1-11", "1-5,Prv1,Prg1", "AUTO", "AUTO", "1")
    link_input(rcp_ip, "ATEM1", 1, 1)
    link_input(rcp_ip, "ATEM1", 2, 2)
    link_output(rcp_ip, "ATEM1", "RCP", "Aux2")
    delete_LAN_ip(rcp_ip)
    setup_autobridge(rcp_ip, "0")
    add_LAN_ip(rcp_ip, "LAN1", "10.193.1.1", "255.255.0.0")
    delete_tally_actions(rio_ip)
    set_tally_action(rio_ip, 1, "1:PWR")
    set_tally_action(rio_ip, 2, "2:PWR")
    create_BUS("10.192.40.142", "bm", "CI0-31-71:3")

if __name__ == "__main__":
    # main()
    # list_cameras_models("10.192.40.142")
    rio_ip = "10.192.50.22"
    delete_cams(rio_ip)
    delete_BUS(rio_ip)
    create_BUS(rio_ip, "atom", "RIO-50-22:1", "0")
    setup_cam(rio_ip, 1, "cam", "AtomMiniZoom")
    add_cam_serial(rio_ip, 1, "RIO-50-22:1:AtomBus:1")
