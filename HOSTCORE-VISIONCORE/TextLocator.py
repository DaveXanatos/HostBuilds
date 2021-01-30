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

def find_text(image):
    #image = cv2.imdecode(image, dtype='uint8')
    # convert the image to grayscale and blur it slightly
    #gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #blurred = cv2.GaussianBlur(gray, (7, 7), 3)

    # apply adaptive thresholding and then invert the threshold map
    thresh = cv2.adaptiveThreshold(image, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    thresh = cv2.bitwise_not(thresh)

    # check to see if we are visualizing each step of the image
    # processing pipeline (in this case, thresholding)
    cv2.imshow("Text Thresh", thresh)
    cv2.waitKey(0)

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
    # show the output warped image (again, for debugging purposes)
    cv2.imshow("Text Transform", text)
    cv2.waitKey(0)

    # return a 2-tuple of text in both RGB and grayscale
    return (text, warped)

find_text("./puzzle.jpg")
