#! /usr/bin/env python

import time
import subprocess
from socket import error as socket_error
import os.path

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106
from mpd import MPDClient, MPDError, CommandError, ConnectionError

serial = i2c(port=0, address=0x3C)
device = sh1106(serial, rotate=2)

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

class MPDConnect(object):
    def __init__(self, host='localhost', port=6600):
        self._mpd_client = MPDClient()
        self._mpd_client.timeout = 10
        self._mpd_connected = False

        self._host = host
        self._port = port

    def connect(self):
        if not self._mpd_connected:
            try:
                self._mpd_client.ping()
            except(socket_error, ConnectionError):
                try:
                    self._mpd_client.connect(self._host, self._port)
                    self._mpd_connected = True
                except(socket_error, ConnectionError, CommandError):
                    self._mpd_connected = False

    def disconnect(self):
        self._mpd_client.close()
        self._mpd_client.disconnect()

    def _play_pause(self):
        self._mpd_client.pause()
        #return False

    def _next_track(self):
        self._mpd_client.next()
        #return False

    def _prev_track(self):
        self._mpd_client.previous()
        #return False

    def fetch(self):
        song_info = self._mpd_client.currentsong()

        if 'artist' in song_info:
            artist = song_info['artist']
        else:
            artist = ''
        if 'title' in song_info:
            title = song_info['title']
        else:
            title = ''

        song_stats = self._mpd_client.status()
        state = song_stats['state']

        if 'elapsed' in song_stats:
            elapsed = song_stats['elapsed']
            m,s = divmod(float(elapsed), 60)
            h,m = divmod(m, 60)
            eltime = "%02d:%02d" % (m, s)
        else:
            eltime ="00:00"

        if 'audio' in song_stats:
            bit = song_stats['audio'].split(':')[1]
            frequency = song_stats['audio'].split(':')[0]
            z, f = divmod( int(frequency), 1000 )
            if ( f == 0 ):
                frequency = str(z)
            else:
                frequency = str( float(frequency) / 1000 )
            bitrate = song_stats['bitrate']

            audio_info =  bit + ":" + frequency
        else:
            audio_info = ""

        vol = song_stats['volume']

        return({'state':state, 'artist':artist, 'title':title, 'eltime':eltime, 'volume':int(vol), 'audio_info':audio_info})

font = ImageFont.truetype('/root/oled_Nanopi_Neo2/Verdana.ttf', 47)
font2 = ImageFont.truetype('/root/oled_Nanopi_Neo2/Verdana.ttf', 13)
font3 = ImageFont.truetype('/root/oled_Nanopi_Neo2/Verdana.ttf', 23)
font4 = ImageFont.truetype('/root/oled_Nanopi_Neo2/Arial-Bold.ttf', 20)

with canvas(device) as draw:
    device.contrast(255) #0-255
    img_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
       'gdis3.png'))
    logo = Image.open(img_path)
    draw.bitmap((25, 0), logo, fill="white")
time.sleep(5)

with canvas(device) as draw:
    cmd = "hostname -I"
    IP = subprocess.check_output(cmd, shell = True )
    draw.text((0, 20), "IP: " + str(IP),  font=font2, fill=255)
time.sleep(8)

def main():
  client = MPDConnect()
  client.connect()

  while True:

    info = client.fetch()
    state = info['state']
    vol = info['volume']
    eltime = info['eltime']
    artist = info['artist']
    title = info['title']
    audio = info['audio_info']

    if '1' in open('/sys/class/gpio/gpio198/value').read():
      if '0' in open('/sys/class/gpio/gpio199/value').read():
        with canvas(device) as draw:
             draw.text((15,15),"Optical 1", font=font3, fill=255)

    if '0' in open('/sys/class/gpio/gpio198/value').read():
      if '1' in open('/sys/class/gpio/gpio199/value').read():
        with canvas(device) as draw:
             draw.text((15,15),"Optical 2", font=font3, fill=255)

    if '1' in open('/sys/class/gpio/gpio198/value').read():
      if '1' in open('/sys/class/gpio/gpio199/value').read():
        if (state == 'stop'):
          with canvas(device) as draw:
             draw.text((0,13),str(vol), font=font, fill=255)

        if state == 'play':
          with canvas(device) as draw:

             draw.text((35,0), audio, font=font2, fill=255)
             draw.text((0,13),str(vol), font=font, fill=255)
             draw.text((80,50),str(eltime), font=font2, fill=255)
             draw.text((87,20),">>", font=font4, fill=255)

        if state == 'pause':
          with canvas(device) as draw:

             draw.text((35,0), audio, font=font2, fill=255)
             draw.text((0,13),str(vol), font=font, fill=255)
             draw.text((80,50),str(eltime), font=font2, fill=255)
             draw.text((87,20)," ||", font=font4, fill=255)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
