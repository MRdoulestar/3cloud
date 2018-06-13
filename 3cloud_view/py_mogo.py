#coding:utf-8
#@auth:yunsle
#@description:3cloud日志可视化平台

from pymongo import MongoClient
from flask import *
import json
import datetime
from bson import ObjectId
# gevent
from gevent import monkey
from gevent.pywsgi import WSGIServer
monkey.patch_all()
#geoip
import geoip2.database
geo_reader = geoip2.database.Reader("GeoLite2-City.mmdb")

app=Flask(__name__)
app.config.update(DEBUG=True)

conn = MongoClient('127.0.0.1',27017)
db = conn['3cloud']
db.authenticate('y*','5*')
col = db.log

geo_data = []
line_pos = 0

class JSONEncoder(json.JSONEncoder):
    '''处理ObjectId,该类型无法转为json'''
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return datetime.datetime.strftime(o,'%Y-%m-%d %H:%M:%S')
        return json.JSONEncoder.default(self, o)

#展示3D地球
@app.route("/globe")
def globe():
   return send_file("template/3D-light.html")
#展示平面地图
@app.route("/map")
def map():
   return send_file("template/2D-lines3d-gl.html")
#收集日志进行存储
@app.route("/push/data",methods=['POST'])
def pushdata():
    try:
        data = json.loads(request.get_data())
        app.logger.info(data)
        res = col.insert(data)
        res = JSONEncoder().encode(res)
    except Exception as e:
        return str(e)
    return json.dumps(res)
#查询ip经纬度
def get_geo(item):
    try:
        src = geo_reader.city(item["data"][0][0])
        dst = geo_reader.city(item["data"][1][0])
        item["data"] = [
            [src.location.longitude,src.location.latitude],
            [dst.location.longitude,dst.location.latitude]
        ]
    except Exception as e:
        app.logger.warn(e)
        return False
    return item
#获取经纬度信息进行可视化
@app.route("/get/geodata")
def getdata():
    global geo_data
    global line_pos
    line_pos_tmp = line_pos
    if geo_data == []:
        for i in col.find():
            i = get_geo(i)
            line_pos += 1
            #跳过未查到的IP，如内网IP等
            if i:
                item = JSONEncoder().encode(i)
                geo_data.append(item)
    else:
        for i in col.find().skip(line_pos_tmp):
            i = get_geo(i)
            line_pos += 1
            if i:
                item = JSONEncoder().encode(i)
                geo_data.append(item)
                print(item)
                
    return json.dumps(geo_data)
        #return jsonify(data)

if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=80, thread=True)
    http_server = WSGIServer(("127.0.01", 8000), app)
    http_server.serve_forever()





