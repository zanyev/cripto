import requests
import time
import hashlib
import hmac
import os
import pandas as pd
from decimal import Decimal
import json
import math
import time

# Replace these with your API key and secret
API_KEY = os.environ.get('API_Key')
API_SECRET = os.environ.get('Secret_Key')
BASE_URL = 'https://fapi.binance.com'

def create_signature(query_string, secret):
    return hmac.new(secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

def get_account_info():
    endpoint = '/fapi/v2/account'
    timestamp = int(time.time() * 1000)
    query_string = f'timestamp={timestamp}'
    signature = create_signature(query_string, API_SECRET)
    headers = {
        'X-MBX-APIKEY': API_KEY
    }
    url = f'{BASE_URL}{endpoint}?{query_string}&signature={signature}'
    response = requests.get(url, headers=headers)
    return response.json()


def create_market_order(symbol, qty, side, zeragem):
    side_str = None
    if side == 1:
        side_str = 'BUY'
    elif side == 0:
        side_str = 'SELL'
    else:
        return {"error": "Invalid side. Use 1 for BUY and 0 for SELL."}
    
    if symbol in list(zeragem.keys()):
        # Define the parameters for the order
        params = {
            'symbol': symbol,
            'side': side_str,
            'type': 'MARKET',
            'quantity':zeragem[symbol],
            'timestamp': int(time.time() * 1000)
        }
    else:
        # Define the parameters for the order
        params = {
            'symbol': symbol,
            'side': side_str,
            'type': 'MARKET',
            'quantity': qty,
            'timestamp': int(time.time() * 1000)
        }

    endpoint = '/fapi/v1/order'
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    signature = create_signature(query_string, API_SECRET)
    params['signature'] = signature

    headers = {
        'X-MBX-APIKEY': API_KEY
    }

    url = f'{BASE_URL}{endpoint}'
    response = requests.post(url, headers=headers, params=params)
    return response.json()


def change_leverage(symbol, leverage):
    # Define the parameters for the request
    params = {
        'symbol': symbol,
        'leverage': leverage,
        'timestamp': int(time.time() * 1000)
    }

    endpoint = '/fapi/v1/leverage'
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    signature = create_signature(query_string, API_SECRET)
    params['signature'] = signature

    headers = {
        'X-MBX-APIKEY': API_KEY
    }

    url = f'{BASE_URL}{endpoint}'
    response = requests.post(url, headers=headers, params=params)
    return response.json()

n_ativos = 14
min_tradable_notional = 5
effective_leverage = 10
max_notional = 300
account_info = get_account_info()
indicator = pd.read_csv('./assets/indicador.csv',index_col=0)


account_assets = account_info['assets']
account_positions = account_info['positions']
usdt_funds = [d for d in account_assets if d['asset'] == 'USDT'][0]

indicator = indicator.sort_values('cumulative_log_returns_64d')

buy_list = list(indicator.head(n_ativos).index)
sell_list = list(indicator.tail(n_ativos).index)


def CreateOrderBasket(buy_list,sell_list,account_positions,max_notional = max_notional):

    def filtro_posicoes(buy_list,sell_list,account_positions):
        all_symbols = buy_list + sell_list
        posicoes_compra = [p for p in account_positions if p['symbol'] in buy_list]
        posicoes_venda = [p for p in account_positions if p['symbol'] in sell_list]
        posicoes_zeragem = [p for p in account_positions if p['symbol'] not in all_symbols]


        return posicoes_compra,posicoes_venda,posicoes_zeragem
    
    def CalcularNotional(posicoes_compra,posicoes_venda,posicoes_zeragem,max_notional):
        basket_order = {}

        target_compra = {p['symbol']:(max_notional/2)/len(posicoes_compra) for p in posicoes_compra}
        target_venda = {p['symbol']:((max_notional/2)/len(posicoes_venda)) *-1 for p in posicoes_venda}
        target_zeragem = {p['symbol']: 0 for p in posicoes_zeragem}

        target = target_zeragem | target_venda | target_compra

        all_positions = posicoes_zeragem + posicoes_venda + posicoes_compra 
        all_positions_notional = {a['symbol']:a['notional'] for a in all_positions}

        for a in target.keys():
            basket_order[a] = float(target[a]) - float(all_positions_notional[a])
        return basket_order, posicoes_zeragem
    
    
    posicoes_compra,posicoes_venda,posicoes_zeragem = filtro_posicoes(buy_list,sell_list,account_positions)
    basket = CalcularNotional(posicoes_compra,posicoes_venda,posicoes_zeragem,max_notional)

    return basket

basket,zeragem_posicoes = CreateOrderBasket(buy_list,sell_list,account_positions)
zeragem = {}
for p in zeragem_posicoes:
    zeragem[p['symbol']] = abs(Decimal(p['positionAmt']))

basket_filtrada = {a:n for a,n in basket.items() if abs(float(n)) > min_tradable_notional}

#change levarage to target leverage
for s in basket_filtrada.keys():
    change_leverage(s,effective_leverage)


with open('./assets/trade_universe.json','r') as f:
    symbol_details = json.loads(f.read())
    f.close()


def get_symbol_min_qty(symbol_details):
    symbol_min_qty = {}
    for sd in symbol_details:
        symbol_name = sd['symbol']
        min_tradable_qty = sd['filters'][1]['minQty'] # menor qtidade tradavel
        symbol_min_qty[symbol_name]  = min_tradable_qty
    return symbol_min_qty

def get_symbol_min_notional(symbol_details):
    symbol_min_notional = {}
    for sd in symbol_details:
        symbol_name = sd['symbol']
        min_notional = sd['filters'][5]['notional'] # menor qtidade tradavel
        symbol_min_notional[symbol_name]  = min_notional
    return symbol_min_notional

def get_latest_price():
    price_url = '/fapi/v2/ticker/price'
    url = f'{BASE_URL}{price_url}'
    prices  = requests.get(url).json()
    prices = {p['symbol']:p['price'] for p in prices}
    return prices


min_tradable_qty = get_symbol_min_qty(symbol_details)
latest_prices = get_latest_price()
#min_notional_tradable = get_symbol_min_notional(symbol_details)


max_qtities = {k:v/(float(latest_prices[k]) * 1.02) for k,v in basket_filtrada.items()}
trades = {}
for k,v in max_qtities.items():
    trades[k] = {
        'qty': Decimal(str(math.floor(abs(v/ float(min_tradable_qty[k]))))) * Decimal(min_tradable_qty[k]),
        'side': v > 0
    }

order_status = {}
for s,info in list(trades.items())[0:]:

    record = create_market_order(symbol=s,qty=info['qty'],side=info['side'],zeragem = zeragem)
    record = record
    order_status[s] = {
        'record':record,
        'qty':info['qty'],
        'side':info['side']
        }
    time.sleep(0.5)


df_order_status = pd.DataFrame(order_status)
df_order_status.index.name = 'details'
df_order_status.to_csv('./assets/order_status.csv')




