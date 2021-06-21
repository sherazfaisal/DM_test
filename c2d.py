import random
import sys
from azure.iot.device import IoTHubDeviceClient
from azure.iot.hub import IoTHubRegistryManager

CONNECTION_STRING = "HostName=IoTHWLabs.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=lp5GJ78EcbwUWcwi5Z5McEGdE4lpHZIReZOVdqnzLjQ="
DEVICE_ID = "edge-test-device"

def iothub_send_video_source(value):
    try:
        # Create IoTHubRegistryManager
        registry_manager = IoTHubRegistryManager(CONNECTION_STRING)

        print('Sending to Device with ID {}'.format(DEVICE_ID))

        registry_manager.send_c2d_message(DEVICE_ID, value)

    except Exception as ex:
        print ( "Unexpected error {0}" % ex )
        return
    except KeyboardInterrupt:
        print ( "IoT Hub C2D Messaging service sample stopped" )

def recieve_from_cloud():

    CONNECTION_STRING = "HostName=IoTHWLabs.azure-devices.net;DeviceId=edge-test-device;SharedAccessKey=yOlOAk/OBHLX3Ty2cwGxJ1+KxGxc+uTqKBMTgqotorg="
    CLIENT = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

    while True:
        try:
            MESSAGE = CLIENT.receive_message()
            CAMERA_SOURCE = MESSAGE.data
            print("\nMessage received:")
            print("Data: {}".format(str(MESSAGE.data)))
            
        except: continue 
    while True:
        time.sleep(1000)


iothub_send_video_source("0")