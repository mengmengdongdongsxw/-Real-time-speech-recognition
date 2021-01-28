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
import pyaudio

# reload(sys)
# sys.setdefaultencoding("utf8")
logging.basicConfig()

#建立通讯连接的密钥
base_url = "ws://rtasr.xfyun.cn/v1/ws"
app_id = ""
api_key = ""

pd = "edu"

end_tag = "{\"end\": true}"

#
order_list = []
order_list.append([])
order_list.append([])

CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1                # 声道数
RATE = 16000                # 采样率
RECORD_SECONDS = 600
p = pyaudio.PyAudio()

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
        self.flag_order = 1

    def send(self):
        while True:
            stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
            print("*" * 10, "请输入语音命令")
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                self.ws.send(data)
                if not data:
                    break
                if self.flag_order == 0:
                    print("*" * 10, "执行结束\n")
                    break
            break
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
                if result_dict["action"] == "started":
                    print("handshake success, result: " + result)

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
                            if '左' in order:
                                print("%s" % ('左转'))
                            elif '右' in order:
                                print("%s" % ('右转'))
                            elif '停' in order or '刹' in order or '下' in order:
                                print("%s" % ('停车'))
                            elif '前' in order or '直' in order or '启' in order or '起' in order or '行' in order:
                                print("%s" % ('直行'))
                            elif '后' in order or '倒' in order:
                                print("%s" % ('后退'))
                            elif '退' in order or '出' in order:
                                print("%s" % ('退出'))
                                self.flag_order = 0
                            else:
                                print("%s" % ('keep'))

                if result_dict["action"] == "error":
                    print("rtasr error: " + result)
                    self.ws.close()
                    return

        except websocket.WebSocketConnectionClosedException:
            ()
            #print("receive result end")

    def close(self):
        self.ws.close()
        print("connection closed")

#if __name__ == '__main__':
#    client = Client()
#    client.send()





