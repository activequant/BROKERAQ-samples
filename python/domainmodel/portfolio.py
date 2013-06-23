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

class Position:
    
    tradInstId = None
    entryPrice = None
    quantity = None
    lastPnl = None
    
    def value(self, valuationPrice):
        if(self.quantity > 0):
            self.lastPnl = (valuationPrice - self.entryPrice) * self.quantity
        else:
            self.lastPnl = (self.entryPrice - valuationPrice) * self.quantity
        return self.lastPnl



class Portfolio:
    
    positions = None
    
    def setPosition(self, tradInstId, entryPrice, quantity):
        return
    
    def getPosition(self, tradInstId):
        return None
