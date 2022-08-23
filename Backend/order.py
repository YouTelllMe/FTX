from requests import get
import client_api
import time
import json 



def get_loop():
    # gets client orders from orders.txt, in form of json 
    # {'future':'BTC', cost: 0, 'target':100, 'tolerance':0.2, 'speed':3, 'side': 'positive'
    # 'status':'initiating'}
    with open('orders.txt', 'r') as orders:
        return(json.loads(orders.read())["orderlist"])

def update_costs(client_orders):
    for j in client_orders:
        account_orders = client_api.FtxClient(j['api_key'],j['api_secret'],j['subaccount']).get_account_info()["positions"]
        if float(j['target'])>0:
            j['side'] = "positive"
        else:
            j['side'] = "negative"
        j['cost'] = 0  
        for i in account_orders:
            if i['future'] == j['future']+'-PERP':
                if j['status'] == 'initiating':
                    if float(j['target'])>(-i['cost']):
                        j['side'] = "positive"
                    else:
                        j['side'] = 'negative'
                j['cost'] = -i['cost']

    return client_orders


def order_loop(client_orders_past):
    client_orders = update_costs(get_loop())
    for i in client_orders:
        if i['side'] == 'positive':
            if float(i['cost'])>float(i['target']):
                print('true')
                print(float(i['cost']),float(i['target']))
                client_orders.remove(i)
            else:
                client = client_api.FtxClient(i['api_key'],i['api_secret'],i['subaccount'])
                print('ran positive')
                #run positive 
                i['status'] = client.run_positive(i['future'],float(i['tolerance']),0.5,float(i['speed']))
        elif i['side'] == 'negative':
            if float(i['cost'])<float(i['target']):
                client_orders.remove(i)
            else:
                client = client_api.FtxClient(i['api_key'],i['api_secret'],i['subaccount'])
                print('ran negative')
                #run negative
                i['status'] = client.run_negative(i['future'],float(i['tolerance']),0.5,float(i['speed']))

    if len(client_orders_past) == len(get_loop()):
        print(client_orders)
        with open('orders.txt', 'w') as orders:
            orders.write(json.dumps({"orderlist": client_orders}))

def run_loop():
    while True:
        try:
            client_orders = update_costs(get_loop())
            if client_orders == []:
                time.sleep(1)
            else:
                order_loop(client_orders)
        except Exception as e:
            print(f"Exception: {e}")
            time.sleep(1)

run_loop()
