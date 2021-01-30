import cv2
import imagezmq
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

def sendImagesToWeb():
    # When we have incoming request, create a receiver and subscribe to a publisher
    receiver = imagezmq.ImageHub(open_port='tcp://192.168.1.210:5560', REQ_REP = False)
    while True:
        # Pull an image from the queue
        camName, frame = receiver.recv_image()
        # Using OpenCV library create a JPEG image from the frame we have received
        jpg = cv2.imencode('.jpg', frame)[1]
        # Convert this JPEG image into a binary string that we can send to the browser via HTTP
        yield b'--frame\r\nContent-Type:image/jpeg\r\n\r\n'+jpg.tostring()+b'\r\n'

# Add `application` method to Request class and define this method here
@Request.application
def application(request):
    # What we do is we `sendImagesToWeb` as Iterator (generator) and create a Response object
    # based on its output.
    return Response(sendImagesToWeb(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # This code starts simple HTTP server that listens on interface with IP 192.168.0.114, port 4000
    run_simple('192.168.1.220', 4000, application)
