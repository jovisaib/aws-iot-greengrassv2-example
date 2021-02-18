from awsiot.eventstreamrpc import Connection, LifecycleHandler, MessageAmendment
import uuid
import calendar
import os
import random
import awsiot.greengrasscoreipc.client as client
from opcua import Client
import time

from awscrt.io import (
    ClientBootstrap,
    DefaultHostResolver,
    EventLoopGroup,
    SocketDomain,
    SocketOptions,
)
from stream_manager.util import Util
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
from awsiot.greengrasscoreipc.model import (
    QOS,
    PublishToIoTCoreRequest
)

TIMEOUT = 10


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


try:
    stream_name = "OPCUAStream"
    streamClient = StreamManagerClient()

    try:
        streamClient.delete_message_stream(stream_name=stream_name)
    except ResourceNotFoundException:
        pass
    exports = ExportDefinition(
        iot_sitewise=[IoTSiteWiseConfig(
            identifier="IoTSiteWiseExport" + stream_name, batch_size=5)]
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


def createSWEntry(propertyAlias, variant):
    time_in_nanos = TimeInNanos(
        time_in_seconds=calendar.timegm(time.gmtime()) - random.randint(0, 60), offset_in_nanos=random.randint(0, 10000)
    )
    asset = [AssetPropertyValue(
        value=variant, quality=Quality.GOOD, timestamp=time_in_nanos)]
    return PutAssetPropertyValueEntry(entry_id=str(uuid.uuid4()), property_alias=propertyAlias, property_values=asset)


ipc_utils = IPCUtils()
connection = ipc_utils.connect()
ipc_client = client.GreengrassCoreIPCClient(connection)

opcUAclient = Client("opc.tcp://localhost:4840/freeopcua/server/")

try:
    opcUAclient.connect()
    val = opcUAclient.get_node("ns=2;i=2")


    while True:
        dataValue = val.get_data_value().Value
        value = float(dataValue.Value)
        topic = "OPCUAServer1/test/myVariable"
        qos = QOS.AT_LEAST_ONCE

        request = PublishToIoTCoreRequest()
        request.topic_name = topic
        request.payload = bytes('{"value": "'+str(value)+'"}', "utf-8")
        request.qos = qos
        operation = ipc_client.new_publish_to_iot_core()
        operation.activate(request)
        future = operation.get_response()
        future.result(TIMEOUT)

        variant = Variant(double_value=value)
        siteWiseTopic = "/testvariable/opcua"

        try:
            print("Appending IoTSiteWiseEntry to stream")
            streamClient.append_message(stream_name, Util.validate_and_serialize_to_json_bytes(
                createSWEntry(siteWiseTopic, variant)))
        except StreamManagerException as e:
            print(e)
            print(type(e))

        time.sleep(1)

finally:
    opcUAclient.disconnect()
