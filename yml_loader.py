#!/usr/bin/env python3

import yaml
import click
from cy_config import *

def yml_router_setup(device_ip, params):
    setup_router(device_ip, params["model"], params["name"], params["ip"], params["inputs"], params["outputs"], params["red_tally"], params["green_tally"], params["shared"])
    for input in params["inputs_link"]:
        link_input(device_ip, params["name"], input["cam"], input["input"])

def yml_camera_setup(device_ip, params):
    setup_cam(device_ip, params["number"], params["name"], params["model"])
    if "ip" in params and "ip" in params["ip"]:
        add_cam_ip(device_ip, params["number"], params["ip"]["ip"], params["login"] if "login" in params else "", params["password"] if "password" in params else "")
    if "serial" in params:
        add_cam_serial(device_ip, params["number"], params["serial"]["port"])
    if "lens" in params:
        add_lens(device_ip, params["number"], params["lens"]["model"], params["lens"]["itf"], params["lens"]["options"] if "options" in params["lens"] else "")
    if "cc" in params:
        link_cc(device_ip, params["cc"], params["number"])

def yml_imported_setup(device_ip, params):
    import_cam(device_ip, params["from"], params["number"])
    if "cc" in params:
        link_cc(device_ip, params["cc"], params["number"])

callback_map = {
    "remi" : add_remi,
    "lan" : lambda device_ip, params : add_LAN_ip(device_ip, params["itf"], params["ip"], params["mask"]),
    "routers" : yml_router_setup,
    "bridge" : setup_autobridge,
    "cameras" : yml_camera_setup,
    "imported": yml_imported_setup,
    "cc": lambda device_ip, params : setup_cc(device_ip, params["model"], params["name"], params["ip"]),
    "tally_actions" : lambda device_ip, params : set_tally_action(device_ip, params["cam_number"], params["GPO"]),
    "bus": lambda device_ip, params : create_BUS(device_ip, params["type"], params["port"], params["bidirectional"] if "bidirectional" in params else "1"),
    "ip" : lambda device_ip, params : None
}

def get_ip(serial):
    try:
        batch, number = serial.split("-")[-2:]
        return f"10.192.{batch}.{number}"
    except ValueError:
        return serial
    except:
        return None

@click.command()
@click.option('-f', '--filename', required=True, type=str, help='YML file to load')
@click.option('-v', '--verbose', is_flag=True, show_default=True, default=False, help='Enable debug logs')
def main(filename, verbose):
    with open(filename, newline='') as file:
        data = yaml.safe_load_all(file)
        for block in data:
            for device in block:
                device_ip = get_ip(device)
                if not device_ip:
                    print(f"Invalid device {device}")
                    continue
                delete_remi(device_ip)
                delete_routers(device_ip)
                delete_ccs(device_ip)
                delete_cams(device_ip)
                delete_tally_actions(device_ip)
                delete_LAN_ip(device_ip)
                delete_BUS(device_ip)   
                for item in block[device]:
                    for key in item:
                        params = item[key]
                        try:
                            if not isinstance(params, list):
                                params = [params]
                            for param in params:
                                print(f"Calling @{key}@ fct with @{param}@")
                                fct = callback_map[key]
                                try:
                                    fct(device_ip, param)
                                except KeyError as e:
                                   print(f"Missing param {e} for {key} item")
                        except KeyError:
                            print(f"Unsupported command {key}")
if __name__ == "__main__":
    main()