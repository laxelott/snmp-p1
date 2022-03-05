import os
import time
from device import snmpDevice
from getSNMP import consultaSNMP
import multiprocessing
import rrdtool

# Things to monitor:
# ICMP echo out requests: 1.3.6.1.2.1.5.21.0
# ICMP echo out responses: 1.3.6.1.2.1.5.22.0
# ICMP in messages: 1.3.6.1.2.1.5.1.0
def monitor_device(device: snmpDevice, rrdFile: str):
    while 1:
        if not device.online:
            device.snmp_check_status()
        
        if device.online: 
            icmpEchoOutRequests = int(device.snmpget("1.3.6.1.2.1.5.21.0"))
            icmpEchoOutResponses = int(device.snmpget("1.3.6.1.2.1.5.22.0"))
            icmpInMessages = int(device.snmpget("1.3.6.1.2.1.5.1.0"))

            valor = (
                "N:"
                + str(icmpEchoOutRequests)
                + ":"
                + str(icmpEchoOutResponses)
                + ":"
                + str(icmpInMessages)
            )
            rrdtool.update(rrdFile, valor)
            # rrdtool.dump(rrdFile,'archivo?.xml')
        
        time.sleep(3)


class rrdDB:
    processes: dict

    def __init__(self):
        self.processes = {}

    def create_graph(self, device: snmpDevice):
        rrdFile = f"./rrd/{device.local_host}.rrd"
        tiempo_inicial = int(time.time()) - 120

        # Set graph's timezone
        os.environ["TZ"] = "America/Mexico_City"

        rrdtool.graph(
            f"./html/img/{device.local_host}-graph-1.png",
            "--start",
            str(tiempo_inicial),
            "--end",
            "N",
            "--vertical-label=Mensajes",
            "--title=Mensajes ICMP Echo que ha enviado el agente",
            f"DEF:outres={rrdFile}:outres:AVERAGE",
            "LINE3:outres#0000FF:ICMP Echo Response enviados",
        )
        rrdtool.graph(
            f"./html/img/{device.local_host}-graph-2.png",
            "--start",
            str(tiempo_inicial),
            "--end",
            "N",
            "--vertical-label=Mensajes",
            "--title=Mensajes ICMP Echo Response que ha enviado el agente",
            f"DEF:outreq={rrdFile}:outreq:AVERAGE",
            "LINE3:outreq#FF0000:ICMP Echo Requests enviados",
        )
        rrdtool.graph(
            f"./html/img/{device.local_host}-graph-3.png",
            "--start",
            str(tiempo_inicial),
            "--end",
            "N",
            "--vertical-label=Mensajes",
            "--title=Mensajes ICMP que ha recibido el agente",
            f"DEF:inmess={rrdFile}:inmess:AVERAGE",
            "LINE3:inmess#00FF00:ICMP Messages recibidos",
        )

    def add_device(self, device: snmpDevice):
        rrdFile = f"./rrd/{device.local_host}.rrd"
        error = False

        # Only create the db file if it doesn't exist
        if not os.path.exists(rrdFile):
            error = rrdtool.create(
                rrdFile,
                "--start",
                "N",
                "--step",
                "5",
                "DS:outreq:COUNTER:30:U:U",
                "DS:outres:COUNTER:30:U:U",
                "DS:inmess:COUNTER:30:U:U",
                "RRA:AVERAGE:0.5:2:12",  # Holds 2 mins of information
            )

        if error:
            rrdtool.error()
        else:
            # Create and start monitoring thread
            process = multiprocessing.Process(
                target=monitor_device, args=(device, rrdFile)
            )
            process.start()

            # Save monitoring thread
            self.processes[rrdFile] = process

    def remove_device(self, device: snmpDevice):
        rrdFile = f"./rrd/{device.local_host}.rrd"

        # Close the monitoring thread
        self.processes[rrdFile].terminate()

        # Delete the rrd file
        os.remove(rrdFile)
        
        # Remove the file entry
        del self.processes[rrdFile]

    def info_device(self, device):
        rrdFile = f"./rrd/{device.local_host}.rrd"
        return self.processes[rrdFile].is_alive()

    def terminate_all(self):
        for key in self.processes:
            self.processes[key].terminate()