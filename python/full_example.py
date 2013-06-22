from connectivity.messages_pb2 import *
from connectivity.aq_socket import *
from connectivity.message_listener import *
from connectivity.definitions import *
from functions import onlinearchive

import pandas as pd
import numpy as np

# Moving average cross over notifier. 
# author: GhostRider

class MyListener(MessageListener):
  
  candles = {}


  def init(self, instrumentId):
      self.candles[ohlc.mdiId] = onlinearchive.history('EURUSD','HOURS_1',20130615,20130701) 
      return
  

  def loggedIn(self):
    print "Logged in!"
  
  def ohlc(self, ohlc):
    
    self.candles[ohlc.mdiId].insert(0, ohlc)
    
    return
    

# let's create the listener. 
listener = MyListener()
aqsPrice = AqSocket(l)
aqsPrice.host = '78.47.96.150'
aqsPrice.connect()
aqsPrice.login("ustaudinger2", "abcd1234", "PRICE")


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





