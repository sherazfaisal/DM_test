from azure.iot.device import IoTHubDeviceClient
import time
import json
MESSAGE_RECIEVED = 0
def recieve_from_cloud():
    global MESSAGE_RECIEVED

    CONNECTION_STRING = "HostName=IoTHWLabs.azure-devices.net;DeviceId=edge-test-device;SharedAccessKey=yOlOAk/OBHLX3Ty2cwGxJ1+KxGxc+uTqKBMTgqotorg="
    CLIENT = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

    while True:
        try:
            MESSAGE = CLIENT.receive_message()
            CAMERA_SOURCE = MESSAGE.data
            print("\nMessage received:")
            print("Data: {}".format(str(MESSAGE.data)))
            MESSAGE_RECIEVED+=1
            source = {"source":str(MESSAGE.data).split('b')[1].split("'")[1]}
            with open('video_source.json', 'w') as outfile:
                json.dump(source, outfile)
            print(MESSAGE.data)

        except: continue 
    while True:
        time.sleep(1000)


recieve_from_cloud()



