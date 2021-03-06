#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 监播机上请求监播脚本机，中转暴光
import configparser
import hashlib
import json
import requests
import time
import datetime
import sqlite3
import math
import os
import subprocess
import re
import sys
import socket


usleep = lambda x: time.sleep(x/1000000.0)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class RequestImpression(metaclass=Singleton): 
    iniFile = 'config.ini'
    """request impression api """
    def __init__(self , dirname=''):
        self.config = configparser.ConfigParser();
        self.loadConfig(dirname)
        #sig = self.genSignature({'zd':"sdfadsd" , 'plaery_id': 1, 'time': 2012} , self.secretKey)



    #生成加密文件
    def genSignature(self,data: dict , key: str):
        data = self.ksort(data)
        tmpStr = ''
        for name in data:
            tmpStr += str(name) + "=" + str(data[name])+"&"
        tmpStr += key
        m = hashlib.md5()
        m.update(tmpStr.encode("utf8"))
        return m.hexdigest()


    #读取配置
    def loadConfig(self , dirname: str):
        self.iniFile = os.path.abspath(os.path.dirname(__file__))+"/"+self.iniFile
        self.config.read(self.iniFile)
        self.configMame = self.config.sections()[0]
        self.requestUrl = self.config[self.configMame]['request_url']
        self.secretKey = self.config[self.configMame]['secret_key']
        self.dbPath = self.config[self.configMame]['db_path']
        self.path = self.config[self.configMame]['path']
        self.path.strip()
        if len(self.path) == 0 :
            self.path = dirname
        self.rowId = int(self.config[self.configMame]['row_id'])
        self.readMaxRow = int(self.config[self.configMame]['read_max_row'])
        self.retry = int(self.config[self.configMame]['retry'])
        self.playerId =  self.getPlayerId(self.config[self.configMame]['player_id'])
        self.ipAddress = self.getIpAddress(self.config[self.configMame]['ip_address'])
        self.failFile = self.path+"/req_fail_"+time.strftime("%Y-%m", time.localtime())+".log"
        self.bakupFail = self.path+"/back_req_fail_"+time.strftime("%Y-%m-%d", time.localtime())+".log"

    #获取playerid方法
    def getPlayerId(self,playerId = ''):
        playerId.strip()
        if len(playerId) == 0 :
            playerId = os.popen("/bin/DMS-broadsignID").read().strip()
            playerId = int(playerId)
        return playerId

    #获取本机ip方法
    def getIpAddress(self , ip = ''):
        ip.strip()
        if len(ip) == 0 :
            #ip = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1][0]
            #第二种获取方式,效率会差一些
            ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
        return ip

    #做排序
    def ksort(self,data : dict):
        return {k:data[k] for k in sorted(data.keys())}

    #写入错误日志
    def writeFail(self , data , filePath, mode="a+"):
        with open(filePath, mode) as f:
            f.write(json.dumps(data)+'\n')
        return True

    #获取当前错误文件
    def readFail(self):
        rows = []
        if not os.path.exists(self.failFile):
            return rows
        with open(self.failFile , "r+") as f:
            for line in f:
                rows.append(json.loads(line))
            #f.seek(0)
            #f.truncate()
        return rows
            #f.truncate()
       


    #重试错误
    def retryRequest(self):
        rows = self.readFail()
        for row in rows:
            i=0
            while i < self.retry:
                #ret = False
                ret = self.request(row)
                if ret == False:
                    usleep(500000)
                    i += 1
                    if i == self.retry:
                        print("retry request row id:" , self.rowId , row ," request fail\n")
                        #只能放弃
                        self.writeFail(row , self.bakupFail)
                else:
                    print("retry request row id:" , self.rowId , row ," request sucess\n")
                    rows.remove(row)
                    break;
        self.writeFail(rows , self.failFile, "w")


    #请求
    def request(self , data):
        t = time.time();
        params = {'player_id':str(self.playerId) , 'time':int(t) , 'ip_address':self.ipAddress}
        token = self.genSignature(params , self.secretKey)
        params['data'] = data
        params['token'] = token
        params = json.dumps(params)
        headers = {'Content-type': 'application/json'}
        try:
            r = requests.post(url=self.requestUrl, data=params , headers=headers)
            if r.status_code == 200:
                response = r.json();
                print("request response:" , response)
                if (int(response['code']) == 0):
                    return True
                else:
                    return False
        except:
            return False

    #写入配置
    def writeConfig(self):
        with open(self.iniFile,"w+") as f:
            self.config.write(f)

    #执行
    def execute(self):
        #data = [{"adcopy_id":45 , "player_id":113799}]
        conn = sqlite3.connect(self.dbPath)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        #如果没有记录id，查最后一行记录
        if self.rowId == 0:
            sql = 'SELECT  stat_id FROM monitor_stats_stat order by stat_id desc limit 1'
            cur.execute(sql)
            self.rowId = int(cur.fetchone()[0]) - self.readMaxRow
            self.config.set(self.configMame, "row_id", str(self.rowId))

        sql = 'select count(stat_id) from monitor_stats_stat where stat_id > %s limit 1' % self.rowId
        cur.execute(sql)
        #self.readMaxRow=2
        countRows = int(cur.fetchone()[0])
        pageSize = math.ceil(countRows / self.readMaxRow)
        #print(pageSize)
        #pageSize = 2
        maxId = self.rowId
        for i in range(0,pageSize):
            sql = 'select stat_id , content_id as ad_copy_id , timestamp as imp_time , duration  from monitor_stats_stat where stat_id > %s limit %s , %s' % (maxId , i*self.readMaxRow , self.readMaxRow)
            cur.execute(sql)
            tmpData = []
            for row  in cur.fetchall():
                row = dict(row)
                row['player_id'] = self.playerId
                row['ip_address'] = self.ipAddress
                tmpData.append(row)
                self.rowId = row['stat_id']
            self.config.set(self.configMame, "row_id", str(self.rowId))
            #如果为空
            if not tmpData:
                continue;
            i=0
            while i < self.retry:
                #ret = False
                ret = self.request(tmpData)
                if ret == False:
                    usleep(500000)
                    i += 1
                    if i == self.retry:
                        print("retry request row id:" , self.rowId , tmpData ," request fail")
                        self.writeFail(tmpData , self.failFile)
                else:
                    print("request row id:" , self.rowId , tmpData ," request sucess")
                    break;

        self.writeConfig();
        cur.close()
        conn.close()


#检测进程是否存在
def checkProccess(name):
    ps = subprocess.Popen("ps ax -o pid= -o args= |grep " + name , shell=True, stdout=subprocess.PIPE)
    psPid = ps.pid
    output = str(ps.stdout.read())
    ps.stdout.close()
    ps.wait()
    for line in output.split("\n"):
        res = re.findall("(\d+) (.*)", line)
        if res:
            pid = int(res[0][0])
            if  pid != os.getpid() and pid != psPid:
                return True
    return False



def main():
    dirname, _ = os.path.split(os.path.abspath(__file__))
    #path = os.path.realpath(__file__)
    if not checkProccess(sys.argv[0]):
        try:
            reqImp = RequestImpression(dirname)
            print('Impression Request Start ' , time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) , ' Run')
            #请求错误的
            reqImp.retryRequest()
            #请求最新的
            reqImp.execute()
            print('Impression Request run end')
        except KeyboardInterrupt as e:
            pass
        except Exception as e:
            print(e)
            
    else:
        print("imp_callback runing now")

if __name__ == '__main__':
    main()