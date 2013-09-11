#
# Copyright 2013 ActiveQuant GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import threading
import socket 
import time
import logging
from messages_pb2 import *
from bincalc import *
from message_listener import *
           

# The AqSocket class is responsible for managing the connection to an AQ endpoint and also to send messages to and from it. 
class AqSocket (threading.Thread):

    sock = None 
    messageListener = None
    host = '78.47.96.150' # by default we connect to the demo server. 
    port = 59999   
    orderCounter = 0
    logger = None
    # set this flag to a value greater than 0 to enable automatic reconnects. 
    # The set value specifies the time between reconnect attempts after a connection has been lost. 
    autoReconnectTime = 5

    # plain constructor. 
    def __init__(self, mlistener):
        logging.basicConfig(format='%(asctime)-15s %(name)s %(message)s')
        self.logger = logging.getLogger('AQSocket')
        self.logger.setLevel(logging.INFO)
        self.logger.info('Initializing AQSocket.')
        threading.Thread.__init__(self)
        # let's store the reference to the message listener. 
        self.messageListener = mlistener
        # let's also set a link back to the message listener. 
        mlistener.aqSocket = self
        self.kill_received = False
            
    # connects the socket and starts the read thread. 
    def connect(self):
        self.start()
        
    # read loop
    def run(self):
        while not self.kill_received: 
            self.sock = None
            # we'll try to reconnect as often as possible. 
            try:
                self.logger.info('Trying to connect socket.')        
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, self.port))
                self.logger.info('socket connected')
                if self.messageListener != None:
                    self.messageListener.connected()
                lengthBytes = [] 
                # check if we received a kill signal.                    
                while not self.kill_received:            
                    data = self.sock.recv(1)
                    if len(data) == 0:
                        if self.messageListener!=None:
                            self.messageListener.disconnected()
                            self.sock = None
                        break
                    lengthBytes.append(data)
                    intVal = ord(data)
                    if intVal < 128:
                        length = varintToNumber(bytearray(lengthBytes))
                        data = self.sock.recv(length)
                        lengthBytes = []
                        try:
                            self.decodeBaseMessage(data)
                        except Exception: 
                            self.logger.warn(sys.exc_info())
            except Exception as msg:
                print 'Error while working with socket:', sys.exc_info(), msg
                if self.sock is not None: 
                    self.sock.close()
                self.sock = None
            # let's check if we should reconnect
            if self.autoReconnectTime>0 and not self.kill_received:
                time.sleep(self.autoReconnectTime)
            else: 
                break
    
    # method to send a base message. 
    # gets the Varint32 encoded length as bytes, sends these and then sends the base message
    def sendFrame(self, baseMsg):
        if self.sock is None: 
            self.logger.warn('Cannot send message as socket is not connected.')
            
        self.logger.debug('sending frame to server.')
        b = numberToVarint(len(baseMsg))
        # send the frame
        self.sock.sendall(b)
        self.sock.sendall(baseMsg)
            
    # method to subscribe to a live feed.        
    # it is recommended that you use isntrumentIds from the Symbols definition
    # time frames are also contained in the defintions file (see domainmodel folder)
    def subscribe(self, instrumentId, timeframe):
        self.logger.info('Subscribing to %s with resolution %s', instrumentId, timeframe)
        baseMsg = BaseMessage()
        baseMsg.type = BaseMessage.MD_SUBSCRIBE
        req = baseMsg.Extensions[MDSubscribe.cmd]
        req.mdiId = instrumentId
        req.timeframe = timeframe
        self.sendFrame(baseMsg.SerializeToString())
    
    # a method to unsubscribe from a price feed. 
    def unsubscribe(self, instrumentId, timeframe):
        self.logger.info('Unsubscribing from %s with resolution %s', instrumentId, timeframe)
        baseMsg = BaseMessage()
        baseMsg.type = BaseMessage.MD_UNSUBSCRIBE
        req = baseMsg.Extensions[MDUnsubscribe.cmd]
        req.mdiId = instrumentId
        req.timeframe = timeframe
        self.sendFrame(baseMsg.SerializeToString())
    
    # method to send an in-band history request to the server. 
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
    
    # generates and returns a new order id, should be used internally only. 
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
    


