import os 
import math
import time
import serial
import struct

port = 'COM8'
baud = 230400
ser = serial.Serial(port, baud, timeout=1)

packet_def = {'S1': [31, bytearray.fromhex('5331')]}


def get_data():
    while True:
        read_size = 31
        data = ser.read(read_size)
        # print(data)
        parse_new_data(data)
        

def parse_new_data(data):
    size = 0
    lens = len(data)
    header = '0x55'
    # Iterate over all the data
    for idx, i in enumerate(data):
        pos = idx
        header_1 = hex(i)
        if header_1 == header and (pos+4) <= lens: 
            header_2 = hex(data[pos+1])  
            if header_2 == header and (pos+4) <= lens:
                check_pos = hex(data[pos+2])
                if check_pos == header:
                    continue
                else:
                    packet_type = chr(data[pos+2]) + chr(data[pos+3])
                    if packet_type in packet_def.keys() and (pos+size) <= lens: 
                        size = packet_def[packet_type][0]
                    if packet_type in packet_def.keys() and (pos+size) <= lens:
                        size = packet_def[packet_type][0]
                        # crc
                        packet_len = (pos+size)
                        if packet_len <= lens:
                            crc_f = data[pos+size-2]
                            crc_s = data[pos+size-1]
                            packet_crc = 256 * crc_f+ crc_s
                            calculated_crc = calc_crc(data[(pos+2):(pos+size-2)])
                            # decode
                            if packet_crc == calculated_crc:
                                latest = parse_packet(data[(pos+2):(pos+size-2)])
                                print(f"{lens}\n{latest}")
                                # record packet data to txt 
                            else:
                                print('crc fail')  

def parse_packet(payload):
    data = parse_S1(payload[3::])
    return data

def rest_buff():
    ser.flushOutput()
    ser.flushInput()

def calc_crc(payload):
    crc = 0x1D0F
    for bytedata in payload:
        crc = crc^(bytedata << 8) 
        for i in range(0,8):
            if crc & 0x8000:
                crc = (crc << 1)^0x1021
            else:
                crc = crc << 1

    crc = crc & 0xffff
    return crc

def parse_S1(payload):
    fmt = '>hhhhhhhhhhhh'
    data = struct.unpack(fmt, payload)
    accels = (data[0:3])
    accels_list = []
    for i in range(len(accels)):
        accel = accels[i] * 20 / math.pow(2,16)
        accels_list.append(accel)
    rates = data[3:6]
    rates_list = []
    for i in range(len(rates)):
        rate = rates[i] * 1260  / math.pow(2,16)
        rates_list.append(rate)
    temps = data[6:10]
    temps_list = []
    for i in range(len(temps)):
        temp = temps[i] * 200  / math.pow(2,16)
        temps_list.append(temp)
    timer = data[10] * 15.259022
    bit_status = data[11]
    return accels_list, rates_list, temps_list, timer, bit_status

get_data()