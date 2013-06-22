

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
