import os

from flask import *
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db as database

import cv2
from PIL import Image
import pytesseract

from mqtt_client import MQTTClient

import sys
sys.path.append("IP/SecurityCamera");
import ccCameraDraft4

app = Flask(__name__);

global firebaseApp;
global firebaseDB;
global lightEventsRef;
global carEventsRef;
global mqttClient;
global LED_HIGH;
global LED_LOW;

def main():
    # All things global should be defined here
    global firebaseApp;
    global firebaseDB;
    global lightEventsRef;
    global carEventsRef;
    global mqttClient;
    global LED_HIGH;
    global LED_LOW;
    cred = credentials.Certificate("mdec-5edc2-firebase-adminsdk-vg9vm-9c5355fe8e.json");
    firebaseApp = firebase_admin.initialize_app(cred);
    firebaseDB = database;
    databaseURL = "https://mdec-5edc2.firebaseio.com/";
    lightEventsRef = database.reference("light/lightEvents", firebaseApp, databaseURL);
    carEventsRef = database.reference("car/carEvents", firebaseApp, databaseURL);

    mqttClient = MQTTClient();
    LED_HIGH = "D1";
    LED_LOW = "D2";


def isCapitalized(c):
    return ord(c) >= 65 and ord(c) <= 90;


def isDigit(c):
    return ord(c) >= 48 and ord(c) <= 57;


def signalCallback(signal, datetimeStr):
    if signal == 0:
        mqttClient.publishData(LED_LOW);
    else:
        mqttClient.publishData(LED_HIGH);

    time, date = datetimeStr.split(" ");
    data = { "date": date, "time": time, "Log": 400, "Event": "Motion"};
    carEventsRef.push(data);


@app.route("/")
def entranceExitDetection():
    # FIXME: Hardcoded Image path
    currentDir = os.path.dirname(os.path.realpath(__file__));
    imgPath = os.path.join(currentDir, "IP/carNumberPlate.jpg");
    img = cv2.imread(imgPath);
    cv2.imshow("Image", img);
    cv2.waitKey(1);

    config = ("-l eng --oem 1 --psm 6");
    result = pytesseract.image_to_string(Image.open(imgPath), config=config);
    carPlateNum = "";
    for c in result:
        if isCapitalized(c) or isDigit(c):
            carPlateNum += c;

    mqttClient.publishData(LED_HIGH);

    data = { "date": "22-09-2018", "time": "08:22:08", "Log": 319, "Carplate": "WPR9070", "Event": "Entry"};
    data["Carplate"] = carPlateNum;
    carEventsRef.push(data);

    return "";


@app.route("/motion")
def analyse_footage():
    ccCameraDraft4.motionDetection(signalCallback);
    return "";


@app.route("/test")
def test():
    currentDir = os.path.dirname(os.path.realpath(__file__));
    filePath = os.path.join(currentDir, "lippy/json_data.txt");
    with open(filePath, "r") as lipFile:
        for Json in lipFile:
            current = Json.rstrip();
            dic = json.loads(current);
            try:
                dic["Event"];
                carEventsRef.push(dic);
            except KeyError:
                lightEventsRef.push(dic);

    return "";


@app.errorhandler(404)
def not_found(error):
    return "404 NOT FOUND!", 404;


@app.errorhandler(405)
def method_not_allowed(error):
    return "405 METHOD NOT ALLOWED", 405


if __name__ == "__main__":
    main();
    app.run();

