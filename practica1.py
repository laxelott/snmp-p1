import datetime
import math
import os
import shutil
from jsonDB import jsonDB
from device import snmpDevice
from rrdDB import rrdDB
import pdfkit

# TODO
# Imprimir menu inicial
# Agregar dispositivo
# Eliminar dispositivo
# Generar reporte PDF
print("Checando estatus de los agentes...")
deviceDB = jsonDB("./devices.json")
rrdFileDB = rrdDB()

# Agregar todos los dispositivos a RRD
print("Generando los archivos RRD...")
for device in deviceDB.devices:
    rrdFileDB.add_device(device)


def menu():
    clear()

    while True:
        print("--- Práctica 1 ---")
        print(f"Número de dispositivos: {len(deviceDB.devices)}")
        print("")
        dispositivos()
        print("")
        print("Elige una opción:")
        print("1 - Agregar dispositivo")
        print("2 - Eliminar dispositivo")
        print("3 - Consultar dispositivo")
        print("4 - Generar reporte")
        print("5 - Recargar estatus")
        print("6 - Salir")

        opcion = input("->")
        print("\n\n")
        if opcion == "1":
            clear()
            agregar_dispositivo()
            clear()
        elif opcion == "2":
            clear()
            eliminar_dispositivo()
            clear()
        elif opcion == "3":
            clear()
            consultar_dispositivo()
            clear()
        elif opcion == "4":
            clear()
            generar_reporte()
            clear()
        elif opcion == "5":
            print("Checando estatus de los agentes...", end="\r")
            recargar_estatus()
            clear()
        elif opcion == "6":
            deviceDB.save_file()
            rrdFileDB.terminate_all()
            exit()
        else:
            clear()
            print("Opción errónea!")


def dispositivos(index=False, online=False):
    formatLength = 16
    length = formatLength
    num = 3

    devices = deviceDB.devices

    for i, device in enumerate(devices):
        # Obtener el registro más largo
        if (length - formatLength) < len(device.local_host):
            length = formatLength + len(device.local_host)
        elif (length - formatLength) < len(device.local_version):
            length = formatLength + len(device.local_version)
        elif (length - formatLength) < len(device.local_community):
            length = formatLength + len(device.local_community)

    i = 0
    num = min(len(devices) - i, num)
    while i < len(devices):
        for j in range(num):
            print(("|" + ("-" * (length - 2)) + "|"), end="")
        print("")

        if index:
            for j in range(num):
                print(f"|-{'Index:':<12}{(i+j):<{length - formatLength}}-|", end="")
            print("")

        for j in range(num):
            print(
                f"|-{'Host:':<12}{devices[i+j].local_host:<{length - formatLength}}-|",
                end="",
            )
        print("")

        for j in range(num):
            print(
                f"|-{'Version:':<12}v{devices[i+j].local_version:<{length - formatLength-1}}-|",
                end="",
            )
        print("")

        for j in range(num):
            print(
                f"|-{'Community:':<12}{devices[i+j].local_community:<{length - formatLength}}-|",
                end="",
            )
        print("")

        for j in range(num):
            status = "up" if devices[i + j].online else "down"
            print(f"|-{'Status:':<12}{status:<{length - formatLength}}-|", end="")
        print("")

        for j in range(num):
            devices[i + j].snmp_get_inter_number()
            print(
                f"|-{'Interfaces:':<12}{devices[i+j].snmp_inter_number:<{length - formatLength}}-|",
                end="",
            )
        print("")

        for j in range(num):
            print(("|" + ("-" * (length - 2)) + "|"), end="")
        print("")

        # num será el restante de los elementos
        i = i + num
        num = min(len(devices) - i, num)


def agregar_dispositivo():
    print("-- Agregar dispositivo:")

    while True:
        host = input("Inserta el host del nuevo dispositivo: ")
        if host == "":
            print("El host no puede estar vacío!")
        else:
            break

    version = input("Inserta la versión del nuevo dispositivo: ")
    community = (
        input("Inserta la comunidad del nuevo dispositivo (vacío para 'public'): ")
        or "public"
    )

    while True:
        device = snmpDevice(host=host, version=version, community=community)

        if deviceDB.add_device(device):
            deviceDB.save_file()
            rrdFileDB.add_device(device)
            break
        else:
            print("ERROR! Host ya existe...")
            host = input("Inserta nuevo host:")


def eliminar_dispositivo():
    print("-- Eliminar dispositivo:")
    dispositivos(index=True)
    index = (
        input("Inserta el indice del dispositivo a eliminar (vacío para cancelar): ")
        or False
    )

    if not index:
        return
    else:
        if index.isdigit():
            rrdFileDB.remove_device(deviceDB.devices[int(index)])
            deviceDB.remove_device_index(int(index))

            deviceDB.save_file()


