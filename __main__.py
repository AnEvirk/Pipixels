import neopixel as neo
import board
import socket
from struct import pack, unpack
import glob
from pixel import Pixel
import time


if __name__ == '__main__':
    pix = neo.NeoPixel(board.D18, 200, auto_write=False, pixel_order=neo.RGB)
    server = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    server.bind(('', 7770))
    print(board.D18)
    cls = Pixel(pix, server)
    pix.fill((255, 255, 255))
    pix.show()
    time.sleep(1)
    pix.fill((0, 0, 0))
    pix.show()
    cls.run()
