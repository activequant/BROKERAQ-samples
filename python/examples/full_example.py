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
import os
import sys

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
    sys.path.insert(1, path)
del path



# aq
from aq.stream.aq_socket import AqSocket
from aq.stream.message_listener import MessageListener
from aq.domainmodel.definitions import Symbols, TimeFrames
from aq.util import onlinearchive
from aq.util.xmppbot import XmppBot, BaseXMPPListener

# 3rd party
import pandas as pd


class XMPPMessageListener(BaseXMPPListener):
    myListener = None 
    
    def __init__(self, myListener):
        self.myListener = myListener 
    
    def message(self, msg):
        print 'XMPP Message received: ', msg
        if msg['body'] == 'status':
            msg.reply("Current %s" %self.myListener.currentDirections).send()
	else:
	    msg.reply('All fine.').send()


# Moving average cross over notifier. 
# author: GhostRider
# Listener class. 
class CrossOverMonitor(MessageListener):
  
  currentDirections = {}
  candles = {}
  xmpp = []
  aqsPrice = None
  xmppListener = None

  jid = '@jabber.org'
  password = ''
  targetjid = ''

  def __init__(self):
      super(CrossOverMonitor, self).__init__()
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
    
  def connected(self):
      self.aqsPrice.login(brokeraqUid, brokeraqPwd, "PRICE")

  
  def init(self, instrumentId):      
      # let's fetch ten days of hourly history. 
      endDate = date.today().strftime('%Y%m%d')
      startDate = (date.today()-timedelta(days=10)).strftime('%Y%m%d')
      
      self.candles[instrumentId] = onlinearchive.history(instrumentId,'HOURS_1',startDate, endDate)          
      print 'Fetched ', len(self.candles[instrumentId]), ' candles from history archive.'      
      return
  
  def loggedIn(self):
    print "Logged in!"
    self.xmpp.outgoingQueue.put([self.targetjid, 'Bot is up and running'])
    
    self.init(Symbols.EURUSD)
    self.aqsPrice.subscribe(Symbols.EURUSD, TimeFrames.HOURS_1)
    
    self.init(Symbols.OILUSD)
    self.aqsPrice.subscribe(Symbols.OILUSD, TimeFrames.HOURS_1)
    
    self.init(Symbols.EURCHF)
    self.aqsPrice.subscribe(Symbols.EURCHF, TimeFrames.HOURS_1)
    
    self.init(Symbols.USDCHF)
    self.aqsPrice.subscribe(Symbols.USDCHF, TimeFrames.HOURS_1)
    
    self.init(Symbols.XAGUSD)
    self.aqsPrice.subscribe(Symbols.XAGUSD, TimeFrames.HOURS_1)



  # checks if a series crossed. 
  def crossing(self, series1, series2):
      if len(series1)==len(series2) and len(series1) > 1:
          length = len(series1)
          if series1[length-2] > series2[length-2] and series1[length-1] < series2[length-1]:
              print 'SHORT'
              return -1
          if series1[length-2] < series2[length-2] and series1[length-1] > series2[length-1]:
              print 'LONG'
              return 1                
      return 0
  
  def ohlc(self, ohlc):
    print 'ohlc received for ', ohlc.mdiId,': ', ohlc.close
    tempDf = pd.DataFrame({'O': ohlc.open, 'H':ohlc.high,'L':ohlc.low,'C':ohlc.close, 'V':ohlc.volume}, index=[ohlc.timestamp])
    tempDf.index = pd.to_datetime(tempDf.index)
    # let's append this new candle ... 
    self.candles[ohlc.mdiId] = self.candles[ohlc.mdiId].append(tempDf)
    # now, let's calculate the ewma values. 
    ewma20 = pd.ewma(self.candles[ohlc.mdiId]['C'], span=20)
    ewma50 = pd.ewma(self.candles[ohlc.mdiId]['C'], span=50)
    
    lastEma20Val = ewma20[len(ewma20)-1]
    lastEma50Val = ewma50[len(ewma50)-1]
    print "EMAs: ", lastEma20Val, " - ", lastEma50Val
    if lastEma20Val > lastEma50Val:
        self.currentDirections[ohlc.mdiId] = 'LONG'
    else:
        self.currentDirections[ohlc.mdiId] = 'SHORT'
    if self.crossing(ewma20, ewma50) > 0:
        # let's trigger some action ... 
        self.xmpp.outgoingQueue.put([self.targetjid, 'LONG '+ohlc.mdiId])
        return
    if self.crossing(ewma20, ewma50) < 0: 
        # let's trigger some action ... 
        self.xmpp.outgoingQueue.put([self.targetjid, 'SHORT '+ohlc.mdiId])
        return    
    return
    
    
############### MAIN CODE START     
# let's create the listener. 

brokeraqUid = 'XXXX'
brokeraqPwd = 'XXXX'

listener = CrossOverMonitor()
aqsPrice = AqSocket(listener)
listener.setAqsPrice(aqsPrice)
aqsPrice.connect()
