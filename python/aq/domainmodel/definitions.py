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

# This file contains various definitions 
# here we define the most common time frames. 
class TimeFrames:
        RAW = "RAW" # Raw is a tick based stream 
        MINUTES_1 = "MINUTES_1"  # one minute candles ... 
        MINUTES_5 = "MINUTES_5"  # five minute ...
        MINUTES_15 = "MINUTES_15" # fifteen ... 
        HOURS_1 = "HOURS_1" # 1 ... 
        EOD = "EOD" # ...
        
# Here we define the most common symbols, dealable on ACM/SwissQuote.  
class Symbols:
        AUDCAD = "AUDCAD"
        AUDCHF = "AUDCHF"
        AUDJPY = "AUDJPY"
        AUDNZD = "AUDNZD"
        AUDUSD = "AUDUSD"
        CADCHF = "CADCHF"
        CADJPY = "CADJPY"
        CHFDKK = "CHFDKK"
        CHFJPY = "CHFJPY"
        CHFNOK = "CHFNOK"
        CHFSEK = "CHFSEK"
        DAXEUR = "DAXEUR"
        DKKSEK = "DKKSEK"
        ESXEUR = "ESXEUR"
        EURAUD = "EURAUD"
        EURCAD = "EURCAD"
        EURCHF = "EURCHF"
        EURCZK = "EURCZK"
        EURDKK = "EURDKK"
        EURGBP = "EURGBP"
        EURHUF = "EURHUF"
        EURJPY = "EURJPY"
        EURNOK = "EURNOK"
        EURNZD = "EURNZD"
        EURPLN = "EURPLN"
        EURSEK = "EURSEK"
        EURTRY = "EURTRY"
        EURUSD = "EURUSD"
        GBPAUD = "GBPAUD"
        GBPCAD = "GBPCAD"
        GBPCHF = "GBPCHF"
        GBPDKK = "GBPDKK"
        GBPJPY = "GBPJPY"
        GBPNOK = "GBPNOK"
        GBPNZD = "GBPNZD"
        GBPPLN = "GBPPLN"
        GBPSEK = "GBPSEK"
        GBPUSD = "GBPUSD"
        NOKJPY = "NOKJPY"
        NOKSEK = "NOKSEK"
        NZDCAD = "NZDCAD"
        NZDCHF = "NZDCHF"
        NZDJPY = "NZDJPY"
        NZDSEK = "NZDSEK"
        NZDUSD = "NZDUSD"
        OILUSD = "OILUSD"
        SEKJPY = "SEKJPY"
        SMICHF = "SMICHF"
        USDCAD = "USDCAD"
        USDCHF = "USDCHF"
        USDCZK = "USDCZK"
        USDCNY = "USDCNY"
        USDDKK = "USDDKK"
        USDHKD = "USDHKD"
        USDHUF = "USDHUF"
        USDILS = "USDILS"
        USDJPY = "USDJPY"
        USDMXN = "USDMXN"
        USDNOK = "USDNOK"
        USDPLN = "USDPLN"
        USDRUB = "USDRUB"
        USDSEK = "USDSEK"
        USDSGD = "USDSGD"
        USDTRY = "USDTRY"
        USDZAR = "USDZAR"
        XAGUSD = "XAGUSD"
        XAUUSD = "XAUUSD"
        XPDUSD = "XPDUSD"
        XPTUSD = "XPTUSD"
        
        def allInstruments(self):
          # getting all attributes and excluding the all instruments method. 
          members = [attr for attr in dir(self) if not callable(attr) and not attr.startswith("__") and not attr.startswith("allInstruments")]
          return members
         
