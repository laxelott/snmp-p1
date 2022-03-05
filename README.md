# Practica 1 SNMP

## Objetivos
- [x] Implementar la arquitectura básica del protocolo SNMP
- [x] Implementar la comunicación (intercambio de mensajes) entre el agente y el gestor usando SNMP
- [x] Implementar la persistencia de información de una manera eficiente
- [x] Generar reportes para controlar y vigilar los agentes
- [x] Implementar un modelo de administración de red

---
## Requerimientos

### **Requerimientos para monitorear rrd**
1. Instalar paquetes rrd
	sudo apt-get install librrd-dev libpython3-dev
2. Instalar librería de python
	pip3 install rrdtool

### **Requerimientos para generar reporte PDF**
1. Instalar wkhtmltopdf
	sudo apt-get install wkhtmltopdf
2. Instalar librería de python
	pip3 install pdfkit
	
---

## Módulo 1
El menú deberá de tener el numero de dispositivos y desplegar los siguientes submenús:

### **Agregar dispositivo**
Para agregar dispositivo, se deberá indicar:

1. Nombre de host (dirección)
2. Versión SNMP
3. Nombre de la comunidad
4. Puerto

### **Eliminar dispositivo**
Listar y eliminar dispositivos registrados

### **Consultar dispositivo**
Con la siguiente información: 

1. Nombre del dispositivo
2. Nombre, versión y logo del sistema operativo
3. Ubicación geográfica
4. Tiempo de actividad desde el último reinicio
5. Número de interfaces de red
6. Estado administrativo y descripción de máximo 5 interfaces


### **Reporte de información del dispositivo**
Genera un documento PDF que muestra el resultado de la monitorización de un dispositivo en una ventana de tiempo.  
Para esto el usuario especificará un agente y una ventana de tiempo con la siguiente estructura:

1. Encabezado  
2. Información del sistema:
	* Nombre
	* Versión y logo del sistema operativo
	* Ubicación geográfica
	* Numero de interfaces de red
	* Tiempo de actividad desde el ultimo reinicio
	* Comunidad
	* IP  
3. Gráficas  
	**Las gráficas serán del bloque 3**
	1. Mensajes ICMP echo que ha enviado el agente
	2. Mensajes de respuesta ICMP que ha enviado el agente
	3. Mensajes ICMP que ha recibido el agente