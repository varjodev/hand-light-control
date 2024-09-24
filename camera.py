# Lauri Varjo, 2024

import urllib
import urllib.request
import json
from pprint import pprint

class HTTPCamera():
    """ class to drive the ESP32-CAM over HTTP
    """
    def __init__(self, camera_url="http://192.168.50.14", config_json=None, config_name=None):
        self.url = camera_url
        if config_json is not None:
            self.config = self.set_config(config_json, config_name)
        else:
            self.config = self.get_status()
            self.__control("vflip", 0) # For some reason it's not included in the json, TODO: fix in the camera code
            self.config["vflip"] = 0

        print("Camera initialized")

    def get_status(self, verb=False):
        res = urllib.request.urlopen(self.url+"/status")
        status = json.load(res)
        pprint(status) if verb else 0
        return status
    
    def set(self, name, val, verb=True):
        if name not in self.config:
            print("Not a valid parameter")
            return

        if self.config[name] != val:
            print(f"set {name}: {self.config[name]} -> {val}") if verb else 0
            self.__control(name, val)
            self.config[name] = val

    def toggle(self, name):
        self.set(name,1) if self.config[name] == 0 else self.set(name,0)

    def __control(self, name, val):
        urllib.request.urlopen(self.url+f"/control?var={name}&val={val}")

    def set_config(self, config_json, config_name):
        with open(config_json) as f:
            config = json.load(f)

        curr_status = self.get_status()
        config = config[config_name] if config_name is not None else config["default"]
        for parameter in config:
            if parameter == "vflip":
                self.__control(parameter,config[parameter])

            elif curr_status[parameter] != config[parameter]:
                print("Changing")
                self.__control(parameter,config[parameter])

        return config


if __name__=="__main__":
    cam = HTTPCamera(config_json="camera_config.json", config_name="myconfig")
    