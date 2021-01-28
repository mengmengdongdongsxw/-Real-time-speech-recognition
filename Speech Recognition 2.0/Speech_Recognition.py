# -*- encoding:utf-8 -*-

import sys
import hashlib
from hashlib import sha1
import hmac
import base64
from socket import *
import json, time, threading
from websocket import create_connection
import websocket
from urllib.parse import quote
import logging
import get_audio_user
import string
import math

# reload(sys)
# sys.setdefaultencoding("utf8")
logging.basicConfig()

input_filename = "input.wav"  # 麦克风采集的语音输入
input_filepath = "音频存储位置"  # 输入文件的path
in_path = input_filepath + input_filename
get_audio_user.get_audio(in_path)

base_url = "ws://rtasr.xfyun.cn/v1/ws"
app_id = ""
api_key = ""
file_path = r"音频存储位置input.wav"

pd = "edu"

end_tag = "{\"end\": true}"

order_list = []
order_list.append([])
order_list.append([])

class Client():
    def __init__(self):
        ts = str(int(time.time()))
        tt = (app_id + ts).encode('utf-8')
        md5 = hashlib.md5()
        md5.update(tt)
        baseString = md5.hexdigest()
        baseString = bytes(baseString, encoding='utf-8')

        apiKey = api_key.encode('utf-8')
        signa = hmac.new(apiKey, baseString, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')

        self.ws = create_connection(base_url + "?appid=" + app_id + "&ts=" + ts + "&signa=" + quote(signa))
        self.trecv = threading.Thread(target=self.recv)
        self.trecv.start()

    def send(self, file_path):
        file_object = open(file_path, 'rb')
        try:
            index = 1
            while True:
                chunk = file_object.read(1280)
                if not chunk:
                    break
                self.ws.send(chunk)

                index += 1
                time.sleep(0.04)
        finally:
            file_object.close()

        self.ws.send(bytes(end_tag.encode('utf-8')))
        # print("send end tag success")

    def recv(self):
        try:
            while self.ws.connected:
                result = str(self.ws.recv())
                if len(result) == 0:
                    print("receive result end")
                    break
                result_dict = json.loads(result)
                # 解析结果
                # if result_dict["action"] == "started":
                #    print("handshake success, result: " + result)

                if result_dict["action"] == "result":
                    result_1 = result_dict
                    # result_2 = json.loads(result_1["cn"])
                    # result_3 = json.loads(result_2["st"])
                    # result_4 = json.loads(result_3["rt"])
                    # print("rtasr result: " + result_1["data"])

                    data_out = json.loads(result_1["data"])
                    flag_type = data_out.get('cn').get('st').get('type')
                    if flag_type == "0" :
                        length = len(data_out.get('cn').get('st').get('rt')[0].get('ws'))
                        i=0
                        order = ''
                        for i in range(length) :
                            flag_wp = data_out.get('cn').get('st').get('rt')[0].get('ws')[i].get('cw')[0].get('wp')
                            if flag_wp == 'n' :
                                result_w = data_out.get('cn').get('st').get('rt')[0].get('ws')[i].get('cw')[0].get('w')
                                order = order + result_w
                                time_out_bg = data_out.get('cn').get('st').get('bg')
                                time_out_we = data_out.get('cn').get('st').get('rt')[0].get('ws')[i].get('we')
                                time_out = int(time_out_bg) + int(time_out_we) * 10
                        if order :
                            print("%s %s" % (time_out, order))
                            order_list[0].append(time_out)
                            order_list[1].append(order)


                if result_dict["action"] == "error":
                    print("rtasr error: " + result)
                    self.ws.close()
                    return



        except websocket.WebSocketConnectionClosedException:
            length2 = len(order_list[0])
            print(length2)
            ts = int(time.time()*100)
            flag_ts = 0
            i = 0
            while i < length2 :
                order_ts = ts + int(order_list[0][i]/10)
                if flag_ts >= order_ts :
                    i = i + 1
                    continue
                if order_ts == int(time.time()*100) :
                    # print("%s %s" % (order_list[0][i], order_list[1][i]))
                    if '左' in order_list[1][i] :
                        print("%s" % ('左转'))
                    elif '右' in order_list[1][i] :
                        print("%s" % ('右转'))
                    elif '停' in order_list[1][i] or '刹' in order_list[1][i] or '下' in order_list[1][i]:
                        print("%s" % ('停车'))
                    elif '前' in order_list[1][i] or '直' in order_list[1][i] or '行' in order_list[1][i] or '起' in order_list[1][i]:
                        print("%s" % ('直行'))
                    else :
                        print("%s" % ('keep'))
                    i = i + 1
                    flag_ts = order_ts

            #print("receive result end")


    def close(self):
        self.ws.close()
        print("connection closed")



#if __name__ == '__main__':
#    client = Client()
#    client.send(file_path)





