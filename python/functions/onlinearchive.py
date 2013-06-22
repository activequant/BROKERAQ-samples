import pandas as pd
import numpy as np

def history(instrument, timeframe, startDate8, endDate8):
  url = 'http://78.47.96.150:44444/csv/?SERIESID=' + instrument + '&FREQ=' + timeframe + '&FIELD=O,H,L,C&STARTDATE=' + str(startDate8) + '&ENDDATE=' + str(endDate8)
  # print url  
  x = pd.read_csv(url, index_col=[0])
  # as AQ already uses nanosecond time stamps ... 
  x.index = pd.to_datetime(x.index)
  # we'll drop the date time column as it is not needed. 
  del x['DateTime']
  # 
  return x
  