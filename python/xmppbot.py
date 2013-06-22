
import sys
import logging
import getpass
from threading import Thread
from Queue import Queue
from optparse import OptionParser

import sleekxmpp



class XmppBot(sleekxmpp.ClientXMPP):

    outgoingQueue = Queue()    
    
    def worker(self):
        while True:
            item = self.outgoingQueue.get()
            # let's send it. 
            print item[0], item[1]
            self.send_message(mto=item[0], mbody=item[1], mtype='chat')

            

    def __init__(self, jid, password):
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
        if msg['type'] in ('chat', 'normal'):
            msg.reply("Thanks for sending\n%(body)s" % msg).send()

