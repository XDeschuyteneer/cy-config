#!/usr/bin/env python3

import yaml
import click
import cy_config
import logging
import sys

logger = logging.getLogger(__name__)


def yml_router_setup(device_ip, params):
    if params["name"][0] == "@":
        # shared router
        cy_config.update_router_tally(device_ip, params["name"], params["red_tally"], params["green_tally"])
    else:
        cy_config.setup_router(device_ip, params["model"], params["name"], params["ip"], params["inputs"], params["outputs"], params["red_tally"], params["green_tally"], params["shared"])
    for input in params["inputs_link"]:
        cy_config.link_input(device_ip, params["name"], input["cam"], input["input"])
    for output in params["outputs_link"]:
        cy_config.link_output(device_ip, params["name"], output["monitor"], output["output"])

def yml_camera_setup(device_ip, params):
    cy_config.setup_cam(device_ip, params["number"], params["name"], params["model"])
    if "ip" in params and "ip" in params["ip"]:
        cy_config.add_cam_ip(device_ip, params["number"], params["ip"]["ip"], params["login"] if "login" in params else "", params["password"] if "password" in params else "")
    if "serial" in params:
        cy_config.add_cam_serial(device_ip, params["number"], params["serial"]["port"])
    if "lens" in params:
        cy_config.add_lens(device_ip, params["number"], params["lens"]["model"], params["lens"]["itf"], params["lens"]["options"] if "options" in params["lens"] else "")
    if "cc" in params:
        cy_config.link_cc(device_ip, params["cc"], params["number"])

def yml_imported_setup(device_ip, params):
    cy_config.import_cam(device_ip, params["from"], params["number"])
    if "cc" in params:
        cy_config.link_cc(device_ip, params["cc"], params["number"])

callback_map = {
    "remi" : cy_config.add_remi,
    "lan" : lambda device_ip, params : cy_config.add_LAN_ip(device_ip, params["itf"], params["ip"], params["mask"]),
    "routers" : yml_router_setup,
    "bridge" : cy_config.setup_autobridge,
    "cameras" : yml_camera_setup,
    "imported": yml_imported_setup,
    "cc": lambda device_ip, params : cy_config.setup_cc(device_ip, params["model"], params["name"], params["ip"]),
    "tally_actions" : lambda device_ip, params : cy_config.set_tally_action(device_ip, params["cam_number"], params["GPO"]),
    "bus": lambda device_ip, params : cy_config.create_BUS(device_ip, params["type"], params["port"], params["bidirectional"] if "bidirectional" in params else "1"),
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
@click.option('-v', '--verbosity', required=False, show_default=True, type=str, default="WARNING", help='Enable debug logs')
def main(filename, verbosity):
    print(f"Loading {filename}")
    print(f"Verbose mode: {verbosity}")
    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR
    }
    if verbosity not in log_levels:
        logging.error(f"Invalid verbosity level {verbosity}")
    logging.basicConfig(stream=sys.stdout, level=log_levels[verbosity])
    try:
        with open(filename, newline='') as file:
            data = yaml.safe_load_all(file)
            for block in data:
                for device in block:
                    device_ip = get_ip(device)
                    if not device_ip:
                        logger.error(f"Invalid device {device}")
                        continue
                    cy_config.delete_remi(device_ip)
                    cy_config.delete_routers(device_ip)
                    cy_config.delete_ccs(device_ip)
                    cy_config.delete_cams(device_ip)
                    cy_config.delete_tally_actions(device_ip)
                    cy_config.delete_LAN_ip(device_ip)
                    cy_config.delete_BUS(device_ip)
                    for item in block[device]:
                        for key in item:
                            params = item[key]
                            try:
                                if not isinstance(params, list):
                                    params = [params]
                                for param in params:
                                    logger.info(f"Calling @{key}@ fct with @{param}@")
                                    fct = callback_map[key]
                                    try:
                                        fct(device_ip, param)
                                    except KeyError as e:
                                        logger.info(f"Missing param {e} for {key} item")
                            except KeyError:
                                logger.error(f"Unsupported command {key}")
    except FileNotFoundError:
        logger.error(f"File {filename} not found")
    except yaml.scanner.ScannerError:
        logger.error(f"Invalid YML file {filename}")
if __name__ == "__main__":
    main()