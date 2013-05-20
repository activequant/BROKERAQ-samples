import logging
from messages_pb2 import *

# the message listener class receives all messages from an AQ socket.
class MessageListener:

    logger = None
    
    def __init__(self):
        self.logger = logging.getLogger('MessageListener')
        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)
        sh.setFormatter(logging.Formatter('%(asctime)-15s %(clientip)s %(user)-8s %(message)s'))        
        self.logger.addHandler(sh)
        self.logger.info('Initializing message listener.')
        return
    
    def connected(self):
        self.logger.info('Connected.')
        
    def disconnected(self):
        self.logger.info('Disconnected.')
        
    def loggedIn(self):
        self.logger.info('Logged in ')
        print 'logged in'
    
    def loginRejected(self, message):
        self.logger.info('Login rejected. ', message)
        print message
        
    # base messages are all raw protobuf messages.
    def process(self, baseMessage):
        #ok, we got a base message. let's check its type. 
        if baseMessage.type == BaseMessage.LOGIN_RESPONSE:
            obj = baseMessage.Extensions[LoginResponse.cmd]
            if obj.status.startswith('Welcome.'):
                self.loggedIn()
            else:
                self.loginRejected(obj.status)
        elif baseMessage.type == BaseMessage.MDS:
            obj = baseMessage.Extensions[MarketDataSnapshot.cmd]
            self.price(obj.mdiId, obj)            
        else:
            print baseMessage 
        return
        
    def price(self, instrument, priceMsg):
        self.logger.info('Price: ', instrument, priceMsg)
        print instrument, ': ', priceMsg.bidPx[0],' - ', priceMsg.askPx[0]        
        
    def accountData(self, accountMessage):
        return
        
    def positionReport(self, positionReport):
        return
        
    def executionReport(self, executionReport):
        return        
        
    def infoMessage(self, infoMessage):
        return
        
    def orderMessage(self, orderMessage):
        return
        
        
        