def consultar_dispositivo():
    print("-- Consultar dispositivo:")
    dispositivos(index=True)
    print("")
    index = (
        input("Inserta el indice del dispositivo a consultar (vacío para cancelar): ")
        or False
    )

    if not index:
        return
    else:
        if index.isdigit():
            device = deviceDB.devices[int(index)]

            if device.online:
                maxInterfaces = int(
                    input(
                        "Inserta el numero máximo de interfaces a obtener (vacío para 5): "
                    )
                    or 5
                )
                device.snmp_get_data()

                print(
                    "RRD Monitoring: ", "ON" if rrdFileDB.info_device(device) else "OFF"
                )
                print(f"SNMP Name: {device.snmp_name}")
                print(f"SNMP OS: {device.snmp_os} v{device.snmp_os_version}")
                print(f"SNMP Location: {device.snmp_location}")
                print(f"SNMP Up Time: {device.snmp_time}")
                print(f"SNMP Interface Number: {device.snmp_inter_number}")
                print("SNMP Interfaces:")

                print(f"Obteniendo interfaces...", end="\r")

                # Mostrar el estado de maximo 5 interfaces
                device.get_interface_info(max_interfaces=maxInterfaces)
                print("                      ", end="\r")

                for i, interface in enumerate(device.interfaces):
                    status = (
                        "up"
                        if interface["admin"] == 1
                        else "down"
                        if interface["admin"] == 2
                        else "testing"
                        if interface["admin"] == 3
                        else "unknown"
                    )

                    if interface["descr"][0:2] == "0x":
                        interface["descr"] = bytes.fromhex(
                            interface["descr"][2:]
                        ).decode("ASCII")

                    print("\tInterface #" + str(i + 1) + ":")
                    print("\t\tAdmin Status:", status)
                    print("\t\tDescription:", interface["descr"])

            else:
                print(
                    "RRD Monitoring: ", "ON" if rrdFileDB.info_device(device) else "OFF"
                )
                print("No se puede consultar un dispositivo desconectado!")

            input("Presiona ENTER para continuar...")


def generar_reporte():
    print("-- Generar reporte:")
    dispositivos(index=True)
    index = (
        input(
            "Inserta el indice del dispositivo para generar reporte (vacío para cancelar): "
        )
        or False
    )

    if not index:
        return
    else:
        if index.isdigit():
            device = deviceDB.devices[int(index)]

            if device.online:
                print("Obteniendo información...")
                device.snmp_get_data()

                print("Generando gráficas...")
                rrdFileDB.create_graph(device)

                template = ""
                htmlFile = f"./html/{device.local_host}.html"
                pdfFile = f"./reportes/{device.local_host}.pdf"

                print("Generando pdf...")
                # Load template
                with open("./html/template.html", "r") as f:
                    template = f.read()

                osIcon = (
                    "windows-brands"
                    if device.snmp_os == "Windows"
                    else "linux-brands"
                    if device.snmp_os == "Linux"
                    else "question-circle-solid"
                )

                # Format uptime
                device.snmp_time = math.floor(device.snmp_time / 100)
                uptime = datetime.timedelta(seconds=device.snmp_time)
                uptime = "{:0>8}".format(str(uptime))
                uptime = f"{device.snmp_time}s ({uptime})"

                # Fill template with info
                template = template.replace(r"%name%", device.snmp_name)
                template = template.replace(r"%os-name%", device.snmp_os)
                template = template.replace(r"%os-ver%", device.snmp_os_version)
                template = template.replace(r"%os-icon%", osIcon)
                template = template.replace(r"%location%", device.snmp_location)
                template = template.replace(
                    r"%interface-number%", str(device.snmp_inter_number)
                )
                template = template.replace(r"%uptime%", uptime)
                template = template.replace(r"%community%", device.local_community)
                template = template.replace(r"%ip%", device.local_host)

                # Write to html file
                with open(htmlFile, "w+") as f:
                    f.write(template)

                # Convert html file to pdf
                options = {
                    "page-size": "A4",
                    "margin-top": "2cm",
                    "margin-left": "2cm",
                    "margin-right": "2cm",
                    "encoding": "UTF-8",
                }
                pdfkit.from_file(htmlFile, pdfFile, options=options)

                # Delete html file
                os.remove(htmlFile)
                
                # Delete graph images
                shutil.rmtree("./html/img/")
                os.makedirs("./html/img/")
                
                print(f"Reporte generado! Archivo: {os.path.abspath(pdfFile)}")
                input("Presiona ENTER para continuar...")
            else:
                print("No se puede generar reporte de un dispositivo desconectado!")


def recargar_estatus():
    deviceDB.update_status()


def clear():
    os.system("clear")


menu()
