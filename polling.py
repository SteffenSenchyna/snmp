from datetime import datetime
from pysnmp.hlapi import *
import time
from pprint import pprint
from pymongo import MongoClient
import os
from dotenv import load_dotenv


# Firewall CPU
# for (errorIndication,
#      errorStatus,
#      errorIndex,
#      values) in nextCmd(SnmpEngine(),
#                         CommunityData('cs1', mpModel=0),
#                         UdpTransportTarget((device_ip, 161)),
#                         ContextData(),
#                         ObjectType(ObjectIdentity(
#                             'FORTINET-FORTIGATE-MIB', "fgSystemInfo")),
#                         lexicographicMode=False):
#     for v in values:
#         print(v)

# Old CPU MIB
# for (errorIndication,
#      errorStatus,
#      errorIndex,
#      values) in nextCmd(SnmpEngine(),
#                         CommunityData('cs1', mpModel=0),
#                         UdpTransportTarget((device_ip, 161)),
#                         ContextData(),
#                         ObjectType(ObjectIdentity(
#                             'OLD-CISCO-CPU-MIB', "busyPer")),
#                         ObjectType(ObjectIdentity(
#                             'OLD-CISCO-CPU-MIB', "avgBusy1")),
#                         ObjectType(ObjectIdentity(
#                             'OLD-CISCO-CPU-MIB', "avgBusy5")),
#                         lexicographicMode=False):
#     for v in values:
#         print(v)


# New CPU MIB
# for (errorIndication,
#      errorStatus,
#      errorIndex,
#      values) in nextCmd(SnmpEngine(),
#                         CommunityData('cs1', mpModel=0),
#                         UdpTransportTarget((device_ip, 161)),
#                         ContextData(),
#                         ObjectType(ObjectIdentity(
#                             'CISCO-PROCESS-MIB', "cpmCPUTotal5secRev")),
#                         ObjectType(ObjectIdentity(
#                             'CISCO-PROCESS-MIB', "cpmCPUTotal1minRev")),
#                         ObjectType(ObjectIdentity(
#                             'CISCO-PROCESS-MIB', "cpmCPUTotal5minRev")),
#                         lexicographicMode=False):
#     for v in values:
#         print(v)
while True:
    device_ips = ["10.0.5.21", "10.0.5.22",
                  "10.0.5.31", "10.0.5.32"]
    for device_ip in device_ips:
        ints_init = []
        ints_delta = []
        ints_util = []
        for (errorIndication,
             errorStatus,
             errorIndex,
             values) in nextCmd(SnmpEngine(),
                                CommunityData('cs1', mpModel=0),
                                UdpTransportTarget((device_ip, 161)),
                                ContextData(),
                                ObjectType(ObjectIdentity(
                                    'IF-MIB', 'ifIndex')),
                                ObjectType(ObjectIdentity(
                                    'IF-MIB', 'ifDescr')),
                                ObjectType(ObjectIdentity('IF-MIB', 'ifType')),
                                ObjectType(ObjectIdentity(
                                    'IF-MIB', 'ifInOctets')),
                                ObjectType(ObjectIdentity(
                                    'IF-MIB', 'ifOutOctets')),
                                ObjectType(ObjectIdentity(
                                    'IF-MIB', 'ifSpeed')),
                                lexicographicMode=False):
            interfaces = {}
            for v in values:
                interfaces[v[0].prettyPrint().split("::")[1].split(".")
                           [0]] = v[1].prettyPrint()

            ints_init.append(interfaces)

        time.sleep(1)

        for (errorIndication,
             errorStatus,
             errorIndex,
             values) in nextCmd(SnmpEngine(),
                                CommunityData('cs1', mpModel=0),
                                UdpTransportTarget((device_ip, 161)),
                                ContextData(),
                                ObjectType(ObjectIdentity(
                                    'IF-MIB', 'ifIndex')),
                                ObjectType(ObjectIdentity(
                                    'IF-MIB', 'ifDescr')),
                                ObjectType(ObjectIdentity('IF-MIB', 'ifType')),
                                ObjectType(ObjectIdentity(
                                    'IF-MIB', 'ifInOctets')),
                                ObjectType(ObjectIdentity(
                                    'IF-MIB', 'ifOutOctets')),
                                ObjectType(ObjectIdentity(
                                    'IF-MIB', 'ifSpeed')),
                                lexicographicMode=False):
            interfaces = {}
            for v in values:
                interfaces[v[0].prettyPrint().split("::")[1].split(".")
                           [0]] = v[1].prettyPrint()

            ints_delta.append(interfaces)

        for i, k in zip(ints_delta, ints_init):
            interfaces_delta = {}
            deltaInOctets = int(i["ifInOctets"]) - int(k["ifInOctets"])
            deltaOutOctets = int(i["ifInOctets"]) - int(k["ifInOctets"])
            speed = int(i["ifSpeed"])
            if speed == 0:
                speed = 1000000000
            inputUtil = (deltaInOctets * 8 * 100) / (speed)
            outputUtil = (deltaOutOctets * 8 * 100) / (speed)
            util = (deltaInOctets + deltaOutOctets) * 8 / speed * 100
            interfaces_delta["ifDescr"] = i["ifDescr"]
            interfaces_delta["ifType"] = i["ifType"]
            interfaces_delta["utils"] = {
                "inputUtil": inputUtil, "outputUtil": outputUtil, "util": util}
            ints_util.append(interfaces_delta)

        try:
            load_dotenv()
            ints_dict = {"interfaces": ints_util,
                         "created_at": datetime.utcnow()}
            mongoURL = os.environ["MONGOURL"]
            client = MongoClient(f"mongodb://{mongoURL}/")
            logs = client["snmp-bandwidth"]
            log_table = logs[device_ip]
            result = log_table.insert_one(ints_dict)
            if result.acknowledged != True:
                print("Could not upload SNMP GET request to DB")

            print(f"Posted to DB with id {result.inserted_id}")
        except Exception as e:
            print(e)
