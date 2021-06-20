from main import livestream
import os
import asyncio
import threading
from six.moves import input
import json
from main import livestream
from azure.iot.device.aio import IoTHubDeviceClient
#from azure.iot.device import Message
from send_iothub import send_to_iot_hub
from azure.iot.device import MethodResponse
 
async def listen():
    # The connection string for your device.
    conn_str = "HostName=IoTHWLabs.azure-devices.net;DeviceId=edge-test-device;SharedAccessKey=yOlOAk/OBHLX3Ty2cwGxJ1+KxGxc+uTqKBMTgqotorg="
    # The client object is used to interact with your Azure IoT hub.
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)
 
    # connect the client.
    await device_client.connect()
  
    async def generic_method_listener(device_client):
        while True:
            method_request = (
                await device_client.receive_method_request("video_source")
            )  # Wait for unknown method calls
            payload = {"result": True, "data": "executed_successfully"}  # set response payload
            status = 400  # set return status code
            print("executed video_source..")
            method_response = MethodResponse.create_from_method_request(
                method_request, status, payload
            )
            await device_client.send_method_response(method_response)  # send response
            payload = method_request.payload
            source = json.loads(payload)
            send_to_iot_hub(source['source'])
            #with open('video_source.json', 'w') as outfile:
            #    json.dump(source, outfile)
            
    # define behavior for halting the application
    def stdin_listener():
        while True:
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

def main():
    asyncio.run(listen())

if __name__ == "__main__":
    main()
    


