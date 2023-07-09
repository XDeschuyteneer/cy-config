import websocket
import json

def check_answer(ws):
    change = None
    while True:
        change = json.loads(ws.recv())
        if change["type"] == "action_reply":
            break
        elif change["type"] == "option_reply":
            break
        else:
            print("unsupported type", change["type"], change)
    print(change)
    if not change["payload"]:
        return None
    else:
        return change["payload"]

def do_action(ws, action, param):
    data = json.dumps({
        "type" : "action_request",
        "request" : {
            action : param
        }
    })
    print(data)
    ws.send(data)
    cam_id = check_answer(ws)[1]
    return cam_id

def get_option(ws, item_id, option):
    data = json.dumps({
        "type" : "option_request",
        "request" : [item_id, option]
    })
    print(data)
    ws.send(data)
    response = check_answer(ws)
    return response   

def delete_cams(ip):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())
        for cam_id in config["payload"]["Camera"]:
            do_action(ws, "delete", [cam_id])
    finally:
        ws.close()

def change(ws, cam_id, key, value):
    return do_action(ws, "update", {"key" : cam_id, "changes" : { key : value }})

def connect(ws, A_id, B_id):
    return do_action(ws, "connect", [A_id, B_id])

def setup_lens(ws, cam_id, lens_type, lens_port, lens_option=""):
    try:
        change(ws, f"{cam_id}_l", "model", lens_type)
        lens_interfaces = get_option(ws, cam_id, "LensInterface")
        CI0_serial = lens_port.split(":")[0]
        CI0_port = lens_port.split(":")[1]
        for itf in lens_interfaces:
            if itf[0]["device"] == CI0_serial and itf[0]["port"] == CI0_port:
                print(itf[1][0])
                port_id = itf[1][0]["connect"][0]
                connect(ws, port_id, f"{cam_id}_l")
                change(ws, f"{cam_id}_l", "params", lens_option)
    except:
        print("no lens setup")

def setup_remi(ip, tags):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())
        remi_id = next(iter(config["payload"]["Remi"]))
        change(ws, remi_id, "tags", tags)
    finally:
        ws.close()

    
def setup_cam(ip, cam_number, cam_name, cam_model, cam_ip, cam_login, cam_passwd, lens_type, lens_port, lens_option):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())
        # create new camera
        cam_id = do_action(ws, "new", ["CyElement.Camera"])
        change(ws, cam_id, "number", cam_number)
        change(ws, cam_id, "name", cam_name)
        change(ws, cam_id, "model", cam_model)

        # camhead
        ip_id = get_option(ws, cam_id, "IP")["key"]
        change(ws, ip_id, "ip", cam_ip)
        change(ws, ip_id, "login", cam_login)
        change(ws, ip_id, "password", cam_passwd)

        # lens
        setup_lens(ws, cam_id, lens_type, lens_port, lens_option)

        return cam_id

    except KeyboardInterrupt as e:
        print("CTRL+C pressed")
    except Exception as e:
        print(e, "| line", e.__traceback__.tb_lineno)
    finally:
        print("closing socket")
        ws.close()

def import_cam(ip, device, cam_number):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())
        imported_cam_id = None
        for key in config["payload"]['Remi']:
            if config["payload"]['Remi'][key]:
                item = config["payload"]['Remi'][key]
                if "Active" in item and item["Active"]:
                    for cnx_id in item["Connections"]:
                        if item["Connections"][cnx_id]["name"] == device:
                            for cam in item["Connections"][cnx_id]['cameras']:
                                c_number = cam[0].split(" ")[0]
                                if c_number == str(cam_number):
                                    imported_cam_id = cam[3]
                                    break
        if imported_cam_id:
            change(ws, imported_cam_id, "auto_camera", "1")
    finally:
        print("closing socket")
        ws.close()

def delete_routers(ip):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())
        for router_id in config["payload"]["Router"]:
            do_action(ws, "delete", [router_id])
    finally:
        ws.close()

def setup_router(ip, model, name, router_ip, input_range, output_range, red_tally, green_tally, shared="1"):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        router_id = do_action(ws, "new", [f"CyElement.{model}"])
        change(ws, router_id, "name", name)
        change(ws, router_id, "ip", router_ip)
        change(ws, router_id, "num_inputs", input_range)
        change(ws, router_id, "num_outputs", output_range)
        change(ws, router_id, "tally_red", red_tally)
        change(ws, router_id, "tally_green", green_tally)
        change(ws, router_id, "shared", shared)

        return router_id
    finally:
        print("closing socket")
        ws.close()     


