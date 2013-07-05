import os
import sys
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
    sys.path.insert(1, path)
del path

from aq.functions import onlinearchive

import pybacktest
import matplotlib.pyplot as plt
import pandas
from pandas import Series, ewma, concat, DataFrame
import matplotlib.pyplot as plt

#h = onlinearchive.history('EURUSD','HOURS_1',20130615,20130701)
eurusd = onlinearchive.history('EURUSD','HOURS_1',20130501,20130701)
# usdchf = onlinearchive.history2('CNX.MDI.EUR/GBP','HOURS_1',20120801,20130701)
# eurusd.plot()
# usdchf.plot()
# plt.show()

slowEma1 = DataFrame(ewma(eurusd.ix[:,3], span = 20))
fastEma1 = DataFrame(ewma(eurusd.ix[:,3], span = 50))

emaDiff = (fastEma1 - slowEma1) * 1000000
emaDiff = emaDiff.astype(int)
# signal = (((fastEma1 - slowEma1) > 0) * 2 - 1)
signal = emaDiff.shift(1).ix[:,0]

closeDiff = eurusd.ix[:,3].diff()

pnl = (closeDiff * signal).cumsum()


# 
plt.figure(1)
plt.subplot(211)
pnl.plot()
plt.subplot(212)
eurusd.ix[:,3].plot()

