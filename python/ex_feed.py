from connectivity.messages_pb2 import *
from connectivity.aq_socket import *
from connectivity.message_listener import *
from connectivity.definitions import *

class MyListener(MessageListener):
  def loggedin(self):
    print "Logged in!"
    


aqsPrice = AqSocket(MyListener())
aqsPrice.host = '192.168.0.6'
aqsPrice.connect()
aqsPrice.login("ustaudinger2", "abcd1234", "PRICE")
aqsPrice.subscribe(Symbols.AUDCHF, TimeFrames.RAW)