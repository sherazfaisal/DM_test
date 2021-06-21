import cv2
import time
import json
import imutils
import numpy as np
import datetime
import threading
import asyncio
import os
from six.moves import input
from azure.iot.device import IoTHubDeviceClient, Message
from azure.iot.device import MethodResponse

from imutils.video import FPS 
from imutils.video import VideoStream
from imutils.video import WebcamVideoStream
from imutils.video import FileVideoStream

#----------------------- SSD_INITIALIZATIONS ----------------------#
PROTOTXT_PATH = "./models/SSD_MobileNet_prototxt.txt"
MODEL_PATH = "./models/SSD_MobileNet.caffemodel"
CONFIDENCE_THRESHOLD = 0.7

#--------------------- LIVESTREAM_INITIALIZATIONS------------------#
ENABLE_PERSON_COUNT = True
ENABLE_VEHICLE_COUNT = False
ENABLE_ANIMAL_COUNT = False
CAMERA_SOURCE = 0#"https://192.168.2.131:8080/video"#"http://192.168.137.32:8080/video"#"./test_videos/animals.mp4"
TOTAL_FRAMES = 0
BUFFER_SIZE = 60
FRAMES_TO_SKIP = 6

#------------------------ IOT-HUB INITIALIZATION -------------------- #
RECIEVE_C2D_MESSAGES = True
CONNECTION_STRING = "HostName=IoTHWLabs.azure-devices.net;DeviceId=edge-test-device;SharedAccessKey=yOlOAk/OBHLX3Ty2cwGxJ1+KxGxc+uTqKBMTgqotorg="
SEND_COUNTER_TO_IOT_HUB = True
SEND_AFTER_FRAMES = 30*1 # After 4 seconds
if SEND_COUNTER_TO_IOT_HUB or RECIEVE_C2D_MESSAGES:
    CLIENT = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)


def livestream():

    global TOTAL_FRAMES, MAX_PERSON_COUNT, CAMERA_SOURCE, VS

    if RECIEVE_C2D_MESSAGES:
        with open('video_source.json','r') as json_file:
            CAMERA_SOURCE = json.load(json_file)['source']

    if not((ENABLE_PERSON_COUNT or ENABLE_ANIMAL_COUNT or ENABLE_VEHICLE_COUNT)):
        print('Please enable only one of the following modes. \n 1. PERSON_COUNT \n 2. VEHICLE_COUNT \n 3. ANIMAL_COUNT')
        return
    nn, labels = load_SSD()
    colors = np.random.uniform(0, 255, size=(len(labels["all_labels"]), 3))
    print('[Status] Starting Video Stream...')
    if type(CAMERA_SOURCE) not in [str,int]:
        CAMERA_SOURCE = CAMERA_SOURCE.decode("utf-8") 
    if type(CAMERA_SOURCE)==str and CAMERA_SOURCE.isnumeric(): CAMERA_SOURCE = int(CAMERA_SOURCE)
    if type(CAMERA_SOURCE) == int or ('.mp4' or '.avi') not in CAMERA_SOURCE:
        VS = WebcamVideoStream(src=CAMERA_SOURCE).start()
    else: VS = FileVideoStream(CAMERA_SOURCE).start()
    fps = FPS().start()
    while True:
        try:
            frame = VS.read()
            frame = imutils.resize(frame, width=600)
            cv2.putText(frame, str(time.ctime(time.time())), (10, 15),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            TOTAL_FRAMES+=1
            if (TOTAL_FRAMES % (FRAMES_TO_SKIP+1)) == 0:
                # Process your frame here using algorithm
                blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)

                #Passing Blob through network to detect and predict
                nn.setInput(blob)
                detections = nn.forward()
                counter = show_label_on_frame_and_counter(detections, frame , labels , colors)
            else:
                try: show_label_on_frame_and_counter(detections, frame , labels, colors)
                except: pass
            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break 
            fps.update()
            if RECIEVE_C2D_MESSAGES: 
                with open('video_source.json','r') as json_file:
                    source = json.load(json_file)['source']
                if type(source) not in [str,int]:
                    source = source.decode("utf-8") 
                if type(source)==str and source.isnumeric(): source = int(source)
                if source!=CAMERA_SOURCE:
                    VS.stop()
                    CAMERA_SOURCE = source
                    if type(CAMERA_SOURCE) == int or ('.mp4' or '.avi') not in CAMERA_SOURCE:
                        VS = WebcamVideoStream(src=CAMERA_SOURCE).start()
                    else: VS = FileVideoStream(CAMERA_SOURCE).start()
        except:
            pass 
    fps.stop()
    #if RECIEVE_C2D_MESSAGES: message_listener_thread.join()
    if RECIEVE_C2D_MESSAGES or SEND_COUNTER_TO_IOT_HUB: CLIENT.shutdown()
    print("[Info] Elapsed time: {:.2f}".format(fps.elapsed()))
    print("[Info] Approximate FPS:  {:.2f}".format(fps.fps()))
    cv2.destroyAllWindows()
    VS.stop()

