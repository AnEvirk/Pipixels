import sys

import neopixel as neo
import board
import socket
from struct import pack, unpack
import glob
import time
import numpy as np


class Pixel:
    def __init__(self, pix: neo.NeoPixel, serv: socket.socket):
        self.pix = pix
        self.serv = serv
        self.animation = False
        self.loader()

    def run(self):
        try:
            while True:
                data, addr = self.serv.recvfrom(1024)
                if data[0] == 0x01:
                    # static fill
                    if len(data) < 5:
                        self.serv.sendto(b'no', addr)
                        continue
                    br = data[1]
                    self.pix.brightness = br/256
                    r, g, b = data[2:5]
                    self.pix.fill((r, g, b))
                    self.pix.show()
                    self.serv.sendto(b'ok', addr)
                    pass
                elif data[0] == 0x02:
                    # animation
                    if len(data) < 2:
                        self.serv.sendto(b'no', addr)
                        continue
                    end = data.find(b'\x00')
                    try:
                        end = 0 if end == -1 else end
                        sb = str(data[1:end or len(data)], encoding='ascii')
                    except:
                        self.serv.sendto(b'no', addr)
                        continue
                    self.serv.sendto(b'ok', addr)
                    pass
                elif data[0] == 0x03:
                    # sector fill
                    if len(data) < 9:
                        self.serv.sendto(b'no', addr)
                        continue
                    br = data[1]
                    self.pix.brightness = br / 256
                    start: int = unpack('H', data[2:4])[0]
                    length: int = unpack('H', data[4:6])[0]
                    r, g, b = data[6:9]
                    if start >= len(self.pix):
                        self.serv.sendto(b'no', addr)
                        continue
                    if start < 0:
                        start = 0
                    if start + length > len(self.pix):
                        limit = len(self.pix)-start
                        self.pix[start:start + limit] = [(r, g, b)] * limit
                        self.pix[:length-limit] = [(r, g, b)] * (length - limit)
                    else:
                        self.pix[start:start + length] = [(r, g, b)] * length
                    # length = len(self.pix)-start  else length
                    # self.pix[start:start+length] = [(r, g, b)]*length
                    self.pix.show()
                    self.serv.sendto(b'ok', addr)

                    pass
                elif data[0] == 0x04:
                    # dynamic fill
                    if len(data) < 6:
                        self.serv.sendto(b'no', addr)
                        continue
                    br = data[1]
                    self.pix.brightness = br / 255
                    start: int = unpack('H', data[2:4])[0]
                    length: int = unpack('H', data[4:6])[0]
                    rgb_data = data[6:]
                    rgb_arr = np.frombuffer(rgb_data, dtype=np.uint8).reshape((len(rgb_data)//3, 3)).tolist()
                    # print(rgb_arr)
                    if start >= len(self.pix) or len(rgb_arr) != length:
                        print(length, 'len')
                        self.serv.sendto(b'no', addr)
                        continue
                    if length > len(self.pix):
                        length = len(self.pix)
                    if start < 0:
                        start = 0
                    if start + length > len(self.pix):
                        limit = len(self.pix)-start
                        self.pix[start:start + limit] = rgb_arr[:limit]
                        self.pix[:length-limit] = rgb_arr[limit:length]
                    else:
                        self.pix[start:start + length] = rgb_arr[:length]
                    self.pix.show()
                    self.serv.sendto(b'ok', addr)
                    pass
                elif data[0] == 0x00:
                    # reset
                    self.pix.fill((0, 0, 0))
                    self.pix.show()
                    self.serv.sendto(b'ok', addr)
                    pass
        except KeyboardInterrupt:
            print('CTRL+C EXIT')
        except:
            print(sys.exc_info())

    def loader(self):
        files = glob.glob('anims/*.py')