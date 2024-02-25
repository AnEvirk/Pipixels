import sys, json, os
import random

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtGui, QtWidgets
from gui import Ui_MainWindow
import socket
from functools import partial
from struct import pack, unpack
import binascii as ba
from typing import Union, Tuple
import json

ADDR = ('192.168.0.101', 7770)
INDEXES = {
    'KITCHEN': (2, 18),
    'EXIT': (20, 48),
    'WINDOW': (130, 32),
    'RENAT_BED': (68, 26),
    'RENAT_COMP': (106, 24),
    'RENAT_SYNTH': (94, 12),
    'ANDREY_BED': (162, 24),
    'ANDREY_COMP': (186, 11),
    'ANDREY_LOCKER': (197, 5)
}


class Main(Ui_MainWindow):
    def __init__(self, form):
        super().__init__()
        self.setupUi(form)
        self.form = form
        self.conn = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.conn.settimeout(1)
        if not os.path.exists("colors.json"):
            with open("colors.json", 'w') as f:
                f.write('{}')
            self.color_js = {}
        else:
            with open("colors.json", 'r') as f:
                self.color_js = json.loads(f.read())
            for k, v in self.color_js.items():
                p = QPixmap(20, 20)
                p.fill(QColor(*v))
                iq = QIcon(p)
                self.cb_color.addItem(iq, k)
                self.cb_color_changed(0)
        # Color changes
        self.sb_r.valueChanged.connect(self.sb_color_change)
        self.sb_g.valueChanged.connect(self.sb_color_change)
        self.sb_b.valueChanged.connect(self.sb_color_change)
        self.sb_bright.valueChanged.connect(self.sb_color_change)
        self.curr_color = [0, 0, 0]
        self.brightness = 256
        self.sb_color_change(0)

        # BUTTONS BINDS
        self.bt_allrandom.clicked.connect(self.bt_allrandom_clicked)
        self.bt_allgradient.clicked.connect(self.bt_allgradient_clicked)
        self.bt_reset.clicked.connect(self.bt_reset_clicked)
        self.bt_full.clicked.connect(self.bt_full_clicked)
        self.bt_custom.clicked.connect(partial(self.bt_custom_clicked, part='CUSTOM'))
        # customs
        self.bt_kitchen.clicked.connect(partial(self.bt_custom_clicked, part='KITCHEN'))
        self.bt_exit.clicked.connect(partial(self.bt_custom_clicked, part='EXIT'))
        self.bt_window.clicked.connect(partial(self.bt_custom_clicked, part='WINDOW'))

        self.bt_r_bed.clicked.connect(partial(self.bt_custom_clicked, part='RENAT_BED'))
        self.bt_r_synth.clicked.connect(partial(self.bt_custom_clicked, part='RENAT_SYNTH'))
        self.bt_r_comp.clicked.connect(partial(self.bt_custom_clicked, part='RENAT_COMP'))

        self.bt_a_bed.clicked.connect(partial(self.bt_custom_clicked, part='ANDREY_BED'))
        self.bt_a_comp.clicked.connect(partial(self.bt_custom_clicked, part='ANDREY_COMP'))
        self.bt_a_locker.clicked.connect(partial(self.bt_custom_clicked, part='ANDREY_LOCKER'))
        # customs clear
        self.bt_kitchen_2.clicked.connect(partial(self.bt_custom_clicked, part='KITCHEN', color=(0, 0, 0)))
        self.bt_exit_2.clicked.connect(partial(self.bt_custom_clicked, part='EXIT', color=(0, 0, 0)))
        self.bt_window_2.clicked.connect(partial(self.bt_custom_clicked, part='WINDOW', color=(0, 0, 0)))

        self.bt_r_bed_2.clicked.connect(partial(self.bt_custom_clicked, part='RENAT_BED', color=(0, 0, 0)))
        self.bt_r_synth_2.clicked.connect(partial(self.bt_custom_clicked, part='RENAT_SYNTH', color=(0, 0, 0)))
        self.bt_r_comp_2.clicked.connect(partial(self.bt_custom_clicked, part='RENAT_COMP', color=(0, 0, 0)))

        self.bt_a_bed_2.clicked.connect(partial(self.bt_custom_clicked, part='ANDREY_BED', color=(0, 0, 0)))
        self.bt_a_comp_2.clicked.connect(partial(self.bt_custom_clicked, part='ANDREY_COMP', color=(0, 0, 0)))
        self.bt_a_locker_2.clicked.connect(partial(self.bt_custom_clicked, part='ANDREY_LOCKER', color=(0, 0, 0)))

        # Color Save/load
        self.bt_clr_save.clicked.connect(self.bt_clr_save_clicked)
        self.bt_clr_del.clicked.connect(self.bt_clr_del_clicked)
        self.bt_clr_load.clicked.connect(self.bt_clr_load_clicked)
        self.cb_color.currentIndexChanged.connect(self.cb_color_changed)

        print('Initialized')

    def cb_color_changed(self, ind: int):
        # print('cb 0', ind)
        a0 = self.cb_color.currentText()
        # print('cb 1', a0)
        self.le_color.setText(a0)
        # print('cb 2')
        pal = self.wg_color_loader.palette()
        color = QColor(*self.color_js[a0])
        pal.setColor(QPalette.ColorRole.Background, color)
        # print('cb 3')
        self.wg_color_loader.setPalette(pal)
        # print('cb 4')
        pass

    def bt_clr_del_clicked(self):
        cb_ind = self.cb_color.currentIndex()
        cb_text = self.cb_color.currentText()
        if len(self.color_js.keys()) > 1:
            self.color_js.pop(cb_text)
            self.cb_color.removeItem(cb_ind)

        pass

    def bt_clr_load_clicked(self):
        cb_ind = self.cb_color.currentIndex()
        cb_text = self.cb_color.currentText()
        r, g, b = self.color_js[cb_text]
        self.sb_r.setValue(r)
        self.sb_g.setValue(g)
        self.sb_b.setValue(b)

        pass

    def bt_clr_save_clicked(self):
        # print(1)
        cb_ind = self.cb_color.currentIndex()
        # print(2)
        cb_text = self.cb_color.currentText()
        # print(3)
        le_text = self.le_color.text()
        # print(4)
        # r, g, b = self.curr_color
        if le_text != cb_text:
            # print(5,1)
            # self.cb_color.setItemText(cb_ind, le_text)
            self.color_js[le_text] = self.curr_color
            # print(5,2)
            p = QPixmap(20, 20)
            p.fill(QColor(*self.color_js[le_text]))
            iq = QIcon(p)
            self.cb_color.addItem(iq, le_text)
            # self.cb_color.insertItem(self.cb_color.count(), le_text)
            # print(5,3)
        else:
            # print(6,1)
            self.color_js[le_text] = self.curr_color
            p = QPixmap(20, 20)
            p.fill(QColor(*self.color_js[le_text]))
            iq = QIcon(p)
            self.cb_color.setItemIcon(cb_ind, iq)
            # print(6,2)
        with open('colors.json', 'w') as f:
            # print(7,1)
            f.write(json.dumps(self.color_js, indent=4))
            # print(7,2)
        self.cb_color_changed(cb_ind)
        pass

    def bt_allgradient_clicked(self):
        start = pack('H', self.sb_start.value())
        length = pack('H', 200)
        br = pack('B', self.brightness)
        color = QColor()
        barr = bytearray(b'\x04')
        barr += br+start+length
        for i in range(200):
            color.setHsvF(i/200, 1, 1)
            barr += pack('BBB', *color.getRgb()[:3])
        try:
            self.conn.sendto(barr, ADDR)
            print(len(barr), 'bytes sended', barr)
            data = self.conn.recvfrom(1024)
            if data == b'no':
                self.error()
        except:
            self.error('Connection failed')
        pass

    def bt_allrandom_clicked(self):
        start = pack('H', 0)
        length = pack('H', 200)
        br = pack('B', self.brightness)
        color = QColor()
        barr = bytearray(b'\x04')
        barr += br+start+length
        for i in range(200):
            color.setRgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            barr += pack('BBB', *color.getRgb()[:3])
        try:
            self.conn.sendto(barr, ADDR)
            print(len(barr), 'bytes sended', barr)
            data = self.conn.recvfrom(1024)
            if data == b'no':
                self.error()
        except:
            self.error('Connection failed')
        pass

    def bt_reset_clicked(self):
        try:
            self.conn.sendto(b'\x00', ADDR)
            data = self.conn.recvfrom(1024)
            if data == b'no':
                self.error()
        except:
            self.error('Connection failed')

    def bt_full_clicked(self):
        rgb = pack('BBB', *self.curr_color)
        br = pack('B', self.brightness)
        send_data = b'\x01'+br+rgb
        try:
            self.conn.sendto(send_data, ADDR)
            data = self.conn.recvfrom(1024)
            if data == b'no':
                self.error()
        except:
            self.error('Connection failed')
        pass

    def bt_custom_clicked(self, part='CUSTOM', color: Union[Tuple[int, int, int], None] = None):
        # print('custom')
        if part == 'CUSTOM':
            start = pack('H', self.sb_start.value())
            length = pack('H', self.sb_length.value())
        elif part in INDEXES.keys():
            start = pack('H', INDEXES[part][0])
            length = pack('H', INDEXES[part][1])
        else:
            self.error('Error button?')
            return None
        # print(2)
        br = pack('B', self.brightness)
        # print(2,2)
        if color is None:
            rgb = pack('BBB', *self.curr_color)
        else:
            rgb = pack('BBB', *color)
        print(3)
        send_data = b'\x03'+br+start+length+rgb
        print(part, ba.hexlify(send_data).decode('ascii'))
        try:
            self.conn.sendto(send_data, ADDR)
            data = self.conn.recvfrom(1024)
            if data == b'no':
                self.error()
        except:
            self.error('Connection failed')

    def sb_color_change(self, v: int):
        r = self.sb_r.value()
        g = self.sb_g.value()
        b = self.sb_b.value()
        self.curr_color = [r, g, b]
        self.brightness = self.sb_bright.value()
        # print(self.curr_color, self.wg_color.rect())
        pal = self.wg_color.palette()
        color = QColor(*self.curr_color)
        # print(color.getRgb())
        pal.setColor(QPalette.ColorRole.Background, color)
        # pal.setColor(QPalette.ColorRole.Window, color)
        # pal.setColor()
        self.wg_color.setPalette(pal)
        # self.wg_color.update()
        '''qp = QPainter()
        qp.begin(self.wg_color)
        qp.setPen(QPen(QColor(0, 255, 0), 2, Qt.SolidLine))
        qp.setBrush(QColor(*self.curr_color))
        qp.drawRect(QRect(self.wg_color.rect()))
        qp.end()'''

    def error(self, text='Error command'):
        pal = self.statusbar.palette()
        cur = pal.color(QPalette.ColorRole.Text)
        pal.setColor(QPalette.ColorRole.Text, QColor(255, 0, 0))
        self.statusbar.setPalette(pal)
        self.statusbar.showMessage(text, 5000)
        pal.setColor(QPalette.ColorRole.Text, cur)
        self.statusbar.setPalette(pal)

    def successful(self, text='Successful command'):
        pal = self.statusbar.palette()
        cur = pal.color(QPalette.ColorRole.Text)
        pal.setColor(QPalette.ColorRole.Text, QColor(0, 255, 0))
        self.statusbar.setPalette(pal)
        self.statusbar.showMessage(text, 5000)
        pal.setColor(QPalette.ColorRole.Text, cur)
        self.statusbar.setPalette(pal)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = Main(window)
    window.show()
    sys.exit(app.instance().exec_())