def load_SSD():

    #Initialize Objects and corresponding colors which the model can detect
    all_labels = ["background", "aeroplane", "bicycle", "bird", 
    "boat","bottle", "bus", "car", "cat", "chair", "cow", 
    "diningtable","dog", "horse", "motorbike", "person", "pottedplant", 
    "sheep","sofa", "train", "tvmonitor"]

    animal_labels = ['bird','cat','cow','dog','horse','sheep']
    vehicle_labels = ['bicycle','boat','bus','car','motorbike','train']

    labels = {"all_labels":all_labels,"animal_labels":animal_labels, "vehicle_labels":vehicle_labels}

    #Loading Caffe Model
    print('[Status] Loading Model...')
    nn = cv2.dnn.readNetFromCaffe(PROTOTXT_PATH, MODEL_PATH)

    return nn,labels

def show_label_on_frame_and_counter(detections, frame, labels, colors):

    global TOTAL_FRAMES
    
    (h, w) = frame.shape[:2]
    person_count = 0
    animal_count = 0
    vehicle_count = 0

    #Loop over the detections
    #idxs = [] 
    for i in np.arange(0, detections.shape[2]):

        #Extracting the confidence of predictions
        confidence = detections[0, 0, i, 2]
       
        idx = int(detections[0, 0, i, 1])
        #idxs.append(idx)
        condition_ = None
        if ENABLE_PERSON_COUNT: condition_ = condition_ or labels["all_labels"][idx] == 'person' if condition_!=None else labels["all_labels"][idx] == 'person' 
        if ENABLE_ANIMAL_COUNT: condition_ = condition_ or labels["all_labels"][idx] in labels["animal_labels"] if condition_!=None else labels["all_labels"][idx] in labels["animal_labels"]
        if ENABLE_VEHICLE_COUNT: condition_ = condition_ or labels["all_labels"][idx] in labels["vehicle_labels"] if condition_!=None else labels["all_labels"][idx] in labels["vehicle_labels"] 
        #Filtering out weak predictions
        if condition_ and confidence>CONFIDENCE_THRESHOLD:

            #Extracting bounding box coordinates
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            #Drawing the prediction and bounding box
            label = "{}: {:.2f}%".format(labels["all_labels"][idx], confidence * 100)
            cv2.rectangle(frame, (startX, startY), (endX, endY), colors[idx], 2)

            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(frame, label, (startX, y),cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[idx], 2)

            if ENABLE_PERSON_COUNT and labels["all_labels"][idx] == 'person': person_count+=1 
            if ENABLE_ANIMAL_COUNT and labels["all_labels"][idx] in labels["animal_labels"]: animal_count+=1 
            if ENABLE_VEHICLE_COUNT and labels["all_labels"][idx] in labels["vehicle_labels"]: vehicle_count+=1
    time_ = time.ctime(time.time())        
    if ENABLE_PERSON_COUNT:
        text = "Person Count: "+str(person_count)
        cv2.putText(frame,text, (frame.shape[0]-20,10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[idx], 2)
        if SEND_COUNTER_TO_IOT_HUB and (TOTAL_FRAMES % (SEND_AFTER_FRAMES + 1))==0:send_to_iot_hub(CLIENT,"Datetime: "+time_+"\n"+text)
        #if RECIEVE_MAX_PERSON_COUNT_FIRST and person_count>MAX_PERSON_COUNT: 
        #    print("Alert: PERSON CAPACITY EXCEDED ")
        #    send_to_iot_hub(CLIENT,"Datetime: "+time_+"\n"+"Alert: PERSON CAPACITY EXCEDED")
    if ENABLE_ANIMAL_COUNT:
        text = "Animal count = "+str(animal_count)
        cv2.putText(frame,text, (frame.shape[0]-20,25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[idx], 2)
        if SEND_COUNTER_TO_IOT_HUB and (TOTAL_FRAMES % (SEND_AFTER_FRAMES + 1))==0: send_to_iot_hub(CLIENT,"Datetime: "+time_+"\n"+text)
    if ENABLE_VEHICLE_COUNT:
        text = "Vehicle count = "+str(vehicle_count) 
        cv2.putText(frame,text, (frame.shape[0]-20,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[idx], 2)
        if SEND_COUNTER_TO_IOT_HUB and (TOTAL_FRAMES % (SEND_AFTER_FRAMES + 1))==0: send_to_iot_hub(CLIENT,"Datetime: "+time_+"\n"+text)
        
    return [person_count, animal_count, vehicle_count]

def send_to_iot_hub(client,text):

    message = Message(text)
    client.send_message(message)
    print ("Message '{}' successfully sent".format(text))

def change_video_stream(message):

    global VS, CAMERA_SOURCE
    print("Message recieved to change video stream: "+message)
    CAMERA_SOURCE = message
    if type(CAMERA_SOURCE) not in [str,int]:
        CAMERA_SOURCE = CAMERA_SOURCE.decode("utf-8") 
    if type(CAMERA_SOURCE)==str and CAMERA_SOURCE.isnumeric(): CAMERA_SOURCE = int(CAMERA_SOURCE)
    print("Starting the stream again with a camera source provided..")
    VS.stop()
    if type(CAMERA_SOURCE) == int or ('.mp4' or '.avi') not in CAMERA_SOURCE: VS = VideoStream(CAMERA_SOURCE).start() 
    else: VS = FileVideoStream(CAMERA_SOURCE).start()


if __name__ == "__main__":
    livestream()
