import threading
import socket 
import struct
from messages_pb2 import *
from bincalc import *
from message_listener import *


HOST = '192.168.0.6'    
PORT = 59999             

class AqSocket (threading.Thread):
    sock = None 
    messageListener = None
    
    def __init__(self, mlistener):
        threading.Thread.__init__(self)
        self.messageListener = mlistener
        
    def connect(self):         
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        print 'connected...'
        self.start()
        
    # read loop           
    def run(self):
        print 'Going into read mode ...'
        while 1:            
            lengthBytes = []
            data = self.sock.recv(1)
            lengthBytes.append(data)
            intVal = ord(data)
            if intVal < 128:
                length = varintToNumber(bytearray(data))
                data = self.sock.recv(length)
                self.decodeBaseMessage(data)
                    
    
    def sendFrame(self, baseMsg):
      print 'sending frame ...'
      b = numberToVarint(len(baseMsg))
      # send the frame
      self.sock.sendall(b)
      self.sock.sendall(baseMsg)
        
    
    # sends a login message over the wire
    def login(self, username, password, session):
      # let's construct a login message
      baseMsg = BaseMessage()
      baseMsg.type = BaseMessage.LOGIN      
      loginMsg = baseMsg.Extensions[Login.cmd]
      loginMsg.userId = username
      loginMsg.password = password
      loginMsg.sessionType = session     
      # make to serialization
      msg = baseMsg.SerializeToString()
      self.sendFrame(msg)
    
    def decodeBaseMessage(self, message): 
        baseMessage = BaseMessage()
        baseMessage.ParseFromString(message)
        # print baseMessage
        if self.messageListener != None:
            self.messageListener.process(baseMessage)
    



aqs = AqSocket(None)
aqs.messageListener = MessageListener()
print("Started.")
aqs.connect()
aqs.login("ustaudinger2", "abcd1234","PRICE")
