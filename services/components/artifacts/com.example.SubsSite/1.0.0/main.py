import json
import os
import time
import calendar
import random
import uuid


import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    IoTCoreMessage,
    QOS,
    SubscribeToIoTCoreRequest
)


from stream_manager import (
    AssetPropertyValue,
    ExportDefinition,
    IoTSiteWiseConfig,
    MessageStreamDefinition,
    PutAssetPropertyValueEntry,
    Quality,
    ResourceNotFoundException,
    StrategyOnFull,
    StreamManagerClient,
    TimeInNanos,
    Variant,
    StreamManagerException,
)

from stream_manager.util import Util


from awscrt.io import (
    ClientBootstrap,
    DefaultHostResolver,
    EventLoopGroup,
    SocketDomain,
    SocketOptions,
)
from awsiot.eventstreamrpc import Connection, LifecycleHandler, MessageAmendment

TIMEOUT = 10



def createSWEntry(propertyAlias, variant):
    time_in_nanos = TimeInNanos(
        time_in_seconds=calendar.timegm(time.gmtime()) - random.randint(0, 60), offset_in_nanos=random.randint(0, 10000)
    )
    asset = [AssetPropertyValue(value=variant, quality=Quality.GOOD, timestamp=time_in_nanos)]
    return PutAssetPropertyValueEntry(entry_id=str(uuid.uuid4()), property_alias=propertyAlias, property_values=asset)


try:
    stream_name = "TemperatureHumidityStream"
    streamClient = StreamManagerClient()

    try:
        streamClient.delete_message_stream(stream_name=stream_name)
    except ResourceNotFoundException:
        pass
    exports = ExportDefinition(
        iot_sitewise=[IoTSiteWiseConfig(identifier="IoTSiteWiseExport" + stream_name, batch_size=5)]
    )
    streamClient.create_message_stream(
        MessageStreamDefinition(
            name=stream_name, strategy_on_full=StrategyOnFull.OverwriteOldestData, export_definition=exports
        )
    )
    print("Now going to start writing IoTSiteWiseEntry to the stream")
except StreamManagerException as e:
    print(e)
    print(type(e))

class IPCUtils:
    def connect(self):
        elg = EventLoopGroup()
        resolver = DefaultHostResolver(elg)
        bootstrap = ClientBootstrap(elg, resolver)
        socket_options = SocketOptions()
        socket_options.domain = SocketDomain.Local
        amender = MessageAmendment.create_static_authtoken_amender(
            os.getenv("SVCUID"))
        hostname = os.getenv(
            "AWS_GG_NUCLEUS_DOMAIN_SOCKET_FILEPATH_FOR_COMPONENT")
        connection = Connection(
            host_name=hostname,
            port=8033,
            bootstrap=bootstrap,
            socket_options=socket_options,
            connect_message_amender=amender,
        )
        self.lifecycle_handler = LifecycleHandler()
        connect_future = connection.connect(self.lifecycle_handler)
        connect_future.result(TIMEOUT)
        return connection


ipc_utils = IPCUtils()
connection = ipc_utils.connect()
ipc_client = client.GreengrassCoreIPCClient(connection)


class StreamHandler(client.SubscribeToIoTCoreStreamHandler):
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: IoTCoreMessage) -> None:
        message = str(event.message.payload, "utf-8")
        topic = str(event.message.topic_name)
        data = json.loads(message)

        if "value" in data:
            variant = Variant(double_value=float(data["value"]))

            siteWiseTopic = "/temperature/celsius"
            if topic == 'RaspberryPi1/sensor/temperature':
                siteWiseTopic = "/temperature/celsius"
            elif topic == 'RaspberryPi1/sensor/humidity':
                siteWiseTopic = "/humidity/percentage"

            try:
                print("Appending new IoTSiteWiseEntry to stream")
                streamClient.append_message(stream_name, Util.validate_and_serialize_to_json_bytes(createSWEntry(siteWiseTopic, variant)))
            except StreamManagerException as e:
                print(e)
                print(type(e))

    def on_stream_error(self, error: Exception) -> bool:
        return True

    def on_stream_closed(self) -> None:
        pass


topic = "RaspberryPi1/sensor/#"
qos = QOS.AT_MOST_ONCE

request = SubscribeToIoTCoreRequest()
request.topic_name = topic
request.qos = qos
handler = StreamHandler()
operation = ipc_client.new_subscribe_to_iot_core(handler)
future = operation.activate(request)
future.result(TIMEOUT)


while True:
    time.sleep(1)

operation.close()
