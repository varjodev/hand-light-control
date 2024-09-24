from functools import partial

class KeyHandler():
    def __init__(self, cam, pproc):
        self.cam = cam
        self.pproc = pproc

        self.key_action_table = {"h": [self.cam.toggle,"hmirror",None],
                                 "v": [self.cam.toggle,"vflip",None],
                                 "1": [self.cam.set,"led_intensity",0],
                                 "2": [self.cam.set,"led_intensity",130],
                                 "3": [self.cam.set,"led_intensity",255],
                                 "r": [self.pproc.increment_rot,None,None],
                                 "p": [self.pproc.toggle_param,"postprocess_bool",None],
                                 "f": [self.pproc.toggle_param,"fft",None],
                                 "g": [self.pproc.toggle_param,"fft_filter",None],
                                 "e": [self.pproc.toggle_param,"edges",None],
                                 "b": [self.pproc.toggle_param,"blur",None],
                                 "a": [self.pproc.toggle_param,"average",None],
                                 "t": [self.pproc.toggle_param,"threshold",None]
                                 }
        
        self.preserved_keys = ['s', '.']
        
    def get_free_hotkeys(self):
        free_keys = []
        for code in range(ord('a'),ord('z')+1):
            c = chr(code)
            print(code, c)
            if c not in self.key_action_table.keys() and c not in self.preserved_keys:
                free_keys.append(c)

        return free_keys

    def handle(self, key):
        if key < 0:
            return
        
        c = chr(key)
        if c in self.key_action_table:
            action = self.key_action_table[chr(key)][0]
            if self.key_action_table[c][1] == None:
                action()
            elif self.key_action_table[c][2] == None:
                param1 = self.key_action_table[chr(key)][1]
                action(param1)
            else:
                param1 = self.key_action_table[chr(key)][1]
                param2 = self.key_action_table[chr(key)][2]
                action(param1,param2)
