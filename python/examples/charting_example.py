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

from aq.util import onlinearchive

import pybacktest
import matplotlib.pyplot as plt
import pandas
from pandas import Series, ewma, concat, DataFrame
import matplotlib.pyplot as plt

# h = onlinearchive.history('EURUSD','HOURS_1',20130615,20130701)
eurusd = onlinearchive.history('EURUSD', 'HOURS_1', 20130501, 20130701)
# usdchf = onlinearchive.history2('CNX.MDI.EUR/GBP','HOURS_1',20120801,20130701)
# eurusd.plot()
# usdchf.plot()
# plt.show()

slowEma1 = DataFrame(ewma(eurusd.ix[:, 3], span=20))
fastEma1 = DataFrame(ewma(eurusd.ix[:, 3], span=50))

emaDiff = (fastEma1 - slowEma1) * 1000000
emaDiff = emaDiff.astype(int)
# signal = (((fastEma1 - slowEma1) > 0) * 2 - 1)
signal = emaDiff.shift(1).ix[:, 0]

closeDiff = eurusd.ix[:, 3].diff()

pnl = (closeDiff * signal).cumsum()


# 
plt.figure(1)
plt.subplot(211)
pnl.plot()
plt.subplot(212)
eurusd.ix[:, 3].plot()

