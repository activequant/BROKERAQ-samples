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
  