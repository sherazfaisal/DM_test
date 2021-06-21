import os
import asyncio
import threading
from six.moves import input
import json
import time
import sys
from c2d import iothub_send_video_source

from azure.iot.device import IoTHubDeviceClient as ClientConnect
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message
from azure.iot.device import MethodResponse
 
SEND_MESSAGE = False

async def listen():
    global SEND_MESSAGE
    # The connection string for your device.
    conn_str = "HostName=IoTHWLabs.azure-devices.net;DeviceId=edge-test-device;SharedAccessKey=yOlOAk/OBHLX3Ty2cwGxJ1+KxGxc+uTqKBMTgqotorg="
    # The client object is used to interact with your Azure IoT hub.
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)
 
    # connect the client.
    await device_client.connect()
  
    async def generic_method_listener(device_client):
        while True:
            print("Listening for new messages")
            method_request = (
                await device_client.receive_method_request("video_source")
            )  # Wait for unknown method calls
            payload = {"result": False, "data": "executed_successfully"}  # set response payload
            status = 400  # set return status code
            print("executed video_source..")
            method_response = MethodResponse.create_from_method_request(
                method_request, status, payload
            )
            await device_client.send_method_response(method_response)  # send response
            payload = method_request.payload
            source = json.loads(payload)
            iothub_send_video_source(source['source'])
            #with open('video_source.json', 'w') as outfile:
            #    json.dump(source, outfile)
            
    # define behavior for halting the application
    def stdin_listener():
        global SEND_MESSAGE
        while True:
            if SEND_MESSAGE: break
            pass
 
    # Schedule tasks for Method Listener
    listeners = asyncio.gather( generic_method_listener(device_client))
 
    # Run the stdin listener in the event loop
    loop = asyncio.get_running_loop()
    user_finished = loop.run_in_executor(None, stdin_listener)
 
    # Wait for user to indicate they are done listening for method calls
    await user_finished
 
    # Cancel listening
    listeners.cancel()
 
    # Finally, disconnect
    await device_client.disconnect()

    time.sleep(15)

    return

    
def main():
    global SEND_MESSAGE
    while True:
        asyncio.run(listen())
        SEND_MESSAGE= False

def send_to_iot_hub(text):

    global SEND_MESSAGE
    try:
        CONNECTION_STRING = "HostName=IoTHWLabs.azure-devices.net;DeviceId=edge-test-device;SharedAccessKey=yOlOAk/OBHLX3Ty2cwGxJ1+KxGxc+uTqKBMTgqotorg="
        CLIENT = ClientConnect.create_from_connection_string(CONNECTION_STRING)
        message = Message(text['source'])
        CLIENT.send_message(message)
        print ("Message '{}' successfully sent".format(text))
        SEND_MESSAGE = True
    except: pass


if __name__ == "__main__":
    main()