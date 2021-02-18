#!/usr/bin/python
import time
import sys
import Adafruit_DHT
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.core.greengrass.discovery.providers import DiscoveryInfoProvider


myMQTTClient = AWSIoTMQTTClient("RaspiTempAndHumidity") #random key, if another connection using the same key is opened the previous one is auto closed by AWS IOT
myMQTTClient.configureEndpoint("###", 8883)
myMQTTClient.configureCredentials("/opt/thsensor/root-ca.pem", "/opt/thsensor/private.pem.key", "/opt/thsensor/certificate.pem.crt")

myMQTTClient.configureOfflinePublishQueueing(-1) # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2) # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10) # 10 sec
myMQTTClient.configureMQTTOperationTimeout(30) # 5 sec


myMQTTClient.connect()


def readAndPublish():
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(11, 4)

        if temperature != None:
            myMQTTClient.publish(
                topic="RaspberryPi1/sensor/temperature",
                QoS=1,
                payload='{"value": "'+str(float(temperature))+'"}'
            )

        if humidity != None:
            myMQTTClient.publish(
                topic="RaspberryPi1/sensor/humidity",
                QoS=1,
                payload='{"value": "'+str(float(humidity))+'"}'
            )

        print("Temp: {0:0.1f} C  Humidity: {1:0.1f} %".format(temperature, humidity))
        time.sleep(2)


if __name__ == '__main__':
    readAndPublish()

