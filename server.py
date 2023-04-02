# python snmp trap receiver
import time
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
from pysnmp.smi import builder, view, compiler, rfc1902
from pysnmp import hlapi
from pysnmp.proto.api import v2c
from pysnmp.entity.rfc3413.oneliner import ntforg
from dotenv import load_dotenv
from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Assemble MIB browser
mibBuilder = builder.MibBuilder()
mibViewController = view.MibViewController(mibBuilder)
compiler.addMibCompiler(mibBuilder, sources=[
    'http://mibs.snmplabs.com/asn1/@mib@'])
mibBuilder.loadModules('SNMPv2-MIB', 'SNMP-COMMUNITY-MIB')

snmpEngine = engine.SnmpEngine()
load_dotenv()
TrapAgentAddress = '0.0.0.0'  # Trap listerner address
Port = 162  # trap listerner port

print("Agent is listening SNMP Trap on " +
      TrapAgentAddress+" , Port : " + str(Port))
print('--------------------------------------------------------------------------')
config.addTransport(
    snmpEngine,
    udp.domainName + (1,),
    udp.UdpTransport().openServerMode((TrapAgentAddress, Port)),
)

# Configure community here
config.addV1System(snmpEngine, 'cs1', 'cs1')


def cbFun(snmpEngine, stateReference, contextEngineId, contextName,
          varBinds, cbCtx):
    print("Received new Trap message")
    varBinds = [rfc1902.ObjectType(rfc1902.ObjectIdentity(x[0]), x[1]).resolveWithMib(mibViewController)
                for x in varBinds]
    snmp_trap = {
        "system_up_time_instance": "",
        "notification_type": "",
        "source_address": "",
        "community": "",
        "module_id": "",
        "message": ""
    }
    for i, (name, val) in enumerate(varBinds):
        oid = name.prettyPrint()
        value = val.prettyPrint()
        if i == 0:
            snmp_trap["system_up_time_instance"] = value
        elif i == 1:
            snmp_trap["notification_type"] = value
        elif i == 2:
            snmp_trap["source_address"] = value
        elif i == 3:
            snmp_trap["community"] = value
        elif i == 4:
            snmp_trap["module_id"] = value
        else:
            if snmp_trap["message"]:
                snmp_trap["message"] += " "
            snmp_trap["message"] += f"{value}"
    print(snmp_trap)
    mongoURL = os.environ["MONGOURL"]
    snmp_trap["created_at"] = datetime.utcnow()
    client = MongoClient(f"mongodb://{mongoURL}/")
    logs = client["snmp"]
    source_address = snmp_trap["source_address"]
    log_table = logs[source_address]
    result = log_table.insert_one(snmp_trap)
    if result.acknowledged != True:
        print("Could not upload Syslog message to DB")

    print(f"Posted to DB with id {result.inserted_id}")


ntfrcv.NotificationReceiver(snmpEngine, cbFun)

snmpEngine.transportDispatcher.jobStarted(1)

try:
    snmpEngine.transportDispatcher.runDispatcher()
except:
    snmpEngine.transportDispatcher.closeDispatcher()
    raise

# 1.3.6.1.2.1.1.3.0 = 217340 sysUpTimeInstance
# 1.3.6.1.6.3.1.1.4.1.0 = 1.3.6.1.2.1.17.0.2 topologyChange NOTIFICATION-TYPE
# 1.3.6.1.6.3.18.1.3.0 = 10.0.5.21 Trap Address
# 1.3.6.1.6.3.18.1.4.0 = cs1 Community String
# 1.3.6.1.6.3.1.1.4.3.0 = 1.3.6.1.2.1.17 dot1dBridge MODULE-IDENTITY
