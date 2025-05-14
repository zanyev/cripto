import pandas as pd
import numpy as np
import requests
import asyncio
import httpx
from tqdm.asyncio import tqdm_asyncio
import json
import datetime as dt

base_url ="https://fapi.binance.com/" 
url_klines = "fapi/v1/continuousKlines"
url_exchange_info = "/fapi/v1/exchangeInfo"

n = 65

info = {'marginAsset':'USDT',
        'contractType':'PERPETUAL',
        'status':'TRADING',
         }

columns_df = ['open_time',
              'open',
              'high',
              'low',
              'close',
              'volume',
              'close_time',
              'quote_asset_volume',
              'number_of_trades',
              'taker_buy_volume',
              'taker_buy_quote_asset_volume',
              'ignore']



SEM = asyncio.Semaphore(20)  # Limita a 10 requisições simultâneas

async def get_data(client,symbol,n):
    params = {
        'pair': f'{symbol}',
        'contractType': 'PERPETUAL',
        'interval': '1d',  # Intervalo das velas (exemplo: 1h para uma hora)
        'limit': n         # Número de velas a serem retornadas
    }
    async with SEM:  # Garante que só 10 tarefas rodem simultaneamente
        res = await client.get(base_url + url_klines, params=params)
        return symbol,res.json()

def get_exchange_info(info):
    def filter(r,info=info):
        check = []
        for k,v in info.items():
            check.append(r.get(k) == v)
        if all(check):
            return True
        else:
            return False
    
    res = requests.get(base_url + url_exchange_info)
    tradable_symbols = res.json()['symbols']
    filtered_symbols = [r for r in tradable_symbols if filter(r,info)]

    return filtered_symbols

def transf_price_df(df):
    df = df.copy()
    df = df[['open','high','low','close','volume','close_time']]
    df['close_time'] = pd.to_datetime(df['close_time'],unit='ms')
    df = df.iloc[:-1]
    df['log_close'] = np.log(df['close'].astype('float'))
    return df

async def fetch_all_data(symbols, n):
    async with httpx.AsyncClient() as client:
        tasks = [get_data(client, symbol['symbol'], n) for symbol in symbols]
        results = [await f for f in tqdm_asyncio.as_completed(tasks)]
    return results

# Exemplo de uso
async def main():
    results = await fetch_all_data(exchange_info, 65)
    symbols_price_info = {symbol_info[0]:symbol_info[1] for symbol_info in results}
    indicador_cumulative_retuns = {}
    for s,prices in list(symbols_price_info.items()):
        df_price = pd.DataFrame(prices,columns=columns_df).dropna()
        if len(df_price) == n:
            price_df_transformed = transf_price_df(df_price)
            returns = price_df_transformed['log_close'].diff().iloc[1:]
            cumulative_returns = returns.sum()*100
            indicador_cumulative_retuns[s] = round(cumulative_returns,4)

    series_indicador = pd.Series(indicador_cumulative_retuns)
    series_indicador = series_indicador.sort_values()
    series_indicador.name = 'cumulative_log_returns_64d'
    series_indicador.index.name = 'ativos'
    series_indicador = series_indicador.to_frame()
    series_indicador['date'] = dt.date.today().strftime('%Y-%m-%d')
    series_indicador.to_csv('./assets/indicador.csv')



# puxa os dados de symbolos conforme informacoes e dps baixa os precos para os ultimos 65 dias.
#salva em banco de dados os registros e dps processamos essas infos
exchange_info = get_exchange_info(info)
with open('./assets/trade_universe.json','w') as f:
    f.write(json.dumps(exchange_info))
    f.close()

asyncio.run(main())




