from operator import attrgetter
import pandas as pd
import numpy as np

def ema20(index, period, closelist):
  print 'Period', period, ' Index', index
  formerVal = 0
  l = len(closelist)
  if (l-1)>index:
      if index<200:
          print 'diving in ..'
          formerVal = ema20(index+1, period, closelist)
      else:
          print 'returning actual value' 
          formerVal = closelist[l - index-1]
  else:
      print 'returning actual value, too', (closelist[l-index-1])
      formerVal = closelist[l - index-1]
      
  factor = 2.0/(period+1.0)
  currentVal = closelist[l-index-1]
  val = (1-factor)*currentVal + factor * formerVal
  print 'prior',formerVal ,'Calculated', val, ' factor', factor, ' index', index, '  raw val', closelist[l-index-1]
  return val


clist = [1,2,3,4,5,6,7,8,9,10]
print ema20(0, 7, clist)

# map(attrgetter('my_attr'), my_list)

