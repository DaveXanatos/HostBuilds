import zmq
import time
context = zmq.Context()

print("Connecting to Visual Systems")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5556")

def main():
    while True:
        print("Ready")
        T = input("> ")
        socket.send_string(T)
        message = socket.recv()
        message = message.decode('utf-8')
        print("Received reply %s " % (message))

if __name__ == "__main__":
    main()  
