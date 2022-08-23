import enum
import string
import time
from turtle import color, position
import urllib.parse
from typing import Optional, Dict, Any, List

from requests import Request, Session, Response
import hmac
import matplotlib.pyplot as plt
from dateutil import parser
import datetime
from matplotlib import font_manager
import json
import sqlite3


class FtxClient:
    _ENDPOINT = 'https://ftx.com/api/'

    def __init__(self, api_key=None, api_secret=None, subaccount_name=None) -> None:
        self._session = Session()
        self._api_key = api_key
        self._api_secret = api_secret
        self._subaccount_name = subaccount_name
        self.markets_list = list(set([x['baseCurrency'] for x in self.get_markets()]))
        self.future_list=list(set([x['underlying'] for x in self.get_all_futures()]))
        self.futures = list(set([x['underlying'] for x in self.get_all_futures()]))
        self.coins = [x for x in self.future_list if x in self.markets_list]

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        try:
            return self._request('GET', path, params=params)
        except Exception as e:
            msg = str(e).split(':')[0]
            if msg == "No such subaccount" or msg == "Not logged in" or msg == "No such future":
                return False
            else:
                print (f'failure: ({e})')
                return self._get(path,params=params)
            

    def _post(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        try:
            return self._request('POST', path, json=params)
        except Exception as e:
            print (f'failure: {e}')
            return self._post(path,json=params)

    def _delete(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        try:
            return self._request(path, json=params)
        except Exception as e:
            print (f'failure: {e}')
            return self._delete(path,json=params)

    def _request(self, method: str, path: str, **kwargs) -> Any:
        request = Request(method, self._ENDPOINT + path, **kwargs)
        self._sign_request(request)
        response = self._session.send(request.prepare())
        return self._process_response(response)

    def _sign_request(self, request: Request) -> None:
        ts = int(time.time() * 1000)
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
        if prepared.body:
            signature_payload += prepared.body
        signature = hmac.new(self._api_secret.encode(), signature_payload, 'sha256').hexdigest()
        request.headers['FTX-KEY'] = self._api_key
        request.headers['FTX-SIGN'] = signature
        request.headers['FTX-TS'] = str(ts)
        if self._subaccount_name:
            request.headers['FTX-SUBACCOUNT'] = urllib.parse.quote(self._subaccount_name)

    def _process_response(self, response: Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if not data['success']:
                raise Exception(data['error'])
            return data['result']

    def get_all_futures(self) -> List[dict]:
        return self._get('futures')

    def get_future(self, future_name: str = None) -> dict:
        return self._get(f'futures/{future_name}')

    def get_markets(self) -> List[dict]:
        return self._get('markets')

    def get_market(self, market) -> List[dict]:
        return self._get(f'markets/{market}')

    def get_orderbook(self, market: str, depth: int = None) -> dict:
        return self._get(f'markets/{market}/orderbook', {'depth': depth})

    def get_trades(self, market: str, start_time: float = None, end_time: float = None) -> dict:
        return self._get(f'markets/{market}/trades', {'start_time': start_time, 'end_time': end_time})

    def get_account_info(self) -> dict:
        return self._get(f'account')

    def get_open_orders(self, market: str = None) -> List[dict]:
        return self._get(f'orders', {'market': market})

    def get_order_history(
        self, market: str = None, side: str = None, order_type: str = None,
        start_time: float = None, end_time: float = None
    ) -> List[dict]:
        return self._get(f'orders/history', {
            'market': market,
            'side': side,
            'orderType': order_type,
            'start_time': start_time,
            'end_time': end_time
        })

    def get_conditional_order_history(
        self, market: str = None, side: str = None, type: str = None,
        order_type: str = None, start_time: float = None, end_time: float = None
    ) -> List[dict]:
        return self._get(f'conditional_orders/history', {
            'market': market,
            'side': side,
            'type': type,
            'orderType': order_type,
            'start_time': start_time,
            'end_time': end_time
        })

    def modify_order(
        self, existing_order_id: Optional[str] = None,
        existing_client_order_id: Optional[str] = None, price: Optional[float] = None,
        size: Optional[float] = None, client_order_id: Optional[str] = None,
    ) -> dict:
        assert (existing_order_id is None) ^ (existing_client_order_id is None), \
            'Must supply exactly one ID for the order to modify'
        assert (price is None) or (size is None), 'Must modify price or size of order'
        path = f'orders/{existing_order_id}/modify' if existing_order_id is not None else \
            f'orders/by_client_id/{existing_client_order_id}/modify'
        return self._post(path, {
            **({'size': size} if size is not None else {}),
            **({'price': price} if price is not None else {}),
            ** ({'clientId': client_order_id} if client_order_id is not None else {}),
        })

    def get_conditional_orders(self, market: str = None) -> List[dict]:
        return self._get(f'conditional_orders', {'market': market})

    def place_order(self, market: str, side: str, price: float, size: float, type: str = 'limit',
                    reduce_only: bool = False, ioc: bool = False, post_only: bool = False,
                    client_id: str = None, reject_after_ts: float = None) -> dict:
        return self._post('orders', {
            'market': market,
            'side': side,
            'price': price,
            'size': size,
            'type': type,
            'reduceOnly': reduce_only,
            'ioc': ioc,
            'postOnly': post_only,
            'clientId': client_id,
            'rejectAfterTs': reject_after_ts
        })

    def place_conditional_order(
        self, market: str, side: str, size: float, type: str = 'stop',
        limit_price: float = None, reduce_only: bool = False, cancel: bool = True,
        trigger_price: float = None, trail_value: float = None
    ) -> dict:
        """
        To send a Stop Market order, set type='stop' and supply a trigger_price
        To send a Stop Limit order, also supply a limit_price
        To send a Take Profit Market order, set type='trailing_stop' and supply a trigger_price
        To send a Trailing Stop order, set type='trailing_stop' and supply a trail_value
        """
        assert type in ('stop', 'take_profit', 'trailing_stop')
        assert type not in ('stop', 'take_profit') or trigger_price is not None, \
            'Need trigger prices for stop losses and take profits'
        assert type not in ('trailing_stop',) or (trigger_price is None and trail_value is not None), \
            'Trailing stops need a trail value and cannot take a trigger price'

        return self._post('conditional_orders', {
            'market': market,
            'side': side,
            'triggerPrice': trigger_price,
            'size': size,
            'reduceOnly': reduce_only,
            'type': 'stop',
            'cancelLimitOnTrigger': cancel,
            'orderPrice': limit_price
        })

    def cancel_order(self, order_id: str) -> dict:
        return self._delete(f'orders/{order_id}')

    def cancel_orders(
        self, market_name: str = None,
        conditional_orders: bool = False, limit_orders: bool = False
    ) -> dict:
        return self._delete(f'orders', {
            'market': market_name,
            'conditionalOrdersOnly': conditional_orders,
            'limitOrdersOnly': limit_orders
        })

    def get_fills(self, market: str = None, start_time: float = None,
        end_time: float = None, min_id: int = None, order_id: int = None
    ) -> List[dict]:
        return self._get('fills', {
            'market': market,
            'start_time': start_time,
            'end_time': end_time,
            'minId': min_id,
            'orderId': order_id
        })

    def get_balances(self) -> List[dict]:
        return self._get('wallet/balances')

    def get_total_usd_balance(self) -> int:
        total_usd = 0
        balances = self._get('wallet/balances')
        for balance in balances:
            total_usd += balance['usdValue']
        return total_usd

    def get_all_balances(self) -> List[dict]:
        return self._get('wallet/all_balances')

    def get_total_account_usd_balance(self) -> int:
        total_usd = 0
        all_balances = self._get('wallet/all_balances')
        for wallet in all_balances:
            for balance in all_balances[wallet]:
                total_usd += balance['usdValue']
        return total_usd

    def get_positions(self, show_avg_price: bool = False) -> List[dict]:
        return self._get('positions', {'showAvgPrice': show_avg_price})

    def get_position(self, name: str, show_avg_price: bool = False) -> dict:
        return next(filter(lambda x: x['future'] == name, self.get_positions(show_avg_price)), None)

    def get_all_trades(self, market: str, start_time: float = None, end_time: float = None) -> List:
        ids = set()
        limit = 100
        results = []
        while True:
            response = self._get(f'markets/{market}/trades', {
                'end_time': end_time,
                'start_time': start_time,
            })
            deduped_trades = [r for r in response if r['id'] not in ids]
            results.extend(deduped_trades)
            ids |= {r['id'] for r in deduped_trades}
            print(f'Adding {len(response)} trades with end time {end_time}')
            if len(response) == 0:
                break
            end_time = min(parser.parse(t['time']) for t in response).timestamp()
            if len(response) < limit:
                break
        return results

    def get_historical_prices(
        self, market: str, resolution: int = 300, start_time: float = None,
        end_time: float = None
    ) -> List[dict]:
        return self._get(f'markets/{market}/candles', {
            'resolution': resolution,
            'start_time': start_time,
            'end_time': end_time
        })

    def get_last_historical_prices(self, market: str, resolution: int = 300) -> List[dict]:
        return self._get(f'markets/{market}/candles/last', {'resolution': resolution})

    def get_borrow_rates(self) -> List[dict]:
        return self._get('spot_margin/borrow_rates')

    def get_borrow_history(self, start_time: float = None, end_time: float = None) -> List[dict]:
        return self._get('spot_margin/borrow_history', {'start_time': start_time, 'end_time': end_time})

    def get_lending_history(self, start_time: float = None, end_time: float = None) -> List[dict]:
        return self._get('spot_margin/lending_history', {
            'start_time': start_time,
            'end_time': end_time
        })

    def get_expired_futures(self) -> List[dict]:
        return self._get('expired_futures')

    def get_coins(self) -> List[dict]:
        return self._get('wallet/coins')

    def get_future_stats(self, future_name: str) -> dict:
        return self._get(f'futures/{future_name}/stats')

    def get_single_market(self, market: str = None) -> dict:
        return self._get(f'markets/{market}')

    def get_market_info(self, market: str = None) -> dict:
        return self._get('spot_margin/market_info', {'market': market})

    def get_trigger_order_triggers(self, conditional_order_id: str = None) -> List[dict]:
        return self._get(f'conditional_orders/{conditional_order_id}/triggers')

    def get_trigger_order_history(self, market: str = None) -> List[dict]:
        return self._get('conditional_orders/history', {'market': market})

    def get_staking_balances(self) -> List[dict]:
        return self._get('staking/balances')

    def get_stakes(self) -> List[dict]:
        return self._get('staking/stakes')

    def get_staking_rewards(self, start_time: float = None, end_time: float = None) -> List[dict]:
        return self._get('staking/staking_rewards', {
            'start_time': start_time,
            'end_time': end_time
        })

    def place_staking_request(self, coin: str = 'SRM', size: float = None) -> dict:
        return self._post('srm_stakes/stakes',)

    def get_funding_rates(self, future: str = None, start_time: float = None, end_time: float = None)-> List[dict]:
        return self._get('funding_rates', {
            'future': future,
            'start_time': start_time,
            'end_time': end_time
        })

    def get_all_funding_rates(self, start_time=None, end_time=None) -> List[dict]:
        return self._get('funding_rates', {
            'start_time': start_time,
            'end_time': end_time,
        })

    def get_funding_payments(self, start_time: float = None, end_time: float = None, future: str = None) -> List[dict]:
        return self._get('funding_payments', {
            'start_time': start_time,
            'end_time': end_time,
            'future':future
        })

    def create_subaccount(self, nickname: str) -> dict:
        return self._post('subaccounts', {'nickname': nickname})

    def get_subaccount_balances(self, nickname: str) -> List[dict]:
        return self._get(f'subaccounts/{nickname}/balances')

    def get_deposit_address(self, ticker: str) -> dict:
        return self._get(f'wallet/deposit_address/{ticker}')

    def get_deposit_history(self) -> List[dict]:
        return self._get('wallet/deposits')

    def get_withdrawal_fee(self, coin: str, size: int, address: str, method: str = None, tag: str = None) -> Dict:
        return self._get('wallet/withdrawal_fee', {
            'coin': coin,
            'size': size,
            'address': address,
            'method': method,
            'tag': tag
        })

    def get_withdrawals(self, start_time: float = None, end_time: float = None) -> List[dict]:
        return self._get('wallet/withdrawals', {'start_time': start_time, 'end_time': end_time})

    def get_saved_addresses(self, coin: str = None) -> dict:
        return self._get('wallet/saved_addresses', {'coin': coin})

    def submit_fiat_withdrawal(self, coin: str, size: int, saved_address_id: int, code: int = None) -> Dict:
        return self._post('wallet/fiat_withdrawals', {
        'coin': coin,
        'size': size,
        'savedAddressId': saved_address_id,
        'code': code
    })

    def get_latency_stats(self, days: int = 1, subaccount_nickname: str = None) -> Dict:
        return self._get('stats/latency_stats', {'days': days, 'subaccount_nickname': subaccount_nickname})

    def positive_dif(self, future: str = None, market: str = None):
        future_bid = float(self.get_future(future)['bid'])
        market_ask = float(self.get_single_market(market)['ask'])

        difference = (future_bid-market_ask)/market_ask*100
        return (difference)


    def negative_dif(self, future: str = None, market: str = None):
        future_ask = float(self.get_future(future)['ask'])
        market_bid = float(self.get_single_market(market)['bid'])
        difference = (future_ask-market_bid)/market_bid*100
        return (difference)


    def run_positive (self, coin, tolerance, wait, speed):
        if speed<0:
            speed=1
        elif speed>10:
            speed=10
            
        size = self.coin_min(f'{coin}/USD')*speed
        future = f'{coin}-PERP'
        market = f'{coin}/USD'
        future_bid = float(self.get_future(future)['bid'])
        market_ask = float(self.get_single_market(market)['ask'])
        difference = (future_bid-market_ask)/market_ask*100
        #sell future
        #buy market
        if self.positive_dif(future, market)>tolerance:
            try:
                self.place_order(f'{coin}/USD', 'buy', None, size, 'market',
                        False, False, False, None, None)
                self.place_order(f'{coin}-PERP', 'sell', None, size, 'market',
                            False, False, False, None, None)
                time.sleep(wait)
                return ('success')
            except Exception as e:
                time.sleep(wait)
                return (f'failure: {e}')
        else:
            time.sleep(wait)
            return('failure: condition unmet', difference)
                    

    def run_negative (self, coin, tolerance, wait,speed):
        if speed<0:
            speed=1
        elif speed>10:
            speed=10
            
        size = self.coin_min(f'{coin}/USD') * speed

        future = f'{coin}-PERP'
        market = f'{coin}/USD'
        future_ask = float(self.get_future(future)['ask'])
        market_bid = float(self.get_single_market(market)['bid'])
        difference = (future_ask-market_bid)/market_bid*100

        #buy future
        #sell market
        if self.negative_dif(future, market) < tolerance:
            try:
                self.place_order(f'{coin}/USD', 'sell', None, size, 'market',
                        False, False, False, None, None)   
                self.place_order(f'{coin}-PERP', 'buy', None , size, 'market',
                            False, False, False, None, None)
                time.sleep(wait)
                return ('success')
            except Exception as e:
                time.sleep(wait)
                return (f'failure: {e}')
        else:
            time.sleep(wait)
            return('failure: condition unmet', difference)


    def graph_rates(self, future: str="BTC"):
        xvalues = []
        yvalues = []
        colors =[]
        tn = int(time.time())
        funding_rates = self.get_funding_rates(f'{future}-PERP', tn-1728000, tn)
        
        for i in funding_rates[::-1]:
            xvalues.append(i["time"])
            yvalues.append(round(float(i['rate'])*876000,2))

        for i in yvalues:
            if i>0:
                colors.append('green')
            elif i==0:
                colors.append('black')
            else:
                colors.append('red')

        return ({'xvalues':xvalues, 'yvalues':yvalues, 'colors':colors})

    def fund_overtime(self, coin: str="BTC", days: int=20):
        future = f'{coin}-PERP'
        tn = int(time.time())
        funding_rates = self.get_funding_rates(future, tn-(days*86400), tn)
        total_rate = 0

        for i in funding_rates:
            total_rate+=float(i['rate'])*636000
        
        average_rate = round(total_rate/len(funding_rates),2)
        return (coin, average_rate)

    def coin_min(self, market):
        return (self.get_market(market)['minProvideSize'])

    def graph_payments(self, future):
        
        test_date = datetime.datetime(2020, 5, 17)
        tn = int(time.time())
        xvalues = []
        yvalues = []
        data = self.get_funding_payments(tn-(1728000),tn, f'{future}-PERP')
        history = self.borrow_history(future)
        for j in data:
            date = parser.parse(j['time'])
            if test_date.date() != date.date():
                xvalues.append(j['time'])
                test_date = date
            j['time'] = date
            
        
        for i in xvalues:
            payment = 0
            for j in data:
                if j['time'].date() == parser.parse(i).date():
                    payment-=j['payment']
            yvalues.append(payment)


        for index,value in enumerate(xvalues):
            for index2,value2 in enumerate(history[1]):
                if parser.parse(value).date() == value2:
                    yvalues[index]+=history[0][index2]
        
        xvalues = xvalues[::-1]
        yvalues = yvalues[::-1]

        colors = []
        for i in yvalues:
            if i>0:
                colors.append('green')
            elif i<0: 
                colors.append('red')
            else:
                colors.append('black')
        
        return ({'xvalues':xvalues, 'yvalues':yvalues, 'colors':colors})


    def borrow_history(self, coin):
        test_date = datetime.datetime(2020, 5, 17)
        tn = int(time.time())
        history = self.get_borrow_history(tn-1728000, tn)
        xvalues = []
        yvalues = [] 

        for i in history[:]:
            if i['coin'] != coin:
                history.remove(i)

        for j in history:
            j['time'] = parser.parse(j['time'])
            date = j['time']
            if test_date.date() != date.date():
                xvalues.append(date.date())
                test_date = date
        
        for i in xvalues:
            feeUsd = 0
            for j in history:
                if j['time'].date() == i and j['coin'] == coin:
                    feeUsd-=j['feeUsd']
            yvalues.append(feeUsd)
        return [yvalues,xvalues]

    def graph_history(self,coin):
        data = self.borrow_history(coin)
        return ({'yvalues': data[0][::-1], 'xvalues':data[1][::-1]})

    
    def payment_list(self):
        payment_history = self.get_funding_payments()
        futures = []
        for i in payment_history:
            key = i['future'].split('-')[0]
            if key not in futures:
                futures.append(key)
        return({'futures': futures})

    def get_total(self):
        coins = self.payment_list()['futures']
        data = {'coins':coins}
        for coin in coins:
            payment = self.graph_payments(coin)
            data[f'{coin}'] = {'xvalues': payment['xvalues'], 'yvalues':[payment['xvalues'], payment['yvalues']]}
        return data
    
    def get_config(self):
        with open("api_config.txt", "r") as config:
            return (json.loads(config.read()))
    
    def table_data(self):

        conn = sqlite3.connect("rates_data.db")
        c = conn.cursor()

        #market infos; separated into future and spot info with name as key and ask, bid, volume as attributes
        market_data = self.get_markets()
        future_data = self.get_all_futures()
        rates_data = self.get_all_funding_rates(start_time=(int(time.time())-3600))
        borrow_data = self.get_borrow_rates()

        spot_info = {}
        future_info = {}
        rate_info = {}
        borrow_info = {}

        for market in market_data:
            if market["quoteCurrency"] == "USD":
                spot_name = market["baseCurrency"]
                spot_info[f"{spot_name}"] = {'ask':market['ask'], 'bid':market['bid'],'volumeUsd24h':market['volumeUsd24h']}

        for future in future_data: 
            if future['type'] == "perpetual":
                future_name = future["underlying"]
                future_info[f"{future_name}"] = {'ask':future['ask'], 'bid':future['bid'],'volumeUsd24h':future['volumeUsd24h']}

        for rate in rates_data:
            rate_name = rate["future"]
            rate_info[f'{rate_name}'] = rate['rate']

        for entry in borrow_data:
            entry_name = entry['coin']
            borrow_info[f'{entry_name}'] = {"current":entry['previous'],"estimate":entry['estimate']}

        all_data=[]

        #negative
        # future_ask = float(self.get_future(future)['ask'])
        # market_bid = float(self.get_single_market(market)['bid'])
        # difference = (future_ask-market_bid)/market_bid*100

        #positive
        # future_bid = float(self.get_future(future)['bid'])
        # market_ask = float(self.get_single_market(market)['ask'])
        # difference = (future_bid-market_ask)/market_ask*100


        for coin in self.coins:
            try:
                coin_future_ask = future_info[f'{coin}']['ask']
                coin_future_bid = future_info[f'{coin}']['bid']
                coin_spot_ask = spot_info[f'{coin}']['ask']
                coin_spot_bid = spot_info[f'{coin}']['bid']
                rate = rate_info[f'{coin}-PERP']


                for letter in coin[:]:
                    if letter in '0123456789' or letter == ' ':
                        coin = coin.replace(letter, "")
                table_name = coin

                c.execute(f"""SELECT rate FROM {table_name}""")
                hundred_rates = c.fetchmany(2400)[:]
                conn.commit()

                hundred_day_data = [float(x[0]) for x in hundred_rates]
                fourty_day_data = hundred_day_data[:960]
                twenty_day_data = fourty_day_data[:480]
                seven_day_data = fourty_day_data[:168]
                hundred_average = round(sum(hundred_day_data)*365,2)
                fourty_average = round(sum(fourty_day_data)*912.5,2)
                twenty_average = round(sum(twenty_day_data)*1825,2)
                seven_average = round(sum(seven_day_data)*5214.28571,2)


                try:
                    borrow = borrow_info[f'{coin}']
                except:
                    borrow = {"current":0,"estimate":0}
                
                all_data.append({'name':f'{coin}', 'rate':round(rate*876000,2), 'negative':round((coin_future_ask-coin_spot_bid)/coin_spot_bid*100,2), 
                'positive':round((coin_future_bid-coin_spot_ask)/coin_spot_ask*100,2),'future_volume':round(future_info[f'{coin}']['volumeUsd24h'])
                ,'spot_volume':round(spot_info[f'{coin}']['volumeUsd24h']),'current_borrow':round(borrow['current']*876000,2),'estimated_borrow':
                round(borrow['estimate']*876000,2), '100 Average':hundred_average,'40 Average':fourty_average,'20 Average':twenty_average,'7 Average':seven_average})
            except Exception as e:
                print(e)
                
        conn.close()
        return all_data

        #current and estimated borrow rates
        # print(self.get_borrow_rates())



with open("api_config.txt", "r") as config:
    account = json.loads(config.read())
    client_two = FtxClient(account['api_key'],account['api_secret'], account['subaccount'])

if __name__ == "__main__":
    print(client_two.borrow_history("HT"))