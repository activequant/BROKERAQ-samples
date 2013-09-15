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

import sys
import logging
import getpass
from threading import Thread
from Queue import Queue
from optparse import OptionParser
import sleekxmpp


class BaseXMPPListener: 
    botReference = None
    
    def message(self, msg):
        self.logger.info('XMPP Message received: ', msg)

class XmppBot(sleekxmpp.ClientXMPP):

    outgoingQueue = Queue()    
    messageListener = None
    logger = None 
    
    def worker(self):
        while True:
            item = self.outgoingQueue.get()
            # let's send it. 
            print item[0], item[1]
            self.send_message(mto=item[0], mbody=item[1], mtype='chat')

            

    def __init__(self, jid, password, ml):
        self.logger = logging.getLogger('XmppBot')
        self.logger.setLevel(logging.DEBUG)
        self.logger.debug('Initializing XMPPBot ...')

        self.messageListener = ml
        ml.botReference = self 
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)

    def start(self, event):
        self.send_presence()
        self.get_roster()
        # let's also spawn a message sender thread. 
        t = Thread(target=self.worker)
        t.daemon = True
        t.start()

    def message(self, msg):
        if self.messageListener is None: 
            self.loger.info('No message listener registered.')
            if msg['type'] in ('chat', 'normal'):
                msg.reply("You sent\n%(body)s" % msg).send()
        else: 
            self.messageListener.message(msg)    

