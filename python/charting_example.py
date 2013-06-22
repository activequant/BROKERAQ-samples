from functions import onlinearchive
import matplotlib.pyplot as plt


h = onlinearchive.history('EURUSD','HOURS_1',20130615,20130701)
h.plot()
plt.show()

# let's add an EWMA
