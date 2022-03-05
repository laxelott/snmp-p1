from pysnmp.hlapi import *

def onlineSNMP(comunidad, host):
    result = True
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(
            SnmpEngine(),
            CommunityData(comunidad),
            UdpTransportTarget((host, 161), timeout=1, retries=1),
            ContextData(),
            ObjectType(ObjectIdentity("1.3.6.1.2.1.1.1.0")), # Información del sistema
        )
    )
    
    if errorIndication:
        result = False
    elif errorStatus:
        result = False
        
    return result

def consultaSNMP(comunidad, host, oid):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(
            SnmpEngine(),
            CommunityData(comunidad),
            UdpTransportTarget((host, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
        )
    )

    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print(
            "%s at %s"
            % (
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex) - 1][0] or "?",
            )
        )
    else:
        for varBind in varBinds:
            varB = " = ".join([x.prettyPrint() for x in varBind])
            resultado = varB.split("=")[1].strip()
        return resultado
