import RPi.GPIO as GPIO
import time

import paho.mqtt.client as mqtt

BuzzerPin = 11  # Raspberry Pi Pin 17-GPIO 17
GLOBAL_STOP = False


def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt


def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    # print("Message received-> " + msg.topic + "\n" + str(msg.payload))  # Print a received msg
    payload = msg.payload.decode('ascii')
    if "decathlon/error" in msg.topic and payload != "":
        error_message(msg)
    elif "decathlon/success" in msg.topic and payload != "":
        success_message(msg)
    elif "stop" in payload:
        off()


def success_message(message):
    payload = message.payload.decode('ascii')
    for i in range(0, 5):
        on()
        time.sleep(0.5)
        off()
        time.sleep(0.1)
        on()
        time.sleep(0.5)
        off()
        time.sleep(0.5)
    print("Success:" + payload)


def error_message(message):
    print("Error: " + str(message.payload))
    for i in range(0, 10):
        on()
        time.sleep(0.5)
        off()
        time.sleep(1)


def setup():
    global BuzzerPin
    GPIO.setmode(GPIO.BOARD)  # Set GPIO Pin As Numbering
    GPIO.setup(BuzzerPin, GPIO.OUT)
    GPIO.output(BuzzerPin, GPIO.LOW)
    client = mqtt.Client("decathlon_buzzer2")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("10.0.1.150")
    print("Listening")
    client.subscribe("decathlon/#")  # Subscribe to the topic “digitest/test1”, receive any messages published on it
    client.loop_forever()


def on():
    GPIO.output(BuzzerPin, GPIO.HIGH)
    pass


def off():
    GPIO.output(BuzzerPin, GPIO.LOW)
    pass


def destroy():
    GPIO.output(BuzzerPin, GPIO.LOW)
    GPIO.cleanup()  # Release resource
    pass


if __name__ == '__main__':  # Program start from here
    try:
        setup()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be executed.
        destroy()
