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

