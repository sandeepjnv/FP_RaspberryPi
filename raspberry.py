import cv2
import base64
import time
import os,json
import requests
import serial              
from time import sleep
import sys

def frameToBase64():
    print("Capturing...")
    try:
        # capture frame
        cap =  cv2.VideoCapture(0)
        while cap.isOpened():
            ret ,frame = cap.read()

            # save image
            cv2.imwrite("./data/Frame.jpg", frame)
            break
        
        # terminate frame 
        cap.release()
        cv2.destroyAllWindows()

        # convert image to base64
        with open("data/Frame.jpg", "rb") as image:
            encodedImage = base64.b64encode(image.read())   
            
        return encodedImage
    
    except Exception as e:
        return "Error"

def captureLocation():   
    ser = serial.Serial ("/dev/ttyAMA0")
    gpgga_info = "$GPGGA,"
    GPGGA_buffer = 0
    NMEA_buff = 0

    try:
        received_data = (str)(ser.readline()) #read NMEA string received
        GPGGA_data_available = received_data.find(gpgga_info)   #check for NMEA GPGGA string                
        if (GPGGA_data_available>0):
            GPGGA_buffer = received_data.split("$GPGGA,",1)[1]  #store data coming after "$GPGGA," string
            NMEA_buff = (GPGGA_buffer.split(','))
            nmea_time = []
            nmea_latitude = []
            nmea_longitude = []
            nmea_time = NMEA_buff[0]                    #extract time from GPGGA string
            nmea_latitude = NMEA_buff[1]                #extract latitude from GPGGA string
            nmea_longitude = NMEA_buff[3]               #extract longitude from GPGGA string
            print("NMEA Time: ", nmea_time,'\n')
            lat = (float)(nmea_latitude)
            lat = convert_to_degrees(lat)
            longi = (float)(nmea_longitude)
            longi = convert_to_degrees(longi)
            return (lat,longi)

    except Exception as e:
        return "Error"

def convert_to_degrees(raw_value):
    decimal_value = raw_value/100.00
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - int(decimal_value))/0.6
    position = degrees + mm_mmmm
    position = "%.4f" %(position)
    return position


# runs every 1min
strServerURL = "http://192.168.1.13:5000"
strVehicleID = "1"
strImageFrameAPI = "/raspberry_module/image_frame"
strLocationAPI = "/raspberry_module/location"
while True:
    try:
        # image frame to server
        strEncoded = frameToBase64()
        if strEncoded != "Error":
            # sent to server
            payload = {"str_vehicle_id": strVehicleID, "str_img_frame": str(strEncoded)}  
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            ins_request = requests.post(strServerURL+strImageFrameAPI, data=json.dumps(payload), headers=headers)
            print("Image frame API response :"+ins_request.text)

        # gps to server
        tupLocation = captureLocation()
        if tupLocation != "Error":
            # sent to server
            payload = {"str_vehicle_id" : strVehicleID, "str_latitude" : tupLocation[0], "str_longitude" : tupLocation[1]}  
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            ins_request = requests.post(strServerURL+strLocationAPI, data=json.dumps(payload), headers=headers)
            print("Location API response :"+ins_request.text)

    except Exception as e:
        print(str(e))

    
    time.sleep(30)
