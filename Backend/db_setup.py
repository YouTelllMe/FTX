import client_api
import time
import os
import pandas as pd


tn = int(time.time())

DATA_PATH = os.path.join("data","rates_data")

def main(data_path=DATA_PATH):
    """
    fetches 100 days of rates data for each perpetual future
    """
    tn = int(time.time())
    if not os.path.isdir(data_path):
        os.makedirs(data_path)
    for coin in client_api.client.coins:
        coin_path = os.path.join(data_path,coin+".csv")
        future_name = coin+"-PERP"
        data = client_api.client.get_funding_rates(future_name)+client_api.client.get_funding_rates(future_name,tn-(40*86400),tn-(20*86400))+client_api.client.get_funding_rates(future_name,tn-(60*86400),tn-(40*86400))+client_api.client.get_funding_rates(future_name,tn-(80*86400),tn-(60*86400))+client_api.client.get_funding_rates(future_name,tn-(100*86400),tn-(80*86400))
        df = pd.DataFrame(data)
        df = df.reindex(index=df.index[::-1])
        df.to_csv(coin_path,mode='w', index=False, header=False)
        print(f"{coin}: success")
    return 1

if __name__ == "__main__":
    main()