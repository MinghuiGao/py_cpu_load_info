#!/usr/bin/env python
# encoding=utf-8
import datetime
import sqlite3
import subprocess

import numpy as np
import schedule

tagRk = 1
tagIntel = 2

visionCpuRk = []
checkerCpuRk = []
visionCallbackCpuRk = []
totalRk = []

visionCpuIntel = []
checkerCpuIntel = []
visionCallbackCpuIntel = []
totalIntel = []
global conn
conn = None
global flag
flag = True


def getTables(connection):
    """
    Get a list of all tables
    """
    cursor = connection.cursor()
    cmd = "SELECT name FROM sqlite_master WHERE type='table'"
    cursor.execute(cmd)
    names = [row[0] for row in cursor.fetchall()]
    return names


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except sqlite3.Error as e:
        print(e)

    return None


def isTable(connection, nameTbl):
    """
    Determine if a table exists
    """
    return nameTbl in getTables(connection)


def create_task(connection, task):
    sql = ''' INSERT INTO cpu_load_info(mode,pname,cpu,core,ts,freq,platform,rm)  VALUES(?,
            ?,?,?,?,?,?,?) '''
    cur = connection.cursor()
    cur.execute(sql, task)
    return cur.lastrowid


def create_raw_info_task(connection, task):
    sql = ''' INSERT INTO cpu_load_raw(rawinfo,mode,ts,platform,rm)  VALUES(?,?,?,?,?) '''
    cur = connection.cursor()
    cur.execute(sql, task)
    return cur.lastrowid


mode = "depth*2"


# 需要手动设置 fe depth fe+depth*3+ir*3 fe+depth*3(normal) vision_callback
# mode = "normal"
# mode = "fe_depth"
# mode = "depth_T"
# mode = "fisheye_callback"
# mode = "depth*1_callback"
# mode = "full_callback"
# mode = "fe_depth_callback"
# mode = "depth*2_callback"
# mode = "idle_callback"
# [vcu, vcore, ccu, ccore, totalRk]
def save2DB(data, tag):
    global conn
    with conn:
        plat_form = ""
        freq_v = ""
        freq_c = ""
        freq_dict = {
            "0": lambda t: 1416000 if (t == tagRk) else 2560000,
            "1": lambda t: 1416000 if (t == tagRk) else 2560000,
            "2": lambda t: 1416000 if (t == tagRk) else 2560000,
            "3": lambda t: 1416000 if (t == tagRk) else 2560000,
            "4": lambda t: 1800000,
            "5": lambda t: 1800000,
            None: lambda t: "",
            '': lambda t: "",
        }
        if tag == tagRk:
            plat_form = "rk3399"
        elif tag == tagIntel:
            plat_form = "intel"

        ts = datetime.datetime.now()
        vision_info = (
            mode, "vision", data[0], data[1], str(ts), freq_dict[data[1]](tag), plat_form, "")
        checker_info = (
            mode, "checker", data[2], data[3], str(ts), freq_dict[data[3]](tag), plat_form, "")
        vision_callback_info = (
            mode, "v_callback", data[0], data[1], str(ts), freq_dict[data[1]](tag), plat_form, "")
        create_task(conn, vision_info)
        create_task(conn, checker_info)
        create_task(conn, vision_callback_info)


def saveRawInfo2DB(strData, tag):
    global conn
    with conn:
        plat_form = ""
        if tag == tagRk:
            plat_form = "rk3399"
        elif tag == tagIntel:
            plat_form = "intel"
        ts = datetime.datetime.now()
        raw_info = (strData, mode, plat_form, ts, "")
        create_raw_info_task(conn, raw_info)


