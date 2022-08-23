import client_api
import time
import os
from datetime import datetime, timedelta
import pandas as pd


#parameters
PRESET = 0
INTERVAL = 60
DATA_PATH = os.path.join("data","rates_data")


def main(data_path=DATA_PATH):
    """
    fetches latest hour of data
    """
    tn = int(time.time())
    for coin in client_api.client.coins:
        coin_path = os.path.join(data_path,coin+".csv")
        future_name = coin+"-PERP"
        data = client_api.client.get_funding_rates(future_name, start_time=tn-3600, end_time=tn)
        df = pd.DataFrame(data)
        df.to_csv(coin_path,mode='a', index=False, header=False)
    return 1

if __name__ == "__main__":
    time.sleep(PRESET)
    print(f"Initializing Update: PRESET {PRESET} Seconds")
    last_updated = datetime(2000,1,1)
    while True:
        time_now = datetime.now()
        if last_updated+timedelta(seconds=3600)<=time_now:
            last_updated = time_now
            print(f'Update Commencing: {time_now}')
            if main():
                print(f'Update Success.')
        time.sleep(INTERVAL)