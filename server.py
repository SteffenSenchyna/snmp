
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
from pysnmp.smi import builder, view, compiler, rfc1902
from discord_webhook import DiscordEmbed, DiscordWebhook
from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Assemble MIB browser
from pysmi import debug as pysmi_debug
pysmi_debug.setLogger(pysmi_debug.Debug('compiler'))

mibBuilder = builder.MibBuilder()
mibViewController = view.MibViewController(mibBuilder)
compiler.addMibCompiler(mibBuilder, sources=["file://./mibs",
                                             'http://mibs.snmplabs.com/asn1/@mib@',
                                             "http://mibs.snmplabs.com/pysnmp/fulltexts/@mib@"])
# mibdump.py  --mib-source ./mibs --mib-source http://mibs.snmplabs.com/asn1/@mib@ FORTINET-FORTIGATE-MIB
mibBuilder.loadModules('SNMPv2-MIB', 'SNMP-FRAMEWORK-MIB', 'SNMP-COMMUNITY-MIB', "IF-MIB",
                       "SNMPv2-CONF", "SNMPv2-SMI", "SNMPv2-TC", "CISCO-SMI", "CISCO-TC",
                       "IPV6-TC",
                       "HCNUM-TC",
                       "FORTINET-FORTIGATE-MIB",
                       "FORTINET-CORE-MIB")
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

config.addV1System(snmpEngine, 'cs1', 'cs1')


def cbFun(snmpEngine, stateReference, contextEngineId, contextName,
          varBinds, cbCtx):
    execContext = snmpEngine.observer.getExecutionContext(
        'rfc3412.receiveMessage:request'
    )
    print(
        f"Received new Trap message from {execContext['transportAddress'][0]}")

    varBinds = [rfc1902.ObjectType(rfc1902.ObjectIdentity(x[0]), x[1]).resolveWithMib(mibViewController)
                for x in varBinds]
    snmp_trap = {
        "system_up_time_instance": "",
        "source_address": execContext['transportAddress'][0],
        "module_id": "",
        "message": ""
    }
    for i, (name, val) in enumerate(varBinds):
        oid = name.prettyPrint()
        value = val.prettyPrint()
        print(f"{oid} = {value}")
        if i == 0:
            snmp_trap["system_up_time_instance"] = value
        elif i == 1:
            snmp_trap["module_id"] = value
        else:
            if i != len(varBinds):
                if snmp_trap["message"]:
                    snmp_trap["message"] += "\n"
                snmp_trap["message"] += f"{oid} = {value}"
    client_ip = snmp_trap["source_address"]
    data = snmp_trap["message"]
    try:
        discordURL = os.environ["DISCORDURL"]
        webhook = DiscordWebhook(
            url=discordURL)
        embed = DiscordEmbed(
            title='SNMP Event', description=f'The following network device had a SNMP event', color='ab52fe')
        embed.set_author(name='NetBot',
                         icon_url='https://avatars0.githubusercontent.com/u/14542790')
        embed.set_footer(text='Network SNMP Event')
        embed.set_timestamp()
        embed.add_embed_field(
            name='Device', value=client_ip)
        embed.add_embed_field(
            name='Trap OID', value=snmp_trap["module_id"])
        embed.add_embed_field(
            name='Message', value=data, inline=False)
        webhook.add_embed(embed)
        webhook.execute()
        mongoURL = os.environ["MONGOURL"]
        snmp_trap["created_at"] = datetime.utcnow()
        client = MongoClient(f"mongodb://{mongoURL}/")
        logs = client["snmp"]
        source_address = snmp_trap["source_address"]
        log_table = logs[source_address]
        result = log_table.insert_one(snmp_trap)
        if result.acknowledged != True:
            print("Could not upload SNMP trap to DB")

        print(f"Posted to DB with id {result.inserted_id}\n{snmp_trap}")
    except Exception as e:
        print(e)


ntfrcv.NotificationReceiver(snmpEngine, cbFun)

snmpEngine.transportDispatcher.jobStarted(1)

try:
    snmpEngine.transportDispatcher.runDispatcher()
except:
    snmpEngine.transportDispatcher.closeDispatcher()
    raise
