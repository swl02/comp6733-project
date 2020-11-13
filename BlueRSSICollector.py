#!/usr/bin/python

import socket
import time
import datetime
import struct
from threading import Thread
import sys
import csv
from collections import defaultdict

import logging
import asyncio
import platform
from bleak import BleakClient
from bleak import _logger as logger

# -----------------------------------------------------------------------------------
# CONNECT parameter

isRunning = True
read_count = 1
record_list = []

# -----------------------------------------------------------------------------------
#blue tooth connect

address = (
        "fc:f5:c4:31:16:c2"  # <--- Change to your device's address here if you are using Windows or Linux
        if platform.system() != "Darwin"
        else "B9EA5233-37EF-4DD6-87A8-2A875E821C46"  # <--- Change to your device's address here if you are using macOS
    )
CHARACTERISTIC_UUID = "02000000-0000-0000-0000-000000000201"  # <--- Change to the characteristic you want to enable notifications from.


def notification_handler(sender, data):
    """Simple notification handler which prints the data received."""
    message = data.decode()
    message = str(message).replace('\x00', '')
    message = message.split(';')
    RSSI_str = message[0]
    print(RSSI_str)
    global record_list
    record_list.append(int(RSSI_str))


    global read_count
    read_count+=1



async def run(address, read_time):
    async with BleakClient(address) as client:
        is_connet = await client.is_connected()
        if is_connet:

            await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
            sleep_time = read_time/2
            await asyncio.sleep(sleep_time)

            global  read_count
            if read_count == read_time:
                read_count = 1
                await client.stop_notify(CHARACTERISTIC_UUID)


def blue_tooth_connect(address, read_time):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(address, read_time))


# -----------------------------------------------------------------------------------
# DATA record parameter

def dict2csv(record_dic):
    with open('record_data.csv', 'w', newline = '') as f:
        w = csv.writer(f, record_dic.keys(),  quotechar = '|', delimiter = ',', quoting = csv.QUOTE_ALL)
        for key, value in record_dic.items():
            w.writerow((key, value))
        f.close()

def csv2dict(file_name):
    model_dict = defaultdict(list)
    with open(file_name, 'r') as f:
        w = csv.reader(f, quotechar = '|', delimiter = ',', quoting = csv.QUOTE_ALL)
        for eachline in w:
            dic_key = int(eachline[0])
            dic_value =eachline[1]
            dic_value = dic_value.replace('[', '')
            dic_value = dic_value.replace(']', '')
            dic_value = dic_value.split(',')
            model_dict[dic_key] = [int(n) for n in dic_value]
        f.close()
    return model_dict


def dis_RSSI_fuc(p, R):
    #  A is the signal strength of 1m
    # N is the Environmental attenuation factor
    A,N = p
    return 10 ^ ((abs(R) - A) / (10 * N))


def error(p,R,D):
    return dis_RSSI_fuc(p,R) - D

# -----------------------------------------------------------------------------------
# Main Functioin

file_name = 'record_data.csv'
model_dic = csv2dict(file_name)

while True:
    model_type = input("select record or measure modee or save data r/m/s: ")
    if model_type == 'r':
        cur_distance = input("what's the current distance: ")
        record_number = input("how many samples you want to collect?: ")
        record_number = int(record_number)
        print('record begin')
        blue_tooth_connect(address, record_number)

        model_dic[cur_distance] += record_list
        record_list = []
        print('record ending')

    elif model_type == 's':
        dict2csv(model_dic)
        model_dic = csv2dict(file_name)

    elif model_type == 'm':

        recived_RSSI = 0

        # 测量蓝牙信号强度

        if recived_RSSI:
            cur_distance =  10 ** ((abs(R) + 20) / (10 * 3.7))

        print('recived RSSI is :', recived_RSSI, 'current distance is:',  cur_distance)

    else:
        print(model_type)