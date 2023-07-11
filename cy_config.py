import websocket
import json
import time

debug=True

def check_answer(ws):
    change = None
    while True:
        change = json.loads(ws.recv())
        if "type" in change:     
            if change["type"] == "action_reply":
                break
            elif change["type"] == "option_reply":
                break
            elif change["type"] == "config_data":
                pass
            else:
                print("unsupported type", change["type"], change)
        else:
            return None
    if not change["payload"]:
        return None
    else:
        return change["payload"]

def do_action(ws, actions):
    data = json.dumps({
        "type" : "action_request",
        "request" : actions
    })
    if debug:
        print("\t>",data)
    ws.send(data)
    response = check_answer(ws)
    if debug:
        print("\t<", response)

    return response[-1] if response else None

def do_action_no_ws(ip, actions):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        do_action(ws, actions)
    finally:
        ws.close()

def get_option(ws, item_id, option):
    data = json.dumps({
        "type" : "option_request",
        "request" : [item_id, option]
    })
    if debug:
        print("\t>", data)
    ws.send(data)
    response = check_answer(ws)
    if debug:
        print("\t<", response)
    return response   

def delete_cams(ip):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())
        for cam_id in config["payload"]["Camera"]:
            do_action(ws, {"delete" : [cam_id]})
    finally:
        ws.close()

def change(ws, cam_id, key, value):
    return do_action(ws, {"update" : {"key" : cam_id, "changes" : { key : value }}})

def connect(ws, A_id, B_id):
    return do_action(ws, {"connect" : [A_id, B_id]})

def connect2(A_id, B_id):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        connect(ws, A_id, B_id)
    finally:
        ws.close()

def get_port_id(ip, cam_id, port_name, port_type):
    print("get_port_id lens", cam_id, port_name)
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        port_interfaces = get_option(ws, cam_id, port_type)
        CI0_serial = ":".join(port_name.split(":")[0:-1])
        CI0_port = port_name.split(":")[-1]
        for itf in port_interfaces:
            if itf[0]["device"] == CI0_serial and itf[0]["port"] == CI0_port:
                return itf[1]
    finally:
        ws.close()

def setup_lens(ip, cam_id, lens_type, lens_port, lens_option=""):
    print("setup lens", cam_id, lens_type, lens_port, lens_option)
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        change(ws, f"{cam_id}_l", "model", lens_type)
        port_actions = get_port_id(ip, cam_id, lens_port, "LensInterface")
        do_action(ws, port_actions)
        return change(ws, f"{cam_id}_l", "params", lens_option)
    finally:
        ws.close()

def get_remi_id(ip):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())
        for remi_id in config["payload"]["Remi"]:
            remi_config = config["payload"]["Remi"][remi_id]
            if "Active" in remi_config and remi_config["Active"] == "1":
                return remi_id, remi_config["Tags"]
    finally:
        ws.close()

def delete_remi(ip):
    return setup_remi(ip, "")

def setup_remi(ip, tags):
    print("setup remi", ip, tags)
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())
        remi_id, _ = get_remi_id(ip)
        change(ws, remi_id, "tags", tags)
        time.sleep(2)
    finally:
        ws.close()

def add_remi(ip, tag):
    print("add remi", ip, tag)
    remi_id, remi_tags = get_remi_id(ip)
    tags = ",".join(remi_tags + [tag])
    return setup_remi(ip, tags)

    
def setup_cam(ip, cam_number, cam_name, cam_model):
    print("setup cam", ip, cam_number, cam_name, cam_model)
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())
        # create new camera
        cam_id = do_action(ws, {"new" : ["CyElement.Camera"]})
        change(ws, cam_id, "number", str(cam_number))
        change(ws, cam_id, "name", str(cam_name))
        change(ws, cam_id, "model", str(cam_model))
        return cam_id
    finally:
        ws.close()

def add_cam_ip(ip, cam_number, cam_ip, cam_login, cam_passwd):
    print("add cam ip", ip, cam_ip, cam_login, cam_passwd)
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        # camhead
        cam_id = get_cam_id(ip, cam_number)
        ip_id = get_option(ws, cam_id, "IP")["key"]
        change(ws, ip_id, "ip", str(cam_ip))
        change(ws, ip_id, "login", str(cam_login))
        change(ws, ip_id, "password", str(cam_passwd))
    finally:
        ws.close()

def add_cam_serial(ip, cam_number, cam_port):
    print("add cam serial", ip, cam_number, cam_port)
    cam_id = get_cam_id(ip, cam_number)
    port_action = get_port_id(ip, cam_id, cam_port, "Interface")
    do_action_no_ws(ip, port_action)

def add_lens(ip, cam_number, lens_type, lens_port, lens_option=""):
    print("add lens", ip, cam_number, lens_type, lens_port, lens_option)
    cam_id = get_cam_id(ip, cam_number)
    return setup_lens(ip, cam_id, lens_type, lens_port, lens_option)


def import_cam(ip, device, cam_number):
    print("import cam", ip, device, cam_number)
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
            cam_id = change(ws, imported_cam_id, "auto_camera", "1")
            return cam_id
    finally:
        ws.close()

