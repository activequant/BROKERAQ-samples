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

from connectivity.messages_pb2 import *
from connectivity.aq_socket import *
from connectivity.message_listener import *
from connectivity.definitions import *

class MyListener(MessageListener):
  def loggedIn(self):
    print "Logged in!"
    #aqsOrder.marketSell(Symbols.EURUSD, 100000)    
    aqsOrder.limitBuy(Symbols.EURUSD, 100000, 1.2)    

aqsOrder = AqSocket(MyListener())
aqsOrder.host = '78.47.96.150'
aqsOrder.connect()
aqsOrder.login('demo', 'demo', "TRADE")

