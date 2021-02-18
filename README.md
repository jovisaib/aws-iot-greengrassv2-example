# Introducción a Greengrass V2


Este repositorio contiene el código y documentación para hacer una introducción a Greengrass V2.


Se puede dividir el ecosistema de esta introducción en 3 componentes:
- Servicio con que con un sensor DHT11 toma la humedad y temperatura de la sala
- Servidor básico de OPC-UA
- Core de Greengrass V2 y sus respectivos componentes


Este repositorio asume que todo el ecosistema se encuentra dentro de una misma Raspberry Pi, pero podría configurarse facilmente para otras topologías.


Ademas de los SDK indispensables de AWS se han usado las siguientes librerias de terceros.

Para crear el servidor que simula OPC-UA se ha usado la libreria para Free OPC-UA en python:
https://github.com/FreeOpcUa/python-opcua/

Para recoger información del sensor DHT se ha usado la libreria de Adafruit.



![Humidity & Temperature Sensor Diagram](/assets/thsensor.png)

![OPC UA Diagram](/assets/opcuadiagram.png)

![OPC-UA server in SiteWise](/assets/opcua-viz.png)