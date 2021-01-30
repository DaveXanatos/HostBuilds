import time
import board
import serial
import adafruit_bno055
import zmq

uart = serial.Serial("/dev/serial0")
sensor = adafruit_bno055.BNO055_UART(uart)
#print(chr(27)+'[2j')
print('\033c')
#print('\x1bc')

context = zmq.Context()
print("Connecting to Speech Center")
socket = context.socket(zmq.REQ)
socket.connect("tcp://192.168.1.201:5555") # Send to 5555 to speak
SpeakText = ""
lastSpeakText = ""

def set_voice(msg):
    socket.send_string(msg)
    message = socket.recv().decode('utf-8')

while True:
    try:
        print("\033[0;0H") # [y;xH moves cursor to row y, col x
        print()
        #print("Raw T: ", sensor.temperature, "\033[K")
        #print("Raw A: ", sensor.acceleration[0], sensor.acceleration[1], sensor.acceleration[2], "\033[K")
        #print("Raw M: ", sensor.magnetic[0], sensor.magnetic[1], sensor.magnetic[2], "\033[K")
        #print("Raw g: {:.4f}".format(sensor.gyro[0]), "{:.4f}".format(sensor.gyro[1]), "{:.4f}".format(sensor.gyro[2]), "\033[K")
        eY = round(sensor.euler[0], 4)  #Vertical Axis (Rotation about Y Axis): Startup is ~0.  Righter turn = up from 0; lefter turn is down from 360; viewed from top, 0 to 359.999 clockwise
        eX = round(sensor.euler[1], 4)  #Ear-to-ear axis (Rotation about X Axis):  Startup ~0; more negative is down, more positive is up.
        eZ = round(sensor.euler[2], 4)  #Front to back axis (Rotation about Z axis): Head tilt right is more negative, head tilt left is more positive (degrees)
        print("Raw E: Y: ", eY, " X: ", eX, " Z: ", eZ, "\033[K")
        #print("Raw E: Y: {:.4f}".format(sensor.euler[0]), " X: {:.4f}".format(sensor.euler[1]), " Z: {:.4f}".format(sensor.euler[2]), "\033[K")
        #print("Raw Q: {:.4f}".format(sensor.quaternion[0]), "{:.4f}".format(sensor.quaternion[1]), "{:.4f}".format(sensor.quaternion[2]), "{:.4f}".format(sensor.quaternion[3]), "\033[K")
        #print("Raw L: ", sensor.linear_acceleration[0], sensor.linear_acceleration[1], sensor.linear_acceleration[2], "\033[K")
        #print("Raw G: ", sensor.gravity[0], sensor.gravity[1], sensor.gravity[2], "\033[K")

        if eY >= 350 or  eY <= 10:
            HeadLR = "forward"
        elif eY >10 and  eY <=180:
            HeadLR = "to my right"
        elif eY < 350 and eY >180:
            HeadLR = "to my left"

        if eX >= -10 and eX <= 10:
            HeadUD = "level"
        elif eX < -10:
            HeadUD = "down"
        elif eX > 10:
            HeadUD = "up"

        if eZ >= -10 and eZ <= 10:
            HeadT = "forward"
        elif eZ < -10:
            HeadT = "the right"
        elif eZ > 10:
            HeadT = "the left"

        #print(HeadLR, "\033[K")
        #print(HeadUD, "\033[K")
        #print(HeadT, "\033[K")

        if HeadLR == HeadUD and HeadLR == HeadT:
            SpeakText = "My head is facing Straight Ahead"
        else:
            SpeakText = "My head is facing " + HeadLR + " and " + HeadUD + ".  "
            if HeadT != "forward":
                SpeakText = SpeakText + "My head is also tilted to " + HeadT

        print("C: ", SpeakText, "\033[K")
        print("L: ", lastSpeakText, "\033[K")

        if SpeakText != "" and SpeakText != lastSpeakText:
            set_voice(SpeakText)
            lastSpeakText = SpeakText

        time.sleep(.1)
    except:
        pass
        #print("**** Damn UART read error 7 again - fix this shit! *******\n")
        time.sleep(.5)


#Euler:  (Rotation about vertical axis; rotation about ear-to-ear axis; rotation about front-to-baack axis)
#         Vertical Axis (Rotation about Y Axis): Startup is ~0.  Righter turn = up from 0; lefter turn is down from 360; viewed from top, 0 to 359.999 clockwise
#         Ear-to-ear axis (Rotation about X Axis):  Startup ~0; more negative is down, more positive is up.
#         Front to back axis (Rotation about Z axis): Head tilt right is more negative, head tilt left is more positive (degrees)

#, "{:.4f}".format(sensor.gyro[2]), "{:.4f}".format(sensor.gyro[3])

#The BNO055 can output the following sensor data:
#    Absolute Orientation (Euler Vector, 100Hz)
#    Three axis orientation data based on a 360 degree sphere
#    Absolute Orientation (Quaterion, 100Hz)
#    Four point quaternion output for more accurate data manipulation
#    Angular Velocity Vector (100Hz)
#    Three axis of 'rotation speed' in rad/s
#    Acceleration Vector (100Hz)
#    Three axis of acceleration (gravity + linear motion) in m/s^2
#    Magnetic Field Strength Vector (20Hz)
#    Three axis of magnetic field sensing in micro Tesla (uT)
#    Linear Acceleration Vector (100Hz)
#    Three axis of linear acceleration data (acceleration minus gravity) in m/s^2

#Gravity Vector (100Hz)
#Three axis of gravitational acceleration (minus any movement) in m/s^2
#Temperature (1Hz)
#Ambient temperature in degrees celsius

# Original Code:
        #print("Temperature: {} degrees C".format(sensor.temperature))
        #print("Accelerometer (m/s^2): {}".format(sensor.acceleration))
        #print("Magnetometer (microteslas): {}".format(sensor.magnetic))
        #print("Gyroscope (rad/sec): {}".format(sensor.gyro))
        #print("Euler angle: {}".format(sensor.euler))
        #print("Quaternion: {}".format(sensor.quaternion))
        #print("Linear acceleration (m/s^2): {}".format(sensor.linear_acceleration))
        #print("Gravity (m/s^2): {}".format(sensor.gravity))

