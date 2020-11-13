import logging
import asyncio
import platform

from bleak import BleakClient
from bleak import _logger as logger

import sympy
import numpy as np
import math
import matplotlib.pyplot as plt


class Point:
    x = 0
    y = 0

    def __init__(self,x,y):
        self.x = x
        self.y = y


A = Point(0,0)
B = Point(500,0)
C = Point(250, 500)
dA = 3
dB = 3
dC = 3

CHARACTERISTIC_UUID = "02000000-0000-0000-0000-000000000201"  # <--- Change to the characteristic you want to enable notifications from.
address = (
        "fc:f5:c4:31:16:c2"  # <--- Change to your device's address here if you are using Windows or Linux
        if platform.system() != "Darwin"
        else "B9EA5233-37EF-4DD6-87A8-2A875E821C46"  # <--- Change to your device's address here if you are using macOS
    )


def rssi2dis(RSSI):
    cur_dis = 10 ** ((abs(int(RSSI)) + 16.5) / (10 * 3.45))
    return cur_dis


def trilateration(xa,ya,da,xb,yb,db,xc,yc,dc):
    x,y = sympy.symbols('x y')
    f1 = 2*x*(xa-xc)+np.square(xc)-np.square(xa)+2*y*(ya-yc)+np.square(yc)-np.square(ya)-(np.square(dc)-np.square(da))
    f2 = 2*x*(xb-xc)+np.square(xc)-np.square(xb)+2*y*(yb-yc)+np.square(yc)-np.square(yb)-(np.square(dc)-np.square(db))
    f3 = 2*x*(xa-xb)+np.square(xb)-np.square(xa)+2*y*(ya-yb)+np.square(yb)-np.square(ya)-(np.square(db)-np.square(da))
    result = sympy.solve([f1,f2,f3],[x,y])
    locx,locy = result[x],result[y]
    return [locx, locy]


def notification_handler(sender, data):
    print('new position')
    """Simple notification handler which prints the data received."""
    message = data.decode()
    message = str(message).replace('\x00', '')
    message = message.split(';')
    RSSI_A = message[0]
    RSSI_B = message[1]
    RSSI_C = message[2]
    if RSSI_A != 127 and RSSI_B != 127 and RSSI_C != 127:
        print(RSSI_A, RSSI_B, RSSI_C)
        global dA, dB, dC
        dA = rssi2dis(RSSI_A)
        dB = rssi2dis(RSSI_B)
        dC = rssi2dis(RSSI_C)
        plt.cla()
        plt.xlim((-10, 510))
        plt.ylim((-10, 510))
        plt.title('tri-lateration')
        plt.plot(A.x, A.y, 'o', color='g')
        circleA = plt.Circle((A.x, A.y), dA, color='g', fill=False)
        plt.gcf().gca().add_artist(circleA)

        plt.plot(B.x, B.y, 'o', color='orange')
        circleB = plt.Circle((B.x, B.y), dB, color='orange', fill=False)
        plt.gcf().gca().add_artist(circleB)

        plt.plot(C.x, C.y, 'o', color='b')
        circleC = plt.Circle((C.x, C.y), dC, color='b', fill=False)
        plt.gcf().gca().add_artist(circleC)

        result = trilateration(A.x, A.y, dA, B.x, B.y, dB, C.x, C.y, dC)
        print(result)
        plt.plot(result[0], result[1], 'x', color='r')

        ax = plt.gca()
        ax.set_aspect(1)  # set axe at same size
        plt.legend
        plt.show()
        plt.pause(0.1)


async def run(address, debug=False):
    if debug:
        import sys

        l = logging.getLogger("asyncio")
        l.setLevel(logging.DEBUG)
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(logging.DEBUG)
        l.addHandler(h)
        logger.addHandler(h)

    async with BleakClient(address) as client:
        x = await client.is_connected()
        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
        await asyncio.sleep(5000000.0)
        await client.stop_notify(CHARACTERISTIC_UUID)






plt.ion()#打开交互模式


loop = asyncio.get_event_loop()
loop.run_until_complete(run(address, True))