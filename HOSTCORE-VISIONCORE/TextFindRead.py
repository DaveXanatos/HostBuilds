import cv2
import pytesseract
import numpy as np
import threading
from threading import Thread
import imutils
from imutils.video import VideoStream
from imutils.perspective import four_point_transform
import zmq
import imagezmq
from time import sleep

debug = 1

context = zmq.Context()

dev = 1 #1 shows image on screen, 0 does not.  0 *should* be faster...

print("Connecting to Speech Center")
socket = context.socket(zmq.REQ)
socket.connect("tcp://192.168.1.201:5555")   #5556 is visual, 5558 is language, 5555 dir to speech

def set_voice(msg):
    socket.send_string(msg)
    #message = socket.recv().decode('utf-8')

if dev == 1:
    test_img = np.zeros(shape=(300,400,3)).astype('uint8')
    cv2.namedWindow('Txt Frame', cv2.WINDOW_GUI_NORMAL)
    cv2.imshow('Txt Frame',test_img)
    cv2.moveWindow('Txt Frame',75,25)
    cv2.waitKey(1)

class VideoStreamSubscriber:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self._stop = False
        self._data_ready = threading.Event()
        self._thread = threading.Thread(target=self._run, args=())
        self._thread.daemon = True
        self._thread.start()

    def receive(self, timeout=600.0):
        flag = self._data_ready.wait(timeout=timeout)
        if not flag:
            raise TimeoutError(
                "Timeout while reading from subscriber tcp://{}:{}".format(self.hostname, self.port))
        self._data_ready.clear()
        return self._data

    def _run(self):
        receiver = imagezmq.ImageHub("tcp://{}:{}".format(self.hostname, self.port), REQ_REP=False)
        while not self._stop:
            self._data = receiver.recv_jpg()
            self._data_ready.set()
        # Close socket here, not implemented in ImageHub :(
        # zmq_socket.close()

    def close(self):
        self._stop = True

# Receive from broadcast
hostname = "192.168.1.210"  # Use to receive from other computer
port = 5560
receiver = VideoStreamSubscriber(hostname, port)

def find_text(image):
    # convert the image to grayscale and blur it slightly
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 3)

    # apply adaptive thresholding and then invert the threshold map
    thresh = cv2.adaptiveThreshold(blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    thresh = cv2.bitwise_not(thresh)

    # check to see if we are visualizing each step of the image
    # processing pipeline (in this case, thresholding)
    #if debug:
        #cv2.imshow("Text Thresh", thresh)
        #cv2.waitKey(0)

    # find contours in the thresholded image and sort them by size in
    # descending order
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

    # initialize a contour that corresponds to the puzzle outline
    textCnt = None

    # loop over the contours
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        # if our approximated contour has four points, then we can
        # assume we have found the outline of the puzzle
        if len(approx) == 4:
            textCnt = approx
            break

    # if the puzzle contour is empty then our script could not find
    # the outline of the sudoku puzzle so raise an error
    if textCnt is None:
        raise Exception(("Could not find text outline. "
            "Try debugging your thresholding and contour steps."))

    # check to see if we are visualizing the outline of the detected text
    if debug:
        # draw the contour of the text in the image and then display
        # it to our screen for visualization/debugging purposes
        output = image.copy()
        cv2.drawContours(output, [textCnt], -1, (0, 255, 0), 2)
        cv2.imshow("Text Outline", output)
        cv2.waitKey(0)

    # apply a four point perspective transform to both the original
    # image and grayscale image to obtain a top-down birds eye view
    # of the puzzle
    text = four_point_transform(image, textCnt.reshape(4, 2))
    warped = four_point_transform(gray, textCnt.reshape(4, 2))

    # check to see if we are visualizing the perspective transform
    if debug:
        # show the output warped image (again, for debugging purposes)
        cv2.imshow("Text Transform", text)
        cv2.waitKey(0)

    # return a 2-tuple of text in both RGB and grayscale
    return (text, warped)

while True:
    winName, frame = receiver.receive()
    image = cv2.imdecode(np.frombuffer(frame, dtype='uint8'), -1)
    cv2.imshow("Txt Frame", image)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("s"):
        (TextImage, warped) = find_text(image)
        cv2.imshow("Txt Image", TextImage)
        key = cv2.waitKey(1) & 0xFF

        print("'S' Received...")
        speakText = pytesseract.image_to_string(image)
        speakText = speakText.replace("|", "I")
        speakText = speakText.replace("’", "'")
        print(speakText)
        thread = Thread(target = set_voice, args = (speakText, ))
        thread.start()
        cv2.imshow("Txt Frame", image)
        cv2.waitKey(0)
        break

cv2.destroyAllWindows()
