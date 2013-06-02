from connectivity.messages_pb2 import *
from connectivity.aq_socket import *
from connectivity.message_listener import *
from connectivity.definitions import *

class MyListener(MessageListener):
  def loggedin(self):
    print "Logged in!"
    


aqsPrice = AqSocket(MyListener())
aqsPrice.host = '78.47.96.150'
aqsPrice.connect()
aqsPrice.login("ustaudinger2", "abcd1234", "PRICE")
aqsPrice.subscribe(Symbols.GBPNOK, TimeFrames.MINUTES_1)
aqsPrice.subscribe(Symbols.EURUSD, TimeFrames.MINUTES_1)
# aqsPrice.subscribe(Symbols.EURUSD, TimeFrames.RAW)
aqsPrice.subscribe(Symbols.SMICHF, TimeFrames.MINUTES_1)
aqsPrice.subscribe(Symbols.DAXEUR, TimeFrames.RAW)
