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

from aq.stream.messages_pb2 import *
from aq.stream.aq_socket import *
from aq.stream.message_listener import *
from aq.domainmodel.definitions import *

class MyListener(MessageListener):
    def loggedIn(self):
      print "Logged in!"
    
    def connected(self):
        self.aqSocket.login('demo', 'demo', "PRICE")
      


# let's add the main. 
def main(args):
    logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(name)s| %(message)s')
    aqsPrice = AqSocket(MyListener())            
    aqsPrice.host = '78.47.96.150'    
    aqsPrice.connect()

if __name__ == '__main__':
    main(sys.argv)
