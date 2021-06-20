
def send_to_iot_hub(text):

    from azure.iot.device import IoTHubDeviceClient as client_connect
    from azure.iot.device import Message as message_send
    CONNECTION_STRING = "HostName=IoTHWLabs.azure-devices.net;DeviceId=edge-test-device;SharedAccessKey=yOlOAk/OBHLX3Ty2cwGxJ1+KxGxc+uTqKBMTgqotorg="
    CLIENT = client_connect.create_from_connection_string(CONNECTION_STRING)
    message = message_send(text)
    CLIENT.send_message(message)
    print ("Message '{}' successfully sent".format(text))



