import sys
import time
import os
from socket import error as socket_error
import subprocess

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106
from mpd import MPDClient

serial = i2c(port=0, address=0x3C)
device = sh1106(serial, rotate=2)

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

client = MPDClient()
client.timeout = 10
client.idletimeout = None
client.connect("localhost", 6600)

font = ImageFont.truetype('Verdana.ttf', 45)
font2 = ImageFont.truetype('Verdana.ttf', 13)
font3 = ImageFont.truetype('Verdana.ttf', 23)
font4 = ImageFont.truetype('Arial-Bold.ttf', 20)

with canvas(device) as draw:
    cmd = "hostname -I | cut -d\' \' -f1"
    IP = subprocess.check_output(cmd, shell = True )
    draw.text((45,50), "NOS-1", font=font2, fill=255)
    draw.text((40,0), "G-Dis", font=font4, fill=255)
    draw.text((0, 30), "IP: " + str(IP),  font=font2, fill=255)
time.sleep(10)

while True:

    state = client.status()['state']
    vol=client.status()['volume']

    if '1' in open('/sys/class/gpio/gpio4/value').read():
      if '0' in open('/sys/class/gpio/gpio5/value').read():
        with canvas(device) as draw:
             draw.text((15,15),"Optical 1", font=font3, fill=255)

    if '0' in open('/sys/class/gpio/gpio4/value').read():
      if '1' in open('/sys/class/gpio/gpio5/value').read():
        with canvas(device) as draw:
             draw.text((15,15),"Optical 2", font=font3, fill=255)

    if '1' in open('/sys/class/gpio/gpio4/value').read():
      if '1' in open('/sys/class/gpio/gpio5/value').read():
        if (state == 'stop'):
          with canvas(device) as draw:
             draw.text((0,15),str(vol), font=font, fill=255)

        if state == 'play':
          with canvas(device) as draw:
             elaps = client.status()['elapsed']
             m,s = divmod(float(elaps), 60)
             eltime = "%02d:%02d" % (m, s)
             draw.text((0,15),str(vol), font=font, fill=255)
             draw.text((70,45),str(eltime), font=font2, fill=255)
             draw.text((77,15),">>", font=font4, fill=255)

        if state == 'pause':
          with canvas(device) as draw:
             elaps = client.status()['elapsed']
             m,s = divmod(float(elaps), 60)
             eltime = "%02d:%02d" % (m, s)
             draw.text((0,15),str(vol), font=font, fill=255)
             draw.text((70,45),str(eltime), font=font2, fill=255)
             draw.text((77,15)," ||", font=font4, fill=255)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
