# python snmp trap receiver
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
from pysnmp.smi import builder, view
from pysnmp import hlapi

snmpEngine = engine.SnmpEngine()

TrapAgentAddress = '0.0.0.0'  # Trap listerner address
Port = 162  # trap listerner port

print("Agent is listening SNMP Trap on " +
      TrapAgentAddress+" , Port : " + str(Port))
print('--------------------------------------------------------------------------')
config.addTransport(
    snmpEngine,
    udp.domainName + (1,),
    udp.UdpTransport().openServerMode((TrapAgentAddress, Port))
)

# Configure community here
config.addV1System(snmpEngine, 'cs1', 'cs1')


def cbFun(snmpEngine, stateReference, contextEngineId, contextName,
          varBinds, cbCtx):
    print("Received new Trap message")
    for name, val in varBinds:
        print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))


ntfrcv.NotificationReceiver(snmpEngine, cbFun)

snmpEngine.transportDispatcher.jobStarted(1)

try:
    snmpEngine.transportDispatcher.runDispatcher()
except:
    snmpEngine.transportDispatcher.closeDispatcher()
    raise

# iso(1) identified-organization(3) dod(6) internet(1) snmpV2(6) snmpModules(3) snmpCommunityMIB(18) snmpCommunityMIBObjects(1) snmpTrapAddress(3)
# iso(1) identified-organization(3) dod(6) internet(1) snmpV2(6) snmpModules(3) snmpCommunityMIB(18) snmpCommunityMIBObjects(1) snmpTrapCommunity(4)
# Received new Trap message
# 1.3.6.1.2.1.1.3.0 = 217340 sysUpTimeInstance
# 1.3.6.1.6.3.1.1.4.1.0 = 1.3.6.1.2.1.17.0.2 topologyChange NOTIFICATION-TYPE
# 1.3.6.1.6.3.18.1.3.0 = 10.0.5.21 Trap Address
# 1.3.6.1.6.3.18.1.4.0 = cs1 Community String
# 1.3.6.1.6.3.1.1.4.3.0 = 1.3.6.1.2.1.17 dot1dBridge MODULE-IDENTITY
