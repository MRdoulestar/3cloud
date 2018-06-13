# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os
import requests
import datetime
import pyinotify
import logging
import time
import json
import hashlib
import re
import requests
import socket,fcntl,struct

filt_rhost = re.compile(r"rhost=((?:[0-9]{1,3}\.){3}[0-9]{1,3})")
filt_user = re.compile(r"\buser\b=(.*)")
#pos = 0
conffile = 'hash.conf'
path = '/var/log/auth.log'

posturl="http://3cloud.*.com/push/data"
 
ban_ip_dict = {}

def mymd5(line):
    try:
        m2 = hashlib.md5()  
        m2.update(line.encode('utf-8'))  
        return m2.hexdigest()
    except Exception as e:
        print(str(e))
        return ''

def get_local_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15].encode('utf-8')))[20:24])

def handle_log(line):
    #ip黑名单
    global ban_ip_dict
    #正则处理
    #print(line.strip())
    temp = line.strip()
    src_ip=""
    dst_ip=get_local_ip("eth1")
    user=""
    data=""
    ch1 = filt_rhost.search(temp)
    ch2 = filt_user.search(temp)
    if ch1 and ch2:
        src_ip = ch1.group(1)
        user = ch2.group(1)
    if src_ip != "":
        if str(src_ip) in ban_ip_dict:
            ban_ip_dict[str(src_ip)] +=1
            if ban_ip_dict[str(src_ip)] >15:
                with open("/etc/hosts.deny","a") as f:
                    f.write("sshd:"+str(src_ip)+":deny\n")
        else:
            ban_ip_dict[str(src_ip)] = 1
        data = {"type":"ssh","data":[[src_ip],[dst_ip]],"timestamp":time.time(),"payload":user,"ext":""}
    return data

def postlog(line):
    data = handle_log(line)
    if type(data) != str:
        data = json.dumps(data)
        print(data)
        res = requests.post(posturl, data=data)
    else:
        pass        
    

def printlog():
    #global pos
    try:
            pos = 0
            newhash = ''
            fd = open(path)
            line = fd.readline()
            #将文件指针移到行头
            fd.seek(0, os.SEEK_SET)
            newhash = mymd5(line)
            if os.path.isfile(conffile):
                with open(conffile) as fr:
                    data = json.loads(fr.read())
                 
                myhash = data['myhash']
                 
                if newhash == myhash:
                    #print('the same')
                    pos = data['pos']
                else:
                    pass #新创建的文件重头读取
           
            #fd = open(path)
            if pos != 0:
                fd.seek(pos,0)
            while True:
                line = fd.readline()
                if line.strip():
                    #处理日志并发送
                    postlog(line)
                pos = pos + len(line)
                if not line.strip():
                    break
            fd.close()
            with open(conffile,'w') as fr:
                fr.write(json.dumps({'pos':pos,'myhash':newhash}))
    except Exception as e:
        print(str(e))
class MyEventHandler(pyinotify.ProcessEvent):
      
    #当文件被修改时调用函数
    def process_IN_MODIFY(self, event):
        try:
            printlog()
        except Exception as e:
            print(str(e))
    #文件自动被删除
    # 文件被删除 或者切割
    def process_IN_MOVE_SELF(self,event):
        global notifier
        try:
            notifier.stop()
            #wm.rm_watch(0)
        except Exception as e:
            print(str(e))
notifier = None
def main():
    global notifier,pos
     
      
    while True:
        if os.path.isfile(path):
             
            #输出前面的log
            printlog()
            # watch manager
            wm = pyinotify.WatchManager()
            eh = MyEventHandler()
            notifier = pyinotify.Notifier(wm, eh)
            wm.add_watch('/var/log/auth.log', pyinotify.ALL_EVENTS, rec=True)
              
  
            # notifier
            try:
                notifier.loop()
            except Exception as e:
                print(str(e))
            print('end one time')
        else:
            time.sleep(20)
  
if __name__ == '__main__':
    main()
