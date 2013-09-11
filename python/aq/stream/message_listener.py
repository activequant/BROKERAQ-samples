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

import logging
import datetime
from messages_pb2 import *
from aq.domainmodel.portfolio import * 
from aq.domainmodel.account import * 

# the message listener class receives all messages from an AQ socket.
# extend this class to implement your own event handlers. 
class MessageListener(object):

    logger = None
    portfolio = Portfolio()
    account = Account()
    aqSocket = None
    
    def __init__(self):
        logging.basicConfig(format='%(asctime)-15s %(name)s %(message)s')
        self.logger = logging.getLogger('MessageListener')
        self.logger.setLevel(logging.INFO)
        self.logger.info('Initializing message listener.')
        return
    
    def connected(self):
        self.logger.info('Connected.')
        
    def disconnected(self):
        self.logger.info('Disconnected.')
        
    def loggedIn(self):
        self.logger.info('Logged in.')
    
    def loginRejected(self, message):
        self.logger.info('Login rejected: %s', message)
        
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
        self.logger.info('Price: %s %s', instrument, priceMsg)

    # the server sends out the server time in regular intervals. 
    def serverTime(self, serverTime):
        self.logger.info('The server says, it is %s local time.', datetime.datetime.fromtimestamp(serverTime.timestamp/1000000000).strftime('%Y-%m-%d %H:%M:%S'))
        return
        
    # account data contains account specifics, such as cash. 
    def accountData(self, accountMessage):
        self.logger.info('=== Account data ===')
        self.logger.info(accountMessage)
        self.logger.info('--------------------')
        # let's also update the account object. 
        if len(accountMessage.type)>6: 
            if accountMessage.type[:4] == 'CASH':
                self.account.cash = float(accountMessage.value)
                self.account.accountNumber = accountMessage.type[6:]
                self.logger.info('Cash value for account >%s< received: %d', self.account.accountNumber, self.account.cash)
        return
    
    # position reports contain an overview of a position       
    def positionReport(self, positionReport):
        self.logger.info('=== Position report ===')
        self.logger.info(positionReport)
        self.logger.info('-----------------------')
        # let's also update the portfolio. 
        self.portfolio.setPosition(positionReport.tradInstId, positionReport.entryPrice, positionReport.quantity)
        return
    
    # an execution report contains all reports about executed order instructions. 
    # This includes cancellations, rejections, acceptance but also order fills. 
    def executionReport(self, executionReport):
        self.logger.info('=== Execution report ===')
        self.logger.info(executionReport)
        self.logger.info('------------------------')
        return        

    # unused at the moment. 
    def mdSubscribeResponse(self, mdSubRes):
        self.logger.info('=== MD Subscribe Response ===')
        self.logger.info(mdSubRes)
        self.logger.info('-----------------------------')
        return
        
    # unused at the moment. 
    def mdUnsubscribeResponse(self, mdUnsubRes):
        self.logger.info('=== MD Unsubscribe Response ===')
        self.logger.info(mdUnsubRes)
        self.logger.info('-------------------------------')
        return    
    
    # the server sends out open/high/low/close bars at regular intervals. 
    # these bars arrive here. 
    def ohlc(self, ohlc):
        self.logger.info('=== OHLC ===')
        self.logger.info(ohlc)
        self.logger.info('------------')
        return

    # Unused at the moment in favor of a plain out-of-band http history fetch    
    def historicalOHLC(self, historicalData):
        self.logger.info('=== Historical data ===')
        self.logger.info(historicalData)
        self.logger.info('-----------------------')
    
