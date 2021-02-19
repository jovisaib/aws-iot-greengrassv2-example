# Introducción a AWS Greengrass V2



### Resumen
Este repositorio contiene el código y documentación para hacer una introducción a Greengrass V2.


Se puede dividir el ecosistema de esta introducción en 3 componentes:
- Servicio con que con un sensor DHT11 toma la humedad y temperatura de la sala
- Servidor básico de OPC-UA
- Core de Greengrass V2 y sus respectivos componentes


Este repositorio asume que todo el ecosistema se encuentra dentro de una misma Raspberry Pi, pero podría configurarse fácilmente para otras topologías.


Ademas de los SDK indispensables de AWS se han usado las siguientes librerÍas de terceros.

- __[python-opcua](https://github.com/FreeOpcUa/python-opcua/)__ - Free OPC UA Libreria en python 
- __[Adafruit_Python_DHT](https://github.com/adafruit/Adafruit_Python_DHT)__ - LibrerÍa de Adafruit(c) para DHT.
***


### Caso de uso con humedad y temperatura

Representado con un thing, existe un servicio en systemd que recoge los datos de los sensores y los publica en el MQTT de IoT Core.

Por otra parte, desde Greengrass V2, existen dos componentes que cooperan para exportar esa información a SiteWise, son los siguientes:

- **com.example.SubsSite**: Es un componente propio que en primer lugar se suscribe al MQTT de IoT Core para recibir información sobre la temperatura y humedad. Despues filtra esa información y la publica en el Stream encargado de exportar a distintos servicios en la nube de AWS, en este caso SiteWise.

- **aws.greengrass.StreamManager**: Es un servicio publico de Greengrass y permite crear un Stream de datos a partir de la configuración proporcionada (tamaño de buffer, ...). Además mantiene la integridad de los datos incluso si el Greengrass Core pierde la conectividad.


Para poder ver en tiempo real la información sobre la temperatura y humedad se ha usado la siguiente topología:


![Humidity & Temperature Sensor Diagram](/assets/thsensor.png)

Apuntar que por razones didácticas se ha querido pasar por tanto el MQTT de IoT Core como por el Core de Greengrass V2, pero podría tener un recorrido más simple.
***


### Caso de uso con un servidor OPC UA

De nuevo cooperan dos componentes:

- **com.example.OPCUAstreamer**: Este componente propio hace la función de conector a OPC UA, con el añadido de que publica la información en un Stream y este exporta a SiteWise. Esta información sobre el destino de la exportación también se indica en el propio componente customizado.

- **aws.greengrass.StreamManager**: Se usa el mismo servicio de Streams para publicar y exportar a los servicios en la nube de AWS, en este caso la herramienta de activos IoT SiteWise.



El siguiente diagrama muestra la topología usada para que a traves de Greengrass, se pueda visualizar en tiempo real la única variable que tiene el servidor simple de OPC UA que se ha montado:


![OPC UA Diagram](/assets/opcuadiagram.png)
***


### Visualización

IoT SiteWise ha sido la herramienta de recopilación de datos que he escogido para despues, tener la capacidad de conectarlo con distintos proveedores de Dashboards.

Considero que IoT SiteWise es una herramienta muy adecuada para estos casos de uso porque la abstracción que hace de Modelos->Activos es ideal para ecosistemas IoT.

SiteWise te permite visualizar los distintos activos que estamos actualizando con los Streams y también proporciona herramientas drag & drop para montar dashboards intuitivos.

![OPC-UA server in SiteWise](/assets/opcua-viz.png)

IoT SiteEWise te permite conectar con Grafana, y más específicamente el servicio de AWS Grafana Managed Service, que hace que esta adaptación con SiteWise sea muy directa (aunque se encuentra en fases Beta y de momento hay que pedir una preview que dan fácilmente).
***