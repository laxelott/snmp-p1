# Practica 1 SNMP

## Objetivos
* Implementar la arquitectura básica del rptocolo SNMP
* Implementar la comunicación (intercambio de mensajes) entre el agente y el gestor usando SNMP
* Implementar la persistencia de información de una manera eficiente
* Generar reportes para controlar y vigilar los agentes
* Implementar un modelo de administración de red

---

## Módulo 1
El menú deberá de tener los siguientes submenús:

### **Inicio**
Con la siguiente información: 

1. Numero de dispositivos
2. Estado de conectividad
3. Número de interfaces de red
4. Estado administrativo y descripción de interfaces

### **Agregar dispositivo**
Para agregar dispositivo, se deberá indicar:

1. Nombre de host (dirección)
2. Versión SNMP
3. Nombre de la comunidad
4. Puerto

### **Eliminar dispositivo**
Listar y eliminar dispositivos registrados

### **Reporte de información del dispositivo**
Genera un documento PDF que muestra el resultado de la monitorización de un dispositivo en una ventana de tiempo.  
Para esto el usuario especificará un agente y una ventana de tiempo con la siguiente estructura:

1. Encabezado  
2. Información del sistema:
	* Nombre,
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