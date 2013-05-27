from connectivity.messages_pb2 import *
from connectivity.aq_socket import *
from connectivity.message_listener import *
from connectivity.definitions import *

class MyListener(MessageListener):
  def loggedin(self):
    print "Logged in!"
    


aqsPrice = AqSocket(MyListener())
<<<<<<< HEAD
aqsPrice.host = 'localhost'
aqsPrice.connect()
aqsPrice.login("ustaudinger2", "abcd1234", "PRICE")
aqsPrice.subscribe(Symbols.GBPNOK, TimeFrames.RAW)
aqsPrice.subscribe(Symbols.CHFNOK, TimeFrames.RAW)
aqsPrice.subscribe(Symbols.SMICHF, TimeFrames.RAW)
aqsPrice.subscribe(Symbols.DAXEUR, TimeFrames.RAW)
=======
aqsPrice.host = '192.168.0.6'
aqsPrice.connect()
aqsPrice.login("ustaudinger2", "abcd1234", "PRICE")
aqsPrice.subscribe(Symbols.AUDCHF, TimeFrames.RAW)
>>>>>>> d74cca68dcf47c125011f844bb6c14cda5a6f48d
