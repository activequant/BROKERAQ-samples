import logging
import datetime
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
        elif baseMessage.type == BaseMessage.ACCT_DATA:
            self.accountData(baseMessage.Extensions[AccountDataMessage.cmd])
        elif baseMessage.type == BaseMessage.POSITION_REPORT:
            self.positionReport(baseMessage.Extensions[PositionReport.cmd])
        elif baseMessage.type == BaseMessage.SERVER_TIME:
             self.serverTime(baseMessage.Extensions[ServerTime.cmd]) 
        elif baseMessage.type == BaseMessage.EXECUTION_REPORT:
            self.executionReport(baseMessage.Extensions[ExecutionReport.cmd])
        elif baseMessage.type == BaseMessage.MD_SUBSCRIBE_RESPONSE:
            self.mdSubscribeResponse(baseMessage.Extensions[MDSubscribeResponse.cmd])
        elif baseMessage.type == BaseMessage.MD_UNSUBSCRIBE_RESPONSE:
            self.mdUnsubscribeResponse(baseMessage.Extensions[MDUnsubscribeResponse.cmd])
        elif baseMessage.type == BaseMessage.OHLC:
            self.ohlc(baseMessage.Extensions[OHLC.cmd])
        elif baseMessage.type == BaseMessage.HIST_OHLCRESPONSE:
            self.historicalOHLC(baseMessage.Extensions[HistOhlcResponse.cmd])
        else:
            print baseMessage 
        return
        
    # all prices arrive in this method. 
    def price(self, instrument, priceMsg):
        self.logger.info('Price: ', instrument, priceMsg)
        print instrument, ': ', priceMsg.bidPx[0],' - ', priceMsg.askPx[0]        

    # the server sends out the server time in regular intervals. 
    def serverTime(self, serverTime):
        print 'The server says, it is ', datetime.datetime.fromtimestamp(serverTime.timestamp/1000000000).strftime('%Y-%m-%d %H:%M:%S'), ' local time.'
        return
        
    # account data contains account specifics, such as cash. 
    def accountData(self, accountMessage):
        print '=== Account data ==='
        print accountMessage
        print '--------------------'
        return
    
    # position reports contain an overview of a position       
    def positionReport(self, positionReport):
        print '=== Position report ==='
        print positionReport
        print '-----------------------'
        return
    
    # an execution report contains all reports about executed order instructions. 
    # This includes cancellations, rejections, acceptance but also order fills. 
    def executionReport(self, executionReport):
        print '=== Execution report ==='
        print executionReport
        print '------------------------'
        return        

    def mdSubscribeResponse(self, mdSubRes):
        print '=== MD Subscribe Response ==='
        print mdSubRes
        print '-----------------------------'
        return
        
    def mdUnsubscribeResponse(self, mdUnsubRes):
        print '=== MD Unsubscribe Response ==='
        print mdUnsubRes
        print '-------------------------------'
        return    
    
    def ohlc(self, ohlc):
        print '=== OHLC ==='
        print ohlc
        print '------------'
        return
        
    def historicalOHLC(self, historicalData):
        print '=== Historical data ==='
        print historicalData
        print '-----------------------'
    
