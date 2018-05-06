#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3

import os
import time
import glob

# 全局变量
speriod=(15*60)-1
dbname='/var/www/templog.db'

''' 
如果需要创建一个数据库，请在终端使用如下命令：
sqlite3 templog.db
然后执行如下SQL语句：

BEGIN;
CREATE TABLE temps (timestamp DATETIME, temp NUMERIC);
COMMIT;

Temps有两个字段：时间戳，即输入温度的日期和时间，
另一个字段用于存储温度。BEGIN和COMMIT命令确保事务保存在数据库中。
'''

# 将温度存储在数据库中
def log_temperature(temp):
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    curs.execute("INSERT INTO temps values(datetime('now', 'localtime'), (?))", (temp,))
    # 提交更改
    conn.commit()
    conn.close()


# 显示数据库内容
def display_data():
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    for row in curs.execute("SELECT * FROM temps"):
        print str(row[0])+"	"+str(row[1])
    conn.close()


# 获取温度数据
# returns None on error, or the temperature as a float
def get_temp(devicefile):

    try:
        fileobj = open(devicefile,'r')
        lines = fileobj.readlines()
        fileobj.close()
    except:
        return None

    # get the status from the end of line 1 
    status = lines[0][-4:-1]

    # is the status is ok, get the temperature from line 2
    if status=="YES":
        print status
        tempstr= lines[1][-6:-1]
        tempvalue=float(tempstr)/1000
        print tempvalue
        return tempvalue
    else:
        print "There was an error."
        return None


# main function
# This is where the program starts 
def main():

    # enable kernel modules
    #os.system('sudo modprobe w1-gpio')
    #os.system('sudo modprobe w1-therm')

    # 搜索以28开头的设备文件
    devicelist = glob.glob('/sys/bus/w1/devices/28*')
    if devicelist=='':
        return None
    else:
        # append /w1slave to the device file
        w1devicefile = devicelist[0] + '/w1_slave'

#    while True:

    # 从设备文件中获取温度
    temperature = get_temp(w1devicefile)
    if temperature != None:
        print "temperature="+str(temperature)
    else:
        # 有时读取在第一次尝试时失败
        # 所以我们需要重试
        temperature = get_temp(w1devicefile)
        print "temperature="+str(temperature)

        # 将温度存储在数据库中
    log_temperature(temperature)

        # display the contents of the database
#        display_data()

#        time.sleep(speriod)


if __name__=="__main__":
    main()




