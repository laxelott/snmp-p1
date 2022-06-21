import os
import time
from device import snmpDevice
from getSNMP import consultaSNMP
import multiprocessing
import rrdtool


class monitorItem:
    def __init__(self, name: str, address: str, graphTitle: str):
        self.name = name
        self.address = address
        self.graphTitle = graphTitle


monitorItems = {
    # ICMP echo out requests
    "Out Requests": monitorItem(
        "outreq", "1.3.6.1.2.1.5.21.0", "Mensajes ICMP Echo que ha enviado el agente"
    ),
    # ICMP echo out responses
    "Out Responses": monitorItem(
        "outres",
        "1.3.6.1.2.1.5.22.0",
        "Mensajes ICMP Echo Response que ha enviado el agente",
    ),
    # ICMP in messages
    "In Messages": monitorItem(
        "inmess", "1.3.6.1.2.1.5.1.0", "Mensajes ICMP que ha recibido el agente"
    ),
}


def monitor_device(device: snmpDevice, rrdFile: str):
    while 1:
        if not device.online:
            device.snmp_check_status()

        if device.online:
            valor = "N:"

            for key in monitorItems:
                valor += device.snmpget(monitorItems[key].address) + ":"

            valor = valor[:-1]

            rrdtool.update(rrdFile, valor)

        time.sleep(3)


class rrdDB:
    processes: dict

    def __init__(self):
        self.processes = {}

    def create_graphs(self, device: snmpDevice):
        rrdFile = f"./rrd/{device.local_host}.rrd"
        tiempo_inicial = int(time.time()) - 120

        # Set graph's timezone
        os.environ["TZ"] = "America/Mexico_City"

        i = 1
        for key in monitorItems:
            rrdtool.graph(
                f"./html/img/{device.local_host}-graph-{i}.png",
                "--start",
                str(tiempo_inicial),
                "--end",
                "N",
                "--vertical-label=Mensajes",
                f"--title={monitorItems[key].graphTitle}",
                f"DEF:{monitorItems[key].name}={rrdFile}:{monitorItems[key].name}:AVERAGE",
                f"LINE3:{monitorItems[key].name}#0000FF:Mensajes",
            )
            i += 1

    def add_device(self, device: snmpDevice):
        rrdFile = f"./rrd/{device.local_host}.rrd"
        error = False

        # Only create the db file if it doesn't exist
        if not os.path.exists(rrdFile):
            params = []

            for key in monitorItems:
                params.append(f"DS:{monitorItems[key].name}:COUNTER:30:U:U")

            error = rrdtool.create(
                rrdFile,
                "--start",
                "N",
                "--step",
                "5",
                *params,
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
