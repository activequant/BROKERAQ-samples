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


from datetime import date, timedelta


# aq
from aq.stream.aq_socket import AqSocket
from aq.stream.message_listener import MessageListener
from aq.domainmodel.definitions import Symbols, TimeFrames
from aq.util import onlinearchive
from aq.util.xmppbot import XmppBot, BaseXMPPListener

# 3rd party
import pandas as pd

# plain xmpp message listener that responds to incoming chat messages. 
class XMPPMessageListener(BaseXMPPListener):
    myListener = None 
    
    def __init__(self, myListener):
        self.myListener = myListener 
    
    def message(self, msg):
        print 'XMPP Message received: ', msg
        msg.reply('All fine.').send()


# This class looks for periods of low valitity and flat prices.
# It subscribes to hourly and minute bars. 
# Based on the hours, it calculates a threshold value, which it monitors 
# on a minute level. 
# 
# author: GhostRider
class MyListener(MessageListener):
  upperBoundaries = {}
  lowerBoundaries = {}
  currentPriceRanges = {}
  candlesHourly = {}
  candlesMinutely = {}
  xmpp = []
  aqsPrice = None
  xmppListener = None

  jid = 'the_bot_jid'
  password = 'the_bot_pass'
  targetjid = '_jid_to_send_alert_to'

  def __init__(self):
      super(MyListener, self).__init__()
      self.xmppListener = XMPPMessageListener(self)
      self.xmpp = XmppBot(self.jid, self.password, self.xmppListener)
      if self.xmpp.connect(): 
        self.xmpp.process(block=False)
        print("Done")
      else:
        print("Unable to connect.")
      return
  
  def setAqsPrice(self, aqsPrice):
      self.aqsPrice = aqsPrice
  
  def serverTime(self, serverTime):
      return
    
  # called as soon as the socket got connected to the trading servers. 
  def connected(self):
      # now that we are connected, let's send the login message. 
      self.aqsPrice.login(brokeraqUid, brokeraqPwd, "PRICE")

  
  def init(self, instrumentId):      
      # let's fetch ten days of hourly history. 
      endDate = date.today().strftime('%Y%m%d')
      startDate = (date.today()-timedelta(days=10)).strftime('%Y%m%d')
      self.candlesHourly[instrumentId] = onlinearchive.history(instrumentId, 'HOURS_1',startDate, endDate)          
      length = len(self.candlesHourly[instrumentId])
      lastClose = self.candlesHourly[instrumentId]['C'][length-1]      
      tradingRange = self.calculateTradingRange(self.candlesHourly[instrumentId][length-10:length])
      # let's store the current price range for later reuse.         
      self.currentPriceRanges[instrumentId] = tradingRange
      self.upperBoundaries[instrumentId] = lastClose + tradingRange
      self.lowerBoundaries[instrumentId] = lastClose - tradingRange                
          
      print 'Fetched ', len(self.candlesHourly[instrumentId]), ' candles from history archive.'      
      return
  
  def loggedIn(self):
    print "Breakout watcher ready!"
    # self.xmpp.outgoingQueue.put([self.targetjid, 'Bot is up and running'])
    
    self.init(Symbols.EURUSD)
    self.aqsPrice.subscribe(Symbols.EURUSD, TimeFrames.HOURS_1)
    self.aqsPrice.subscribe(Symbols.EURUSD, TimeFrames.MINUTES_1)
    
    self.init(Symbols.OILUSD)
    self.aqsPrice.subscribe(Symbols.OILUSD, TimeFrames.HOURS_1)    
    self.aqsPrice.subscribe(Symbols.OILUSD, TimeFrames.MINUTES_1)
    
    self.init(Symbols.EURCHF)
    self.aqsPrice.subscribe(Symbols.EURCHF, TimeFrames.HOURS_1)    
    self.aqsPrice.subscribe(Symbols.EURCHF, TimeFrames.MINUTES_1)
    
    self.init(Symbols.USDCHF)
    self.aqsPrice.subscribe(Symbols.USDCHF, TimeFrames.HOURS_1)
    self.aqsPrice.subscribe(Symbols.USDCHF, TimeFrames.MINUTES_1)
    
    self.init(Symbols.XAGUSD)
    self.aqsPrice.subscribe(Symbols.XAGUSD, TimeFrames.HOURS_1)
    self.aqsPrice.subscribe(Symbols.XAGUSD, TimeFrames.MINUTES_1)


  def calculateTradingRange(self, candles):
    #length = len(candles)
    #oVector = candles['O']
    hVector = candles['H']
    lVector = candles['L']
    #cVector = candles['C']
    dailyRanges = hVector - lVector
    meanRange = mean(dailyRanges)
    return meanRange
  
  def ohlc(self, ohlc):
    # mdiId stands for market data instrument ID. 
    tf = ohlc.timeFrame
    # let's check the time frame in minutes ... 
    if tf==60:
        # ok, hourly candle received. 
        tempDf = pd.DataFrame({'O': ohlc.open, 'H':ohlc.high,'L':ohlc.low,'C':ohlc.close, 'V':ohlc.volume}, index=[ohlc.timestamp])
        tempDf.index = pd.to_datetime(tempDf.index)
        # let's append this new candle ... 
        self.candlesHourly[ohlc.mdiId] = self.candlesHourly[ohlc.mdiId].append(tempDf)
        # now, let's update the uper and lower threshold
        length = len(self.candlesHourly[ohlc.mdiId])
        # let's calculate the average trading range over the last five hours
        tradingRange = self.calculateTradingRange(self.candlesHourly[ohlc.mdiId][length-10:length])
        # let's store the current price range for later reuse.         
        self.currentPriceRanges[ohlc.mdiId] = tradingRange
        self.upperBoundaries[ohlc.mdiId] = ohlc.close + tradingRange
        self.lowerBoundaries[ohlc.mdiId] = ohlc.close - tradingRange                
    if tf==1: 
        if self.currentPriceRanges[ohlc.mdiId] is not None: 
            # ok, minute candle received. 
            upperBoundary = self.upperBoundaries[ohlc.mdiId]
            lowerBoundary = self.lowerBoundaries[ohlc.mdiId]
            percDistUp = (upperBoundary / ohlc.close - 1.0)*100.0 
            percDistDown = (lowerBoundary / ohlc.close - 1.0)*100.0            

            print ohlc.mdiId, '\tClose:', ohlc.close,'\tUpper boundary:', upperBoundary, '(', percDistUp,')\tLower boundary:', lowerBoundary, '(',percDistDown,')'
            if ohlc.close > upperBoundary:
                print 'UPWARDS BREAKOUT'
                # let's also pull up the breakout point
                self.upperBoundaries[ohlc.mdiId] = ohlc.close + self.currentPriceRanges[ohlc.mdiId]
                self.xmpp.outgoingQueue.put([self.targetjid, ohlc.mdiId+' UPWARDS BREAKOUT'])                    
            if ohlc.close < lowerBoundary: 
                print 'DOWNWARDS BREAKOUT'
                # let's pull it down ...
                self.lowerBoundaries[ohlc.mdiId] = ohlc.close - self.currentPriceRanges[ohlc.mdiId]
                self.xmpp.outgoingQueue.put([self.targetjid, ohlc.mdiId+' DOWNWARDS BREAKOUT'])
    return
    
    
############### MAIN CODE START     
# let's create the listener. 

brokeraqUid = 'demo'
brokeraqPwd = 'demo'

listener = MyListener()
aqsPrice = AqSocket(listener)
listener.setAqsPrice(aqsPrice)
aqsPrice.host = '78.47.96.150'
aqsPrice.connect()
