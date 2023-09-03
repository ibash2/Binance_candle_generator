import requests
import pandas as pd
from pandas import DataFrame
from lightweight_charts import Chart
import websocket
import json
import pandas_ta as ta


def get_histories():
    params = {
        'symbol': 'BTCUSDT',
        'interval': '1s',
        'limit': 500
    }
    res = requests.get('https://api.binance.com/api/v3/klines', params=params)

    candle_data = res.json()

    df = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])

    for i in candle_data:
        new_row = {
            'date': pd.to_datetime(i[0], unit='ms'),
            'open': float(i[1]),
            'high': float(i[2]),
            'low': float(i[3]),
            'close': float(i[4]),
            'volume': float(i[5]),
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    return df


#
def calculate_sma(df, period: int = 50):
    return pd.DataFrame({
        'time': df['date'],
        f'SMA {period}': df['close'].rolling(window=period).mean()
    }).dropna()

def smr(df):

    # new_data= {
    #     'sma': a,
    #     'date': b
    # }
    # df.update([new_data])
    # df['sma'] = ta.sma(get_histories()['close'], length=20)
    # df['date'] = get_histories()['date']


    # sma = df.dropna()
    # print(df)
    return pd.DataFrame({
        'time': df['date'],
        'sma': ta.sma(df['close'], length=20)
    }).dropna()


if __name__ == '__main__':

    sm = pd.DataFrame(columns=['date', 'sma'])

    sma = pd.DataFrame(columns=['date', 'sma'])
    sma['sma'] = ta.sma(get_histories()['close'], length=20)
    sma['date'] = get_histories()['date']
    sma = sma.dropna()

    chart = Chart(
        height=1050,
        x=1125,
        y=0
    )
    chart.legend(visible=True)
    chart.set(get_histories())
    line = chart.create_line('sma')
    line.set(sma)
    candlestick_data = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    chart.show()



    def on_message(ws, message):
        global candlestick_data
        data = json.loads(message)
        sm = pd.DataFrame(columns=['date', 'sma'])

        if 'k' in data and data['k']['x'] == True:
            new_candle = data['k']
            new_row = {
                'date': pd.to_datetime(data['E'], unit='ms'),
                'open': float(new_candle['o']),
                'high': float(new_candle['h']),
                'low': float(new_candle['l']),
                'close': float(new_candle['c']),
                'volume': float(new_candle['v']),
            }
            candlestick_data['date'] = pd.to_datetime(candlestick_data['date'])
            candlestick_data = pd.concat([candlestick_data, pd.DataFrame([new_row])], ignore_index=True)
            # candlestick_data = pd.DataFrame([new_row])
            chart.update(candlestick_data.iloc[-1])

            # print(candlestick_data)
            s = smr(candlestick_data)
            print(s)
            # print(calculate_sma(candlestick_data))


            # Ставим маркер если цена больше 25800
            if round(int(candlestick_data.iloc[-1]['close'])) == round(int(s.iloc[-1]['sma'])) :
                chart.marker(text='SMA contact')


    ws_url = "wss://stream.binance.com:9443/ws/btcusdt@kline_1s"
    websocket.enableTrace(True)

    ws = websocket.WebSocketApp(ws_url, on_message=on_message)

    # Запускаем WebSocket-соединение
    ws.run_forever()
