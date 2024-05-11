#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  8 22:48:26 2024

@author: yfh
"""



# from tqdm import tqdm
# import requests
# import json
# import pandas as pd
# import time
# from datetime import datetime
# import pytz
# import concurrent.futures
# from requests.adapters import HTTPAdapter
# from requests.packages.urllib3.util.retry import Retry
# import requests
from dextools_python import DextoolsAPIV2
dextools = DextoolsAPIV2('WEAb2BMeqe6Dgr5DxUUDe3hRhONZo77kaFZ92U6l', plan="trial")


token_price = dextools.get_token_price("solana", "CLFR99t87xxRQtEtkWkrGj82BiJ2228h7JPgkLWiZ45o")
print(token_price)

