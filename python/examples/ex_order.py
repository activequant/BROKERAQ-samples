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

import os
import sys

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
    sys.path.insert(1, path)
del path

from aq.stream.messages_pb2 import *
from aq.stream.aq_socket import *
from aq.stream.message_listener import *
from aq.domainmodel.definitions import *

class MyListener(MessageListener):
    def loggedIn(self):
        print "Logged in!"
        # aqsOrder.marketSell(Symbols.EURUSD, 100000)    
        aqsOrder.limitBuy(Symbols.EURUSD, 100000, 1.2)
            
    def connected(self):
        aqsOrder.login('demo', 'demo', "TRADE")


# let's set up basic logging.     
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(name)s| %(message)s')

aqsOrder = AqSocket(MyListener())
aqsOrder.host = '78.47.96.150'
aqsOrder.connect()