# grep top result
def grepTopInfo(filePath):
    file = open(filePath, 'r',
                encoding="UTF-8")
    line = file.readline()
    cpuUsage = []
    while line:
        if '{eservice.vision}' in line:
            fields = line.split(" ")
            cpuUsage.append(fields[17])

        line = file.readline()

    for f in cpuUsage:
        print(f)

    cpuUsageF = np.array(cpuUsage).astype(np.float)
    average = np.mean(cpuUsageF)
    print(average)

    maxUsage = np.max(cpuUsageF)
    minUsage = np.min(cpuUsageF)

    print("max:", maxUsage, "min:", minUsage)


def sh(command, tag):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    res = p.stdout.read()
    # print(res)
    return res


def getCpu():
    rkRes = sh('adb -s 9Y6N950H1Z shell busybox top -d 1 -n 1', tagRk)
    intelRes = sh("adb -s 54AGE18GL20830 shell busybox top -d 1 -n 1", tagIntel)
    saveRawInfo2DB(rkRes, tagRk)
    saveRawInfo2DB(intelRes, tagIntel)
    # print("-------------")
    analysRkRes = analysisCpuInfo(rkRes, tagRk)
    analysIntelRes = analysisCpuInfo(intelRes, tagIntel)
    # save to db
    save2DB(analysRkRes, tagRk)
    save2DB(analysIntelRes, tagIntel)


def filt(e):
    return e != ''


vcoreUsageRk = {'0': [], '1': [], '2': [], '3': [], '4': [], '5': []}
vcoreUsageIntel = {'0': [], '1': [], '2': [], '3': []}
ccoreUsageRk = {'0': [], '1': [], '2': [], '3': [], '4': [], '5': []}
ccoreUsageIntel = {'0': [], '1': [], '2': [], '3': []}


def analysisCpuInfo(cpuInfos, flag):
    commands = cpuInfos.split(b'\n')
    vcu = None
    ccu = None
    tcu = 0
    vcore = None
    ccore = None
    for line in commands:
        line = str(line, "utf-8")
        print(line)
        if '{eservice.vision}' in line:
            fields = line.split(" ")
            while '' in fields:
                fields.remove('')
            # print(fields)
            vcore = fields[fields.index("{eservice.vision}") - 2]
            vcu = fields[fields.index("{eservice.vision}") - 1]
            # print(vcu)
            if flag == tagRk:
                visionCpuRk.append(float(vcu))
                vcoreUsageRk[vcore].append(float(vcu))
            elif flag == tagIntel:
                visionCpuIntel.append(float(vcu))
                vcoreUsageIntel[vcore].append(float(vcu))

        if '{nservicechecker}' in line:
            fields = line.split(" ")
            while '' in fields:
                fields.remove('')
            # print(fields)
            ccore = fields[fields.index("{nservicechecker}") - 2]
            ccu = fields[fields.index("{nservicechecker}") - 1]
            # print("--->", checkerCpu)
            if flag == tagRk:
                checkerCpuRk.append(float(ccu))
                ccoreUsageRk[ccore].append(float(ccu))
            else:
                checkerCpuIntel.append(float(ccu))
                ccoreUsageIntel[ccore].append(float(ccu))

    # if vcu is not None and ccu is not None:
    #     tcu = round(float(vcu) + float(ccu), 1)
    #     if flag == tagRk:
    #         totalRk.append(tcu)
    #     else:
    #         totalIntel.append(tcu)
    # if vcu is not None and ccu is not None:

    if flag == tagRk:
        print("RK3399 vision :", vcu, "% @core", vcore, " checker:", ccu, "% @core", ccore,
              " total: ", tcu, "%.")
    if flag == tagIntel:
        print("Intel  vision :", vcu, "% @core", vcore, " checker:", ccu, "% @core", ccore,
              " total: ", tcu, "%.")
    return [vcu, vcore, ccu, ccore, totalRk]


def getIntelCpu():
    sh("adb -s JJ7014E70900017 shell busybox top -d 1 -n 1", tagIntel)


