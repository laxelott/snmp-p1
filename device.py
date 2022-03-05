from getSNMP import consultaSNMP, onlineSNMP
import re


class snmpDevice:
    online = False

    local_host = ""
    local_version = ""
    local_community = ""

    snmp_name = ""
    snmp_os = ""
    snmp_os_version = ""
    snmp_location = ""
    snmp_inter_number = 0
    snmp_time = 0

    def __init__(self, host: str, version: str, community="public"):
        self.local_host = host
        self.local_version = version
        self.local_community = community

    def snmp_check_status(self):
        self.online = onlineSNMP(self.local_community, self.local_host)

    def snmp_get_name(self):
        if self.online:
            self.snmp_name = self.snmpget("1.3.6.1.2.1.1.5.0")
        
    def snmp_get_location(self):
        if self.online:
            self.snmp_location = self.snmpget("1.3.6.1.2.1.1.6.0")

    def snmp_get_inter_number(self):
        if self.online:
            self.snmp_inter_number = int(self.snmpget("1.3.6.1.2.1.2.1.0"))
        
    def snmp_get_time(self):
        if self.online:
            self.snmp_time = int(self.snmpget("1.3.6.1.2.1.1.3.0"))
        
    def snmp_get_os(self):
        if self.online:
            sysDesc = self.snmpget("1.3.6.1.2.1.1.1.0")

            if sysDesc.find("Windows") != -1:
                self.snmp_os = "Windows"
                self.snmp_os_version = re.search(
                    "Windows Version *([^ ]+) ", sysDesc
                ).group(1)
            elif sysDesc.find("Linux") != -1:
                self.snmp_os = "Linux"
                self.snmp_os_version = re.search("([^ ]+)-generic", sysDesc).group(1)
            else:
                self.snmp_os = "unknown"
                self.snmp_os_version = "unknown"
        

    def snmp_get_data(self):
        if self.online:
            self.snmp_get_os()
            self.snmp_get_name()
            self.snmp_get_time()
            self.snmp_get_location()
            self.snmp_get_inter_number()

            

    def get_interface_info(self, max_interfaces):
        self.interfaces = []

        max_interfaces = min(max_interfaces, self.snmp_inter_number)

        for i in range(max_interfaces):
            self.interfaces.append(
                {
                    "admin": int(self.snmpget("1.3.6.1.2.1.2.2.1.7." + str(i+1))),
                    "descr": self.snmpget("1.3.6.1.2.1.2.2.1.2." + str(i+1)),
                }
            )

    def snmpget(self, oid):
        return consultaSNMP(self.local_community, self.local_host, oid)

    def __str__(self):
        return (
            "SNMP Device: ["
            + self.local_host
            + ":161"
            + '], "'
            + self.local_community
            + '" v'
            + self.local_version
        )
