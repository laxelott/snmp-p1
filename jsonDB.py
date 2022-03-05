import json
import os
from device import snmpDevice

class jsonDB:
    devices: "list[snmpDevice]" = []
    file_path = ""

    def __init__(self, file_path):
        self.file_path = file_path
        self.read_file()

    def read_file(self):
        if os.path.exists(self.file_path):
            with open(self.file_path) as f:
                jsonObject = json.load(f)
                for device in jsonObject["devices"]:
                    snmpDev = snmpDevice(
                        device["host"],
                        device["version"],
                        device["community"],
                    )
                    snmpDev.snmp_check_status()
                    self.devices.append(snmpDev)

    def save_file(self):
        jsonObject = {"devices": []}
        for device in self.devices:
            jsonObject["devices"].append(
                {
                    "host": device.local_host,
                    "version": device.local_version,
                    "community": device.local_community,
                }
            )

        with open(self.file_path, "w+", encoding="utf-8") as f:
            json.dump(jsonObject, f, ensure_ascii=False)

    def update_status(self):
        for i, device in enumerate(self.devices):
            self.devices[i].snmp_check_status()

    def get_device_index(self, host):
        for i, device in enumerate(self.devices):
            if device.local_host == host:
                return i
        return -1

    def get_device(self, host):
        for device in self.devices:
            if device.local_host == host:
                return device
        return -1

    def add_device(self, device: snmpDevice):
        if self.get_device(device.local_host) == -1:
            self.devices.append(device)
            return True
        else:
            return False

    def remove_device_index(self, index):
        del self.devices[index]

    def remove_device(self, host):
        for i, device in enumerate(self.json["devices"]):
            if device["host"] == host:
                self.remove_device_index(i)
                return True
        return False