def get_router_id(ip, router_name):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())
        for router_id in config["payload"]["Router"]:
            if config["payload"]["Router"][router_id]["Name"] == router_name:
                return router_id
    finally:
        ws.close()   

def get_cam_id(ip, cam_number):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())
        for cam_id in config["payload"]["Camera"]:
            if config["payload"]["Camera"][cam_id]["Number"] == str(cam_number):
                return cam_id
    finally:
        ws.close()

def get_input_id(ip, router_name, input_number):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())
        router_id = get_router_id(ip, router_name)
        if router_id:
            for input_id in config["payload"]["Router"][router_id]["Inputs"]:
                pass
                # print(config["payload"]["Router"][router_id])
                # if config["payload"]["Router"][router_id]["Inputs"][input_id]["Position"] == str(input_number):
                #     return input_id
    finally:
        ws.close()


def link_input(ip, router_name, cam_number, input_number):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())
        router_id = get_router_id(ip, router_name)
        router_inputs = get_option(ws, router_id, "Inputs")
        for cam_entry in router_inputs[str(input_number)]:
            if cam_entry[0]:
                if cam_entry[0].split(" ")[0] == str(cam_number):
                    for action in cam_entry[1]:
                        for action_name in action:
                            do_action(ws, action_name, action[action_name])
    finally:
        print("closing socket")
        ws.close()

def cleanup_router_input(ip, router_name):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())
        router_id = get_router_id(ip, router_name)
        router_inputs = get_option(ws, router_id, "Inputs")
        for input_number in router_inputs:
            for cam_entry in router_inputs[input_number]:
                for action in cam_entry[1]:
                    if not cam_entry[0] and 'delete' in action:
                        for action_name in action:
                            do_action(ws, action_name, action[action_name])
    finally:
        print("closing socket")
        ws.close()

def link_output(ip, router_name, monitor_name, output_number):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())
        router_id = get_router_id(ip, router_name)
        monitor_id = get_router_id(ip, monitor_name)
        router_outputs = get_option(ws, router_id, "Outputs")
        for output_entry in router_outputs[str(output_number)]:
            if output_entry[0]:
                for action in output_entry[1]:
                    for action_name in action:
                        do_action(ws, action_name, action[action_name])
    finally:
        print("closing socket")
        ws.close()



def delete_ccs(ip):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())
        for cam_id in config["payload"]["Video Processor"]:
            do_action(ws, "delete", [cam_id])
    finally:
        ws.close()


def setup_cc(ip, model, name, cc_ip):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        cc_id = do_action(ws, "new", [f"CyElement.{model}"])
        print(cc_id)
        change(ws, cc_id, "name", name)
        change(ws, cc_id, "ip", cc_ip)
    finally:
        print("closing socket")
        ws.close()

def get_cc_id(ip, cc_name):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())
        for cc_id in config["payload"]["Video Processor"]:
            if config["payload"]["Video Processor"][cc_id]["Name"] == cc_name:
                return cc_id
    finally:
        ws.close()

def link_cc(ip, cc_chanel, cam_number):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())
        cam_id = get_cam_id(ip, cam_number)
        cc_channels = get_option(ws, cam_id, "Video Processor")
        for channel in cc_channels:
            if 'Name' in channel[0]:
                exp_cc_channel = f"{channel[0]['Name']}:{channel[0]['Input']}"
                if  exp_cc_channel == cc_chanel:
                    for action in channel[1]:
                        for action_name in action:
                            do_action(ws, action_name, action[action_name])
    finally:
        ws.close()

def setup_autobridge(ip, bridge_value):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())["payload"]
        global_id = next(iter(config["Global"]))
        print(config["Global"])
        print(global_id)
        change(ws, global_id, "auto_network_bridge", str(bridge_value))
    finally:
        print("closing socket")
        ws.close()

def delete_LAN_ip(ip):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())["payload"]
        for lan_id in config["IP"]:
            do_action(ws, "delete", [lan_id])
    finally:
        print("closing socket")
        ws.close()

def add_LAN_ip(ip, lan_itf, lan_ip, lan_mask):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())["payload"]
        new_id = do_action(ws, "new", ["CyElement.LanIp"])
        change(ws, new_id, "interface", lan_itf)
        change(ws, new_id, "ip", lan_ip)
        change(ws, new_id, "mask", lan_mask)
    finally:
        print("closing socket")
        ws.close()

def list_config_blocks(ip):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())
        for block_name in config['payload']:
            print(block_name)
    finally:
        ws.close()