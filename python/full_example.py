from datetime import date, timedelta

from connectivity.aq_socket import AqSocket
from connectivity.message_listener import MessageListener
from connectivity.definitions import Symbols, TimeFrames
from functions import onlinearchive

import pandas as pd

from xmppbot import XmppBot

# Moving average cross over notifier. 
# author: GhostRider
# Listener class. 
class MyListener(MessageListener):
  
  candles = {}
  xmpp = []

  jid = ''
  password = ''
  targetjid = ''

  def __init__(self):
      super(MyListener, self).__init__()
      self.xmpp = XmppBot(self.jid, self.password)
      if self.xmpp.connect(): 
        self.xmpp.process(block=False)
        print("Done")
      else:
        print("Unable to connect.")
      return
  
  
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

  # checks if a series crossed. 
  def crossing(self, series1, series2):
      if len(series1)==len(series2) and len(series1) > 1:
          length = len(series1)
          if series1[length-2] > series2[length-2] and series1[length-1] < series2[length-1]:
              return -1
          if series1[length-2] < series2[length-2] and series1[length-1] > series2[length-1]:
              return 1                
      return 0
  
  def ohlc(self, ohlc):
    tempDf = pd.DataFrame({'O': ohlc.open, 'H':ohlc.high,'L':ohlc.low,'C':ohlc.close, 'V':ohlc.volume}, index=[ohlc.timestamp])
    tempDf.index = pd.to_datetime(tempDf.index)
    # let's append this new candle ... 
    self.candles[ohlc.mdiId] = self.candles[ohlc.mdiId].append(tempDf)
    # now, let's calculate the ewma values. 
    ewma20 = pd.ewma(self.candles[ohlc.mdiId]['C'], span=20)
    ewma50 = pd.ewma(self.candles[ohlc.mdiId]['C'], span=50)
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
listener = MyListener()
aqsPrice = AqSocket(listener)
aqsPrice.host = '78.47.96.150'
aqsPrice.connect()
aqsPrice.login(brokeraqUid, brokeraqPwd, "PRICE")

listener.init(Symbols.EURUSD)
aqsPrice.subscribe(Symbols.EURUSD, TimeFrames.HOURS_1)

listener.init(Symbols.OILUSD)
aqsPrice.subscribe(Symbols.OILUSD, TimeFrames.HOURS_1)

listener.init(Symbols.EURCHF)
aqsPrice.subscribe(Symbols.EURCHF, TimeFrames.HOURS_1)

listener.init(Symbols.USDCHF)
aqsPrice.subscribe(Symbols.USDCHF, TimeFrames.HOURS_1)

listener.init(Symbols.XAGUSD)
aqsPrice.subscribe(Symbols.XAGUSD, TimeFrames.HOURS_1)

