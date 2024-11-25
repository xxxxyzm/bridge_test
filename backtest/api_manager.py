import tushare as ts
import pandas as pd
from .config import Config
class ApiManager:
    def init(self):
        self.config=Config()
        self.account=tu.pro_api(self.config.api_key)
    def get_stock_data(self,code:str,start_date:int,end_date:int)->pd.DataFrame:

