import sys, time

from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod, CloudToDeviceMethodResult, Twin

CONNECTION_STRING = "HostName=IoTHWLabs.azure-devices.net;SharedAccessKeyName=device;SharedAccessKey=65nt5ey7+Y1hWhmodvSp0yo15kCOQ33r5heJl3UuRI0="
DEVICE_ID = "edge-test-device"

METHOD_NAME = "video_source"
SOURCE_VIDEO_STREAM = input("Input the New Video Stream Souce: ")
METHOD_PAYLOAD = "{\"source\":\""+SOURCE_VIDEO_STREAM+"\"}"
TIMEOUT = 60
WAIT_COUNT = 10

def iothub_devicemethod_sample_run():
    try:
        # Create IoTHubRegistryManager
        registry_manager = IoTHubRegistryManager(CONNECTION_STRING)

        print ( "" )
        print ( "Invoking device to change video stream..." )

        # Call the direct method.
        deviceMethod = CloudToDeviceMethod(method_name=METHOD_NAME, payload=METHOD_PAYLOAD)
        response = registry_manager.invoke_device_method(DEVICE_ID, deviceMethod)

        print ( "" )
        print ( "Successfully invoked the device to change video stream." )

        print ( "" )
        print ( response.payload )
        
        while True:
            press = input("Press Q to exit: ")
            if press.lower()=="q": break
            time.sleep(5)


    except Exception as ex:
        print ( "" )
        print ( "Unexpected error {0}".format(ex) )
        return

    except KeyboardInterrupt:
        print ( "" )
        print ( "IoTHubDeviceMethod sample stopped" )


if __name__ == '__main__':
    print ( "Starting the IoT Hub Service Client DeviceManagement Python sample..." )
    print ( "    Connection string = {0}".format(CONNECTION_STRING) )
    print ( "    Device ID         = {0}".format(DEVICE_ID) )

    iothub_devicemethod_sample_run()

