import zmq
import time
context = zmq.Context()

print("Connecting to HWS")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

for request in range(1000):
    print("Sending request %s ..." % request)
    socket.send(b" This is a test of sending a speech command to the speech center")
    #socket.send_string("This is a new test of sending a speech command to the speech center")

    message = socket.recv()
    print("Received reply %s [ %s ]" % (request, message))
    
