# Introducción a AWS Greengrass V2


Este repositorio contiene el código y documentación para hacer una introducción a Greengrass V2.


Se puede dividir el ecosistema de esta introducción en 3 componentes:
- Servicio con que con un sensor DHT11 toma la humedad y temperatura de la sala
- Servidor básico de OPC-UA
- Core de Greengrass V2 y sus respectivos componentes


Este repositorio asume que todo el ecosistema se encuentra dentro de una misma Raspberry Pi, pero podría configurarse fÁcilmente para otras topologías.


Ademas de los SDK indispensables de AWS se han usado las siguientes librerÍas de terceros.

Para crear el servidor que simula OPC-UA se ha usado la librerÍa para Free OPC-UA en python:
https://github.com/FreeOpcUa/python-opcua/

Para recoger información del sensor DHT se ha usado la librerÍa de Adafruit.





Para poder ver en tiempo real la información sobre la temperatura y humedad se ha usado la siguiente topologia:
![Humidity & Temperature Sensor Diagram](/assets/thsensor.png)

Notese que por razones didacticas se ha querido pasar por tanto el MQTT de IoT Core como por el Core de Greengrass V2, pero podría tener un recorrido más simple.



El siguiente diagrama muestra la topologia usada para que a traves de Greengrass, se pueda visualizar en tiempo real la unica variable que tiene el servidor simple de OPC UA que se ha montado:
![OPC UA Diagram](/assets/opcuadiagram.png)





Finalmente SiteWise te permite visualizar los distintos activos que estamos actualizando con los Streams.

![OPC-UA server in SiteWise](/assets/opcua-viz.png)

IoT SiteEWise te permite conectar con cualquier proveedor de Dashboards para la visualización como puede ser Grafana, y más especificamente el servicio de AWS Grafana Managed Service, que hace que esta adaptación con SiteWise sea muy directa (se encuentra en fase Beta).
