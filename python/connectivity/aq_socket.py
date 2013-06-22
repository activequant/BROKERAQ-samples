# This file is placed into the public domain under the GPL. 
# Author: GhostRider

import threading
import socket 
import struct
import logging
from messages_pb2 import *
from bincalc import *
from message_listener import *
           
class AqSocket (threading.Thread):

    sock = None 
    messageListener = None
    host = 'localhost'
    port = 59999   
    orderCounter = 0
    logger = None

    
    # plain constructor. 
    def __init__(self, mlistener):
        logging.basicConfig(format='%(asctime)-15s %(name)s %(message)s')
        self.logger = logging.getLogger('AQSocket')
        self.logger.setLevel(logging.INFO)
        self.logger.info('Initializing AQSocket.')
        threading.Thread.__init__(self)
        self.messageListener = mlistener
        
    # connects the socket and starts the read thread. 
    def connect(self):         
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.logger.info('socket connected')
        if self.messageListener != None:
            self.messageListener.connected()
        self.start()
        
    # read loop
    def run(self):
        self.logger.info('Spawned new thread in read mode ...')        
        lengthBytes = []                    
        while 1:            
            data = self.sock.recv(1)
            if len(data) == 0:
                if self.messageListener!=None:
                    self.messageListener.disconnected()
                return
            lengthBytes.append(data)
            intVal = ord(data)
            if intVal < 128:
                length = varintToNumber(bytearray(lengthBytes))
                data = self.sock.recv(length)
                lengthBytes = []
                self.decodeBaseMessage(data)
    
    # method to send a base message. 
    # gets the Varint32 encoded length as bytes, sends these and then sends the base message
    def sendFrame(self, baseMsg):
        self.logger.debug('sending frame to server.')
        b = numberToVarint(len(baseMsg))
        # send the frame
        self.sock.sendall(b)
        self.sock.sendall(baseMsg)
            
    def subscribe(self, instrumentId, timeframe):
        self.logger.info('Subscribing to %s with resolution %s', instrumentId, timeframe)
        baseMsg = BaseMessage()
        baseMsg.type = BaseMessage.MD_SUBSCRIBE
        req = baseMsg.Extensions[MDSubscribe.cmd]
        req.mdiId = instrumentId
        req.timeframe = timeframe
        self.sendFrame(baseMsg.SerializeToString())
    
    def unsubscribe(self, instrumentId, timeframe):
        self.logger.info('Unsubscribing from %s with resolution %s', instrumentId, timeframe)
        baseMsg = BaseMessage()
        baseMsg.type = BaseMessage.MD_UNSUBSCRIBE
        req = baseMsg.Extensions[MDUnsubscribe.cmd]
        req.mdiId = instrumentId
        req.timeframe = timeframe
        self.sendFrame(baseMsg.SerializeToString())
    
    def requestHistory(self, instrumentId, timeframe, startDate8, endDate8):
        self.logger.info('Requesting history for %s with resolution %s', instrumentId, timeframe)
        baseMsg = BaseMessage()
        baseMsg.type = BaseMessage.HIST_REQUEST
        req = baseMsg.Extensions[HistRequest.cmd]
        req.timeframe = timeframe
        req.startDate8 = startDate8
        req.endDate8 = endDate8 
        req.mdiId = instrumentId
        self.sendFrame(baseMsg.SerializeToString())
        return
        
    # issues a market buy order. 
    def marketBuy(self, instrumentId, quantity):
        baseMsg = BaseMessage()
        baseMsg.type = BaseMessage.NEW_ORDER
        orderMsg = baseMsg.Extensions[NewOrder.cmd]
        # order type 1
        oid = self.genOid()
        orderMsg.tradInstId = instrumentId
        orderMsg.clOrdId = '%s' % oid
        orderMsg.side = 1
        orderMsg.orderQty = quantity
        orderMsg.ordType = 1
        orderMsg.comment = 'API'
        orderMsg.resend = 0	
        self.sendFrame(baseMsg.SerializeToString())
        return oid
    
    # issues a market sell order - order type 1. 
    def marketSell(self, instrumentId, quantity):
        baseMsg = BaseMessage()
        baseMsg.type = BaseMessage.NEW_ORDER
        orderMsg = baseMsg.Extensions[NewOrder.cmd]
        # order type 1
        oid = self.genOid()
        orderMsg.tradInstId = instrumentId
        orderMsg.clOrdId = '%s' % oid
        orderMsg.side = -1
        orderMsg.orderQty = quantity
        orderMsg.ordType = 1
        orderMsg.comment = 'API'
        orderMsg.resend = 0	
        self.sendFrame(baseMsg.SerializeToString())
        return oid
        
    # sends a buy limit order over the wire - order type 2, order side 1 
    def limitBuy(self, instrumentId, quantity, price):
        baseMsg = BaseMessage()
        baseMsg.type = BaseMessage.NEW_ORDER
        orderMsg = baseMsg.Extensions[NewOrder.cmd]
        # order type 1
        oid = self.genOid()
        orderMsg.tradInstId = instrumentId
        orderMsg.clOrdId = '%s' % oid
        orderMsg.side = 1
        orderMsg.orderQty = quantity
        orderMsg.ordType = 2
        orderMsg.price = price
        orderMsg.comment = 'API'
        orderMsg.resend = 0	
        self.sendFrame(baseMsg.SerializeToString())
        
        return
        
    # sends a sell limit order over the wire - order type 2, order side -1 
    def limitSell(self, instrumentId, quantity, price):
        baseMsg = BaseMessage()
        baseMsg.type = BaseMessage.NEW_ORDER
        orderMsg = baseMsg.Extensions[NewOrder.cmd]
        # order type 1
        oid = self.genOid()
        orderMsg.tradInstId = instrumentId
        orderMsg.clOrdId = '%s' % oid
        orderMsg.side = -1
        orderMsg.orderQty = quantity
        orderMsg.ordType = 2
        orderMsg.price = price
        orderMsg.comment = 'API'
        orderMsg.resend = 0	
        self.sendFrame(baseMsg.SerializeToString())
        return
    
    
    # sends a buy stop market order over the wire - order type 3
    def stopBuy(self, instrumentId, quantity, price):
        return
        
    # sends a sell stop market order over the wire - order type 3
    def stopSell(self, instrumentId, quantity, price):
        return
    
    
    def cancelOrder(self, orderId):
        return
    
    # it is only possible to update limit orders with new price and quantity.  
    def updateOrder(self, orderId, newPrice, newQuantity):
        return
    
    # generates and returns a new order id
    def genOid(self):
        self.orderCounter = self.orderCounter + 1
        return self.orderCounter
    
    # sends a login message over the wire
    def login(self, username, password, session):
      self.logger.info('Preparing login message for a %s session for %s', session, username)
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
    
    # this raw method creates a base message from an input string. 
    def decodeBaseMessage(self, message):
        self.logger.debug('Decoding a base message. ')
        baseMessage = BaseMessage()
        baseMessage.ParseFromString(message)
        # print baseMessage
        if self.messageListener != None:
            self.messageListener.process(baseMessage)
    


