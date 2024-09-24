# Lauri Varjo, 2024

from phue import Bridge
import subprocess
from time import sleep

class Light():
    """ a convenience class to control one Philips Hue light using the phue library ref: https://github.com/studioimaginaire/phue
    """
    def __init__(self, bridge_name = "0017887f0766", bridge_ip=None, light_id=1):
        bridge_ip = self.find_bridge_ip(bridge_name) if bridge_ip is None else bridge_ip
        self.b = Bridge(bridge_ip)
        self.b.connect()
        self.b.get_api()
        self.light_id = light_id
        # self.blink()

    def find_bridge_ip(self, bridge_name):
            """ gets bridge ip by hostname when connected to the same ethernet
            """
            result = subprocess.run(['arp', '-a'], stdout=subprocess.PIPE)

            ips = []
            network_base_ip = "192.168.50"
            for line in str(result.stdout).split("\\n"):
                for col in line.split(" "):
                    if network_base_ip in col:
                        ips.append(col)

            for ip in ips[2:-1]:
                ping_res = subprocess.run(['ping', '-a', f'{ip}', '-n', '1', '-w', '1'], stdout=subprocess.PIPE).stdout.decode("utf-8")
                name = ping_res.split("\n")[1].split(" ")[1]
                if name == bridge_name:
                    return ip
                
            raise RuntimeError("No bridge found. Check that the bridge is connected and the name is correct")
    
    def on(self):
        self.b.set_light(self.light_id, 'on', True)

    def off(self):
        self.b.set_light(self.light_id, 'on', False)

    def brightness(self,val):
        if not self.b.get_light(self.light_id, 'on'):
            self.b.set_light(self.light_id, 'on', True)
        self.b.set_light(self.light_id, 'bri', val)

    def blink(self, n=1, delay=1):
        for i in range(n):
            self.on()
            self.brightness(255)
            sleep(delay)
            self.b.set_light(self.light_id, 'on', False)
            sleep(delay)


if __name__=="__main__":
    l = Light()
    l.on()
    l.brightness(255)
    l.off()