def delete_routers(ip):
    print("delete routers", ip)
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())
        for router_id in config["payload"]["Router"]:
            do_action(ws, {"delete" : [router_id]})
    finally:
        ws.close()

def setup_router(ip, model, name, router_ip, input_range, output_range, red_tally, green_tally, shared="1"):
    print("setup router", ip, model, name, router_ip, input_range, output_range, red_tally, green_tally, shared)
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        router_id = do_action(ws, {"new" : [f"CyElement.{model}"]})
        change(ws, router_id, "name", name)
        change(ws, router_id, "ip", router_ip)
        change(ws, router_id, "num_inputs", input_range)
        change(ws, router_id, "num_outputs", output_range)
        change(ws, router_id, "tally_red", red_tally)
        change(ws, router_id, "tally_green", green_tally)
        change(ws, router_id, "shared", shared)

        return router_id
    finally:
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

def link_input(ip, router_name, cam_number, input_number):
    print("link input", ip, router_name, cam_number, input_number)
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
                    for actions in cam_entry[1]:
                        do_action(ws, actions)
    finally:
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
                        do_action(ws, action)
    finally:
        ws.close()

def link_output(ip, router_name, monitor_name, output_number):
    print("link output", ip, router_name, monitor_name, output_number)
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
                for actions in output_entry[1]:
                    do_action(ws, actions)
    finally:
        ws.close()



def delete_ccs(ip):
    print("delete ccs", ip)
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())
        for cam_id in config["payload"]["Video Processor"]:
            do_action(ws, {"delete" : [cam_id]})
    finally:
        ws.close()


def setup_cc(ip, model, name, cc_ip):
    print("setup cc", ip, model, name, cc_ip)
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        cc_id = do_action(ws, {"new" : [f"CyElement.{model}"]})
        change(ws, cc_id, "name", name)
        change(ws, cc_id, "ip", cc_ip)
    finally:
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
    print("link cc", ip, cc_chanel, cam_number)
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
                    for actions in channel[1]:
                        do_action(ws, actions)
    finally:
        ws.close()

def setup_autobridge(ip, bridge_value):
    print("setup autobridge", ip, bridge_value)
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())["payload"]
        global_id = next(iter(config["Global"]))
        change(ws, global_id, "auto_network_bridge", str(bridge_value))
    finally:
        ws.close()

def delete_LAN_ip(ip):
    print("delete LAN ip", ip)
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())["payload"]
        for lan_id in config["IP"]:
            do_action(ws, {"delete" : [lan_id]})
    finally:
        ws.close()

def add_LAN_ip(ip, lan_itf, lan_ip, lan_mask):
    print("add LAN ip", ip, lan_itf, lan_ip, lan_mask)
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())["payload"]
        new_id = do_action(ws, {"new" : ["CyElement.LanIp"]})
        change(ws, new_id, "interface", lan_itf)
        change(ws, new_id, "ip", lan_ip)
        change(ws, new_id, "mask", lan_mask)
    finally:
        ws.close()

def get_GPO_id(ip, gpo_name):
    url = f"ws://{ip}/ws"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())["elements"]
        for element in config:
            if element["module"] == "CyElement.NetGpio.GPO":
                if element["properties"]["name"] == gpo_name and element["properties"]["available"] == "1":
                    return element["key"]
    finally:
        ws.close()

def delete_tally_actions(ip):
    url = f"ws://{ip}/ws"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())["elements"]
        for element in config:
            if element["module"] == "CyElement.TallyAction":
                ws.send(json.dumps({"delete":[element["key"]]}))
    finally:
        ws.close()


def set_tally_action(ip, cam_number, gpo_name, tally_type="red"):
    print("set tally action", ip, cam_number, gpo_name, tally_type)
    url = f"ws://{ip}/ws"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        cam_id = get_cam_id(ip, cam_number)
        gpo_id = get_GPO_id(ip, gpo_name)
        msg = {"new":["CyElement.TallyAction","red","",cam_id, gpo_id]}
        if debug:
            print("\t>", msg)
        ws.send(json.dumps(msg))
    finally:
        ws.close()

def delete_BUS(ip):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())["payload"]
        for bus_id in config["Bus"]:
            do_action(ws, {"delete" : [bus_id]})
    finally:
        ws.close()

def create_BUS(ip, bus_type, bus_port, bidirectional="1"):
    print("create BUS", ip, bus_type, bus_port)
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        bus_id  = do_action(ws, {"new" : ["CyElement.Bus", bus_type]})
        port_action = get_port_id(ip, bus_id, bus_port, "Interface")
        do_action(ws, port_action)
        change(ws, bus_id, "bidirectional", bidirectional)
        time.sleep(1)
    finally:
        ws.close()

def list_cameras_models(ip):
    url = f"ws://{ip}/ws/ui"
    ws = websocket.WebSocket()
    try:
        ws.connect(url)
        config = json.loads(ws.recv())["payload"]
        cam_id = do_action(ws, {"new" : ["CyElement.Camera"]})
        models = get_option(ws, cam_id, "Model")
        do_action(ws, {"delete" : [cam_id]})
        for item in models:
            try:
                brand, model = item[0].split(" - ")
                code = item[1]['update']['changes']['model']
                print(f"{brand:<20}{model:<20}{code}")
            except:
                pass
    finally:
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