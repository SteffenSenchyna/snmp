#
# PySNMP MIB module HCNUM-TC (http://snmplabs.com/pysmi)
# ASN.1 source file://mibs/HCNUM-TC.mib
# Produced by pysmi-0.3.4 at Mon Apr  3 04:20:25 2023
# On host Steffens-MacBook-Pro-2.local platform Darwin version 22.4.0 by user steffensenchyna
# Using Python version 3.9.2 (default, Feb  8 2023, 20:24:57) 
#
Integer, OctetString, ObjectIdentifier = mibBuilder.importSymbols("ASN1", "Integer", "OctetString", "ObjectIdentifier")
NamedValues, = mibBuilder.importSymbols("ASN1-ENUMERATION", "NamedValues")
ConstraintsIntersection, ConstraintsUnion, ValueSizeConstraint, SingleValueConstraint, ValueRangeConstraint = mibBuilder.importSymbols("ASN1-REFINEMENT", "ConstraintsIntersection", "ConstraintsUnion", "ValueSizeConstraint", "SingleValueConstraint", "ValueRangeConstraint")
NotificationGroup, ModuleCompliance = mibBuilder.importSymbols("SNMPv2-CONF", "NotificationGroup", "ModuleCompliance")
Bits, ObjectIdentity, mib_2, MibScalar, MibTable, MibTableRow, MibTableColumn, iso, ModuleIdentity, Counter64, Gauge32, MibIdentifier, Integer32, Counter32, IpAddress, TimeTicks, NotificationType, Unsigned32 = mibBuilder.importSymbols("SNMPv2-SMI", "Bits", "ObjectIdentity", "mib-2", "MibScalar", "MibTable", "MibTableRow", "MibTableColumn", "iso", "ModuleIdentity", "Counter64", "Gauge32", "MibIdentifier", "Integer32", "Counter32", "IpAddress", "TimeTicks", "NotificationType", "Unsigned32")
DisplayString, TextualConvention = mibBuilder.importSymbols("SNMPv2-TC", "DisplayString", "TextualConvention")
hcnumTC = ModuleIdentity((1, 3, 6, 1, 2, 1, 78))
hcnumTC.setRevisions(('2000-06-08 00:00',))
if mibBuilder.loadTexts: hcnumTC.setLastUpdated('200006080000Z')
if mibBuilder.loadTexts: hcnumTC.setOrganization('IETF OPS Area')
class CounterBasedGauge64(TextualConvention, Counter64):
    status = 'current'

class ZeroBasedCounter64(TextualConvention, Counter64):
    status = 'current'

mibBuilder.exportSymbols("HCNUM-TC", CounterBasedGauge64=CounterBasedGauge64, ZeroBasedCounter64=ZeroBasedCounter64, PYSNMP_MODULE_ID=hcnumTC, hcnumTC=hcnumTC)