def analysisVision(cu):
    if cu is None or len(cu) == 0:
        print("not started.")
        return [0, 0, 0]
    cpuUsageF = np.array(cu).astype(np.float)
    average = np.mean(cpuUsageF)
    maxUsage = np.max(cpuUsageF)
    minUsage = np.min(cpuUsageF)
    return [average, maxUsage, minUsage]


def exit_schedule():
    global flag
    flag = False


def main():
    db_file = "cpu_load_info.db"
    global conn
    conn = create_connection(db_file)
    if not isTable(conn, 'cpu_load_info'):
        conn.execute(
            '''CREATE TABLE cpu_load_info ( pid INTEGER, mode INTEGER, pname TEXT, cpu TEXT, 
            core INTEGER, ts TEXT, freq TEXT, platform TEXT, rm TEXT, PRIMARY KEY(pid) 
            )''')
    if not isTable(conn, 'cpu_load_raw'):
        conn.execute('''CREATE TABLE cpu_load_raw ( pid INTEGER,rawinfo TEXT, mode TEXT, platform 
        TEXT, rm TEXT, ts TEXT, PRIMARY KEY(pid) )''')

    schedule.every(1).second.do(getCpu)
    schedule.every(1).second.do(getIntelCpu)
    schedule.every(10).minutes.do(exit_schedule)
    while flag:
        schedule.run_pending()

    conn.close()
    visionAvgRk = np.mean(visionCpuRk)
    visionAvgIntel = np.mean(visionCpuIntel)
    print("vision rk3399: ", round(float(visionAvgRk), 1), " vision intel:",
          round(float(visionAvgIntel), 1))
    checkerAvgRk = np.mean(checkerCpuRk)
    checkerAvgIntel = np.mean(checkerCpuIntel)
    print("checker rk3399: ", round(float(checkerAvgRk), 1), " checker intel:",
          round(float(checkerAvgIntel), 1))
    totalAvgRk = np.mean(totalRk)
    totalAvgIntel = np.mean(totalIntel)
    print("total rk3399: ", round(float(totalAvgRk), 1), " total intel:",
          round(float(totalAvgIntel), 1))
    # core average usage:
    print("vision rk3399: c0=", round(float(np.mean(vcoreUsageRk['0'])), 1),
          " c1=", round(float(np.mean(vcoreUsageRk['1'])), 1),
          " c2=", round(float(np.mean(vcoreUsageRk['2'])), 1),
          " c3=", round(float(np.mean(vcoreUsageRk['3'])), 1),
          " c4=", round(float(np.mean(vcoreUsageRk['4'])), 1),
          " c5=", round(float(np.mean(vcoreUsageRk['5'])), 1)
          )
    print("checker rk3399: c0=", round(float(np.mean(ccoreUsageRk['0'])), 1),
          " c1=", round(float(np.mean(ccoreUsageRk['1'])), 1),
          " c2=", round(float(np.mean(ccoreUsageRk['2'])), 1),
          " c3=", round(float(np.mean(ccoreUsageRk['3'])), 1),
          " c4=", round(float(np.mean(ccoreUsageRk['4'])), 1),
          " c5=", round(float(np.mean(ccoreUsageRk['5'])), 1)
          )

    print("vision intel: c0=", round(float(np.mean(vcoreUsageIntel['0'])), 1),
          " c1=", round(float(np.mean(vcoreUsageIntel['1'])), 1),
          " c2=", round(float(np.mean(vcoreUsageIntel['2'])), 1),
          " c3=", round(float(np.mean(vcoreUsageIntel['3'])), 1)
          )

    print("checker intel: c0=", round(float(np.mean(ccoreUsageIntel['0'])), 1),
          " c1=", round(float(np.mean(ccoreUsageIntel['1'])), 1),
          " c2=", round(float(np.mean(ccoreUsageIntel['2'])), 1),
          " c3=", round(float(np.mean(ccoreUsageIntel['3'])), 1)
          )
    print(datetime.datetime.now())


if __name__ == '__main__':
    main()
