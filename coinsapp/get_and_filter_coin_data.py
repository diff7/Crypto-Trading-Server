from __future__ import absolute_import, unicode_literals
import ccxt
from coinsapp.models import Coin, Value, Coinproperties
import requests
from datetime import datetime, timedelta
from coinsapp.models import Coin, Value, Coinproperties

def get_coinmarketcap():
    r = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=0')
    coinmarketcap_data=r.json()
    return(coinmarketcap_data)

def get_my_symbols():
    exchange = ccxt.binance  ({ 'verbose': True })
    exchange.load_markets()

    binance_symbols=exchange.symbols
    binance_symbols.remove('123/456')
    binance_symbols.remove('CHAT/BTC')
    binance_symbols.remove('CHAT/ETH')
    binance_symbols.remove('BCD/BTC')
    binance_symbols.remove('BCD/ETH')

    binance_symbols.remove('RCN/ETH')
    binance_symbols.remove('RCN/BTC')
    binance_symbols.remove('BAT/ETH')
    binance_symbols.remove('BAT/BTC')
    binance_symbols.remove('BAT/BNB')
    binance_symbols.remove('RCN/BNB')

    binance_symbols_clean=[]
    for ticker in binance_symbols:
         binance_symbols_clean.append(ticker.split('/')[0])

    coinmarketcap_data=get_coinmarketcap()
    coinmarkectcap_symbols=[]
    coinmarkectcap_symbols=[c['symbol'] for c in coinmarketcap_data]

    my_symbols=[]
    my_symbols=[s for s in binance_symbols_clean if s in coinmarkectcap_symbols]

    return(my_symbols)

def get_coin_ful_name():
    full_name=[]
    name=0
    my_symbols=get_my_symbols()
    coinmarketcap_data=get_coinmarketcap()
    for ticker in coinmarketcap_data:
        if ticker['symbol'] in my_symbols:
            name=(str(ticker['symbol'])+" "+str(ticker['name']))

            full_name.append(name)

    return(full_name)



def update_my_markers():
    all_names=get_coin_ful_name()
    my_symbols=get_my_symbols()
    for name in all_names:
        c=Coin.objects.update_or_create(coin_name=name)

    coins=Coin.objects.all().values('coin_name')
    coins_to_delete = [c['coin_name'] for c in coins if c['coin_name'] not in all_names]
    
    for ticker in coins_to_delete:
        coin=Coin.objects.filter(coin_name=ticker)
        coin.delete()



def get_my_coin_data():
    t=datetime.now()-timedelta(hours=2)
    all_names=get_coin_ful_name()
    coinmarketcap_data=get_coinmarketcap()
    my_symbols=get_my_symbols()

    for ticker in coinmarketcap_data:
        if ticker['symbol'] in my_symbols:

            price = ticker['price_usd']
            basevolume = ticker['market_cap_usd']


            if (price is not None) and (basevolume is not None):

                d=datetime.now()
                d=d.replace(tzinfo=None)
                for_values=Coin.objects.get(coin_name=str(ticker['symbol'])+" "+str(ticker['name']))


                v=for_values.value_set.create(coin_value=price, reqtime=datetime.now(),coin_basevolume=basevolume)
                v.save()


def make_coin_properties():
    t=datetime.now()-timedelta(hours=2)
    t_half=datetime.now()-timedelta(minutes=30)
    coin=Coin.objects.exclude(value__coin_value__isnull=True, value__coin_basevolume__isnull=True )

    for ticker in coin:

        volume=ticker.value_set.filter(reqtime__gt=t).order_by('reqtime')


        #VOLUME CHANGE 1 HOUR
        Firstvolume=volume.last().coin_basevolume
        Lastvolume=volume.first().coin_basevolume

        volumechange=(Lastvolume-Firstvolume)/Firstvolume*100

        #PRICE CHANGE 1 HOUR
        Firstprice=volume.last().coin_value
        Lastprice=volume.first().coin_value

        pricechange=(Lastprice-Firstprice)/Firstprice*100

        volume_half=ticker.value_set.filter(reqtime__gt=t_half).order_by('reqtime')

        #VOLUME CHANGE 30 MIN
        Last_volumehalf=volume_half[0].coin_basevolume
        First_volumehalf=volume_half.reverse()[0].coin_basevolume
        volume_changehalf=(Last_volumehalf-First_volumehalf)/First_volumehalf*100

        #PRICE CHANEG 30 MIN
        Last_pricehalf=volume_half[0].coin_value
        First_pricehalf=volume_half.reverse()[0].coin_value
        price_changehalf=(Last_pricehalf-First_pricehalf)/First_pricehalf*100

        p=ticker.coinproperties_set.update_or_create(coin_change=pricechange,volume_change=volumechange, coin_changehalf=price_changehalf,volume_changehalf=volume_changehalf)



def delete_old_values():
    t=datetime.now()-timedelta(hours=5)
    c=Value.objects.filter(reqtime__lt=t)
    c.delete()
