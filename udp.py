import socket
import struct
import binascii
import threading
from io import BytesIO

import cv2

import numpy as np

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--host', type=str, help='The IP at the server is listening', required=True)
parser.add_argument('--port', type=int, help='The port on which the server is listening', required=True)

args = parser.parse_args()

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = args.host
port = args.port
# server_address = (host, port)

local_addr = ('', 8080)
sock.bind(local_addr)

def pack(str):
    str_p = ''
    while(str):
        _str = str[0:2]
        s = int(_str, 16)
        str_p += struct.pack('B', s)
        str = str[2:]
    return str_p

def unpack(str):
    return str[0:1],str[1:3],str[4:5],str[5:8]
    
def binhex2int(b):
    return int(binascii.hexlify(b), 16)

def join_img(data,cma_id, img_cnt):
    for d in data:
        d+=d
    img_np=np.frombuffer(d, np.uint8)
    print(img_np.shape)
    img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
    print(img.shape)
    cv2.imwrite('{}_{}.jpg'.format(cma_id, img_cnt), img)
# 一次握手
# send_str = 'fe00020001000a350001020301'
# send_pack = pack(send_str)
# print('send to {} : {}'.format(server_address, send_pack))
# sent = sock.sendto("get".encode('utf-8'), server_address)

cam_curr = -1
img_bytes = b''
img_seri = 0
img_cnt = 0
img_bytes_arr = []
while True:
    data, server = sock.recvfrom(65507)
    h, b, cam_id, seri = unpack(data)        
    if cam_curr != cam_id:
        print('cam_id:{}, seri:{}'.format(cam_id,img_seri))
        if(img_seri>0):
            join_img(img_bytes_arr,cam_id, img_cnt)
        cam_curr = cam_id
        img_buff = b''
        img_bytes_arr = []
        img_bytes_arr.append(data[8:])
        img_seri = 1
    else:
        img_seri+=1
        img_bytes_arr.append(data[8:])
        # img_buff+=img_data

sock.close